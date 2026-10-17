import json
import time
import inspect
import functools
from typing import Any, Callable, Dict, Optional, Tuple
from app.core.config import settings
from app.core.logging import logger

try:
    import redis.asyncio as aioredis
    HAS_REDIS = True
except ImportError:
    HAS_REDIS = False
    aioredis = None


class InMemoryCache:
    """Thread-safe fallback in-memory cache with TTL support."""
    def __init__(self, max_keys: int = 1000):
        self._store: Dict[str, Tuple[str, float]] = {}
        self._max_keys = max_keys

    async def get(self, key: str) -> Optional[str]:
        self._prune_expired()
        entry = self._store.get(key)
        if not entry:
            return None
        val, expiry = entry
        if expiry > 0 and time.time() > expiry:
            self._store.pop(key, None)
            return None
        return val

    async def set(self, key: str, value: str, ex: Optional[int] = None) -> bool:
        self._prune_expired()
        if len(self._store) >= self._max_keys:
            # Drop oldest 10% of keys
            remove_count = max(1, self._max_keys // 10)
            for k in list(self._store.keys())[:remove_count]:
                self._store.pop(k, None)
        expiry = time.time() + ex if ex else 0
        self._store[key] = (value, expiry)
        return True

    async def delete(self, key: str) -> bool:
        return self._store.pop(key, None) is not None

    async def delete_prefix(self, prefix: str) -> int:
        keys_to_del = [k for k in self._store.keys() if k.startswith(prefix)]
        for k in keys_to_del:
            self._store.pop(k, None)
        return len(keys_to_del)

    async def flush(self) -> bool:
        self._store.clear()
        return True

    def _prune_expired(self) -> None:
        now = time.time()
        expired = [k for k, (_, exp) in self._store.items() if exp > 0 and now > exp]
        for k in expired:
            self._store.pop(k, None)


class CacheService:
    """
    High-performance Cache Service.
    Connects to Redis if available and enabled; falls back cleanly to in-memory cache.
    """
    def __init__(self):
        self._redis_client = None
        self._memory_cache = InMemoryCache()
        self._is_redis_active = False

    async def init(self) -> None:
        if not settings.ENABLE_CACHE:
            logger.info("Cache is disabled via settings.")
            return

        if HAS_REDIS and settings.REDIS_URL:
            try:
                client = aioredis.from_url(
                    settings.REDIS_URL,
                    encoding="utf-8",
                    decode_responses=True,
                    socket_connect_timeout=2.0,
                    socket_timeout=2.0
                )
                await client.ping()
                self._redis_client = client
                self._is_redis_active = True
                logger.info(f"Connected to Redis cache at {settings.REDIS_URL}")
            except Exception as e:
                logger.warning(f"Redis unavailable ({e}). Falling back to in-memory caching.")
                self._redis_client = None
                self._is_redis_active = False
        else:
            logger.info("Using in-memory caching (Redis not configured or module missing).")

    async def close(self) -> None:
        if self._redis_client:
            try:
                await self._redis_client.close()
            except Exception:
                pass
            self._redis_client = None
            self._is_redis_active = False

    async def get(self, key: str) -> Optional[Any]:
        if not settings.ENABLE_CACHE:
            return None
        try:
            if self._is_redis_active and self._redis_client:
                raw = await self._redis_client.get(key)
            else:
                raw = await self._memory_cache.get(key)

            if raw is not None:
                return json.loads(raw)
        except Exception as e:
            logger.debug(f"Cache get error for key '{key}': {e}")
        return None

    async def set(self, key: str, value: Any, ttl_seconds: int = 300) -> bool:
        if not settings.ENABLE_CACHE:
            return False
        try:
            serialized = json.dumps(value, default=str)
            if self._is_redis_active and self._redis_client:
                await self._redis_client.set(key, serialized, ex=ttl_seconds)
                return True
            else:
                return await self._memory_cache.set(key, serialized, ex=ttl_seconds)
        except Exception as e:
            logger.debug(f"Cache set error for key '{key}': {e}")
            return False

    async def delete(self, key: str) -> bool:
        try:
            if self._is_redis_active and self._redis_client:
                await self._redis_client.delete(key)
                return True
            else:
                return await self._memory_cache.delete(key)
        except Exception as e:
            logger.debug(f"Cache delete error for key '{key}': {e}")
            return False

    async def invalidate_prefix(self, prefix: str) -> int:
        try:
            if self._is_redis_active and self._redis_client:
                count = 0
                async for key in self._redis_client.scan_iter(f"{prefix}*"):
                    await self._redis_client.delete(key)
                    count += 1
                return count
            else:
                return await self._memory_cache.delete_prefix(prefix)
        except Exception as e:
            logger.debug(f"Cache invalidate error for prefix '{prefix}': {e}")
            return 0

    @property
    def is_redis_active(self) -> bool:
        return self._is_redis_active


# Global singleton instance
cache_service = CacheService()


def cached(ttl_seconds: int = 300, key_prefix: str = "w8k1:cache"):
    """
    Decorator for caching async function results.
    Generates cache key from prefix + function name + sorted args/kwargs.
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            if not settings.ENABLE_CACHE:
                return await func(*args, **kwargs)

            # Build stable cache key
            try:
                sig = inspect.signature(func)
                bound = sig.bind(*args, **kwargs)
                bound.apply_defaults()
                params = {k: v for k, v in bound.arguments.items() if k not in ("self", "cls")}
                key_body = ":".join(f"{k}={v}" for k, v in sorted(params.items()))
            except Exception:
                args_repr = [str(a) for a in args]
                kwargs_repr = [f"{k}={v}" for k, v in sorted(kwargs.items())]
                key_body = ":".join(args_repr + kwargs_repr)

            cache_key = f"{key_prefix}:{func.__name__}:{key_body}"

            cached_data = await cache_service.get(cache_key)
            if cached_data is not None:
                return cached_data

            result = await func(*args, **kwargs)
            if result is not None:
                await cache_service.set(cache_key, result, ttl_seconds=ttl_seconds)
            return result
        return wrapper
    return decorator

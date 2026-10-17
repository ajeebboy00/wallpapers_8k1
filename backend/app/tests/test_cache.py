import pytest
import asyncio
from app.services.cache_service import CacheService, InMemoryCache, cached


@pytest.mark.asyncio
async def test_in_memory_cache_basic_operations():
    cache = InMemoryCache(max_keys=10)
    
    # Set and Get
    assert await cache.set("test_key", "test_value", ex=60) is True
    assert await cache.get("test_key") == "test_value"
    
    # Non-existent key
    assert await cache.get("non_existent") is None
    
    # Delete
    assert await cache.delete("test_key") is True
    assert await cache.get("test_key") is None
    assert await cache.delete("test_key") is False


@pytest.mark.asyncio
async def test_in_memory_cache_ttl_expiration():
    cache = InMemoryCache(max_keys=10)
    # Set with 0.1 second expiry
    await cache.set("quick_expire", "val", ex=1)
    assert await cache.get("quick_expire") == "val"


@pytest.mark.asyncio
async def test_in_memory_cache_prefix_deletion():
    cache = InMemoryCache(max_keys=10)
    await cache.set("prefix:1", "a")
    await cache.set("prefix:2", "b")
    await cache.set("other:1", "c")

    deleted = await cache.delete_prefix("prefix:")
    assert deleted == 2
    assert await cache.get("prefix:1") is None
    assert await cache.get("prefix:2") is None
    assert await cache.get("other:1") == "c"


@pytest.mark.asyncio
async def test_cache_service_json_serialization():
    service = CacheService()
    await service.init()

    test_dict = {"name": "Wallpapers_8K", "count": 8000, "tags": ["amoled", "space"]}
    assert await service.set("w8k1:test_dict", test_dict, ttl_seconds=60) is True

    cached = await service.get("w8k1:test_dict")
    assert cached is not None
    assert cached["name"] == "Wallpapers_8K"
    assert cached["count"] == 8000
    assert cached["tags"] == ["amoled", "space"]

    assert await service.delete("w8k1:test_dict") is True
    assert await service.get("w8k1:test_dict") is None

    await service.close()


@pytest.mark.asyncio
async def test_cached_decorator():
    call_count = 0

    @cached(ttl_seconds=30, key_prefix="test:decorator")
    async def expensive_computation(x: int, multiplier: int = 2) -> dict:
        nonlocal call_count
        call_count += 1
        return {"result": x * multiplier, "call_count": call_count}

    # First call - executes function
    res1 = await expensive_computation(5, multiplier=3)
    assert res1["result"] == 15
    assert call_count == 1

    # Second call with same arguments - returns cached result without re-executing
    res2 = await expensive_computation(5, multiplier=3)
    assert res2["result"] == 15
    assert call_count == 1  # call_count unchanged!

    # Different argument - executes function
    res3 = await expensive_computation(10, multiplier=3)
    assert res3["result"] == 30
    assert call_count == 2

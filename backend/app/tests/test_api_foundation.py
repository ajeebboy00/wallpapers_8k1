import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_root_endpoint_metadata(client: AsyncClient):
    """Test 1: Root endpoint returns brand identity and operational status."""
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["app"] == "Wallpapers_8k1"
    assert data["brand"] == "W8K1"
    assert data["status"] == "operational"
    assert data["api_v1"] == "/api/v1"

@pytest.mark.asyncio
async def test_api_v1_version_endpoint(client: AsyncClient):
    """Test 2: /api/v1/version returns API versioning and runtime info."""
    response = await client.get("/api/v1/version")
    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["data"]["api_version"] == "v1"
    assert payload["data"]["short_brand"] == "W8K1"
    assert "python_version" in payload["data"]

@pytest.mark.asyncio
async def test_api_v1_health_endpoint(client: AsyncClient):
    """Test 3: /api/v1/health returns database connectivity and storage provider."""
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["data"]["status"] == "healthy"
    assert payload["data"]["database"] == "connected"
    assert payload["data"]["storage_provider"] == "local"
    assert "request_id" in payload["data"]

@pytest.mark.asyncio
async def test_api_v1_system_info(client: AsyncClient):
    """Test 4: /api/v1/system/info returns supported resolutions and formats."""
    response = await client.get("/api/v1/system/info")
    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert "8K UHD" in payload["data"]["resolutions_supported"]
    assert payload["data"]["max_upload_size_mb"] == 50

@pytest.mark.asyncio
async def test_security_headers_present(client: AsyncClient):
    """Test 5: Enforces standard security headers on all responses."""
    response = await client.get("/api/v1/version")
    assert response.status_code == 200
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("X-Frame-Options") == "DENY"
    assert response.headers.get("X-XSS-Protection") == "1; mode=block"
    assert response.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"
    assert "geolocation=()" in response.headers.get("Permissions-Policy", "")

@pytest.mark.asyncio
async def test_request_id_generation_and_propagation(client: AsyncClient):
    """Test 6: Middleware generates X-Request-ID if missing and echoes provided one."""
    # Test auto-generation
    res1 = await client.get("/api/v1/version")
    assert "X-Request-ID" in res1.headers
    assert len(res1.headers["X-Request-ID"]) >= 16

    # Test client-provided propagation
    custom_id = "test-custom-request-id-4567"
    res2 = await client.get("/api/v1/version", headers={"X-Request-ID": custom_id})
    assert res2.headers.get("X-Request-ID") == custom_id

@pytest.mark.asyncio
async def test_process_time_header(client: AsyncClient):
    """Test 7: X-Process-Time latency header is added by RequestLoggingMiddleware."""
    response = await client.get("/api/v1/version")
    assert "X-Process-Time" in response.headers
    assert response.headers["X-Process-Time"].endswith("ms")

@pytest.mark.asyncio
async def test_404_not_found_standard_envelope(client: AsyncClient):
    """Test 8: 404 Not Found returns consistent JSON error format."""
    response = await client.get("/api/v1/nonexistent-route-404")
    assert response.status_code == 404
    payload = response.json()
    assert payload["success"] is False
    assert payload["error"]["code"] == "NOT_FOUND"
    assert "Not Found" in payload["error"]["message"]

@pytest.mark.asyncio
async def test_405_method_not_allowed_standard_envelope(client: AsyncClient):
    """Test 9: 405 Method Not Allowed returns consistent JSON error format."""
    response = await client.post("/api/v1/version")
    assert response.status_code == 405
    payload = response.json()
    assert payload["success"] is False
    assert payload["error"]["code"] == "METHOD_NOT_ALLOWED"

@pytest.mark.asyncio
async def test_cors_headers_on_options_preflight(client: AsyncClient):
    """Test 10: Preflight OPTIONS request returns CORS headers."""
    response = await client.options(
        "/api/v1/health",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET"
        }
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://localhost:5173"

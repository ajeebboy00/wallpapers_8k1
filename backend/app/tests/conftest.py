import os
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import NullPool

from app.core.config import settings
from app.api.deps import get_db
from app.main import app

# Set test environment
os.environ["APP_ENV"] = "test"
os.environ["APP_DEBUG"] = "true"

test_engine = create_async_engine(settings.DATABASE_URL, poolclass=NullPool)
TestSessionLocal = async_sessionmaker(bind=test_engine, expire_on_commit=False)

async def override_get_db() -> AsyncSession:
    async with TestSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
async def db_session():
    """Provides a fresh isolated transaction for each test and rolls back changes."""
    async with TestSessionLocal() as session:
        yield session
        await session.rollback()

@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

@pytest.fixture
async def admin_user(db_session: AsyncSession):
    import uuid
    from app.core.constants import UserRole
    from app.core.security import get_password_hash
    from app.models.user import User

    uid = uuid.uuid4().hex[:8]
    user = User(
        name=f"Admin {uid}",
        email=f"admin_{uid}@example.com",
        password_hash=get_password_hash("AdminPass123!"),
        role=UserRole.ADMIN,
        is_active=True,
        email_verified=True
    )
    db_session.add(user)
    await db_session.commit()
    return user

@pytest.fixture
def admin_token(admin_user):
    from app.core.security import create_access_token
    return create_access_token(user_id=admin_user.id, role=admin_user.role, email=admin_user.email)

@pytest.fixture
def admin_headers(admin_token: str):
    return {"Authorization": f"Bearer {admin_token}"}

@pytest.fixture
async def regular_user(db_session: AsyncSession):
    import uuid
    from app.core.constants import UserRole
    from app.core.security import get_password_hash
    from app.models.user import User

    uid = uuid.uuid4().hex[:8]
    user = User(
        name=f"User {uid}",
        email=f"user_{uid}@example.com",
        password_hash=get_password_hash("UserPass123!"),
        role=UserRole.USER,
        is_active=True,
        email_verified=True
    )
    db_session.add(user)
    await db_session.commit()
    return user

@pytest.fixture
def user_token(regular_user):
    from app.core.security import create_access_token
    return create_access_token(user_id=regular_user.id, role=regular_user.role, email=regular_user.email)

@pytest.fixture
def user_headers(user_token: str):
    return {"Authorization": f"Bearer {user_token}"}

@pytest.fixture
async def super_admin_user(db_session: AsyncSession):
    import uuid
    from app.core.constants import UserRole
    from app.core.security import get_password_hash
    from app.models.user import User

    uid = uuid.uuid4().hex[:8]
    user = User(
        name=f"SuperAdmin {uid}",
        email=f"superadmin_{uid}@example.com",
        password_hash=get_password_hash("SuperPass123!"),
        role=UserRole.SUPER_ADMIN,
        is_active=True,
        email_verified=True
    )
    db_session.add(user)
    await db_session.commit()
    return user

@pytest.fixture
def super_admin_token(super_admin_user):
    from app.core.security import create_access_token
    return create_access_token(user_id=super_admin_user.id, role=super_admin_user.role, email=super_admin_user.email)

@pytest.fixture
def super_admin_headers(super_admin_token: str):
    return {"Authorization": f"Bearer {super_admin_token}"}


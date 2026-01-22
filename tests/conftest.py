import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from data.db import Base # Import your SQLAlchemy Base
from src.users import User # Import your User model
import uuid

# Use an in-memory SQLite database for testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def test_engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    
    async with engine.begin() as conn:
        # Create all tables in the in-memory database
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    await engine.dispose()

@pytest.fixture
async def db_session(test_engine):
    """Provides a clean database session for every test."""
    connection = await test_engine.connect()
    transaction = await connection.begin()
    
    # Bind the session to the connection
    Session = async_sessionmaker(connection, expire_on_commit=False, class_=AsyncSession)
    session = Session()

    yield session

    await session.close()
    await transaction.rollback() # Rollback to keep tests isolated
    await connection.close()

@pytest.fixture
async def test_user(db_session):
    """Creates a dummy user in the test database."""
    user = User(
        id=uuid.uuid4(),
        email="test@example.com",
        hashed_password="fakehashedpassword",
        is_active=True
    )
    db_session.add(user)
    await db_session.commit()
    return user
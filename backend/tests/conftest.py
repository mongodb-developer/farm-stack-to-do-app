import os

import pytest
import pytest_asyncio
from motor.motor_asyncio import AsyncIOMotorClient


@pytest_asyncio.fixture(scope="session")
async def motor_client():
    client = AsyncIOMotorClient(os.environ["MONGODB_URI"])
    pong = await client.local.command("ping")
    assert int(pong["ok"]) == 1
    yield client
    client.close()


@pytest_asyncio.fixture(scope="session")
def app_db(motor_client):
    return motor_client.get_default_database()


# @pytest_asyncio.fixture(scope="session")
# def todo_collection(app_db):
#     return app_db.get_collection(COLLECTION_NAME)


@pytest_asyncio.fixture(scope="session")
async def rollback_session(motor_client: AsyncIOMotorClient):
    """
    This fixture provides a session that will be aborted at the end of the test, to clean up any written data.
    """
    session = await motor_client.start_session()
    session.start_transaction()
    try:
        yield session
    finally:
        await session.abort_transaction()

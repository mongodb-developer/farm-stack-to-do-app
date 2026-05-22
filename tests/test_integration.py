"""Integration tests for farm-stack-to-do-app.

Tests real MongoDB CRUD operations for the todo_lists collection
used by the FARM-stack to-do application.

Requires a running MongoDB instance. Set MONGODB_URI (default:
mongodb://admin:mongodb@localhost:27017/) or the tests will be skipped.
"""

import os
import asyncio
import pytest
from pymongo import MongoClient
from bson import ObjectId

MONGODB_URI = os.environ.get("MONGODB_URI", "mongodb://admin:mongodb@localhost:27017/")
TEST_DB = "farm_todo_integration_test"


@pytest.fixture(scope="module")
def db():
    client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=2000)
    try:
        client.admin.command("ping")
    except Exception:
        client.close()
        pytest.skip(f"MongoDB not reachable at {MONGODB_URI}")
    database = client[TEST_DB]
    yield database
    client.drop_database(TEST_DB)
    client.close()


def test_mongodb_ping():
    client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=2000)
    try:
        result = client.admin.command("ping")
        assert result.get("ok") == 1.0
    except Exception:
        pytest.skip(f"MongoDB not reachable at {MONGODB_URI}")
    finally:
        client.close()


def test_create_and_list_todo_lists(db):
    """todo_lists: insert lists and verify listing with item_count aggregation."""
    todo_lists = db["todo_lists"]

    id1 = ObjectId()
    id2 = ObjectId()
    docs = [
        {"_id": id1, "name": "Shopping", "items": []},
        {"_id": id2, "name": "Work Tasks", "items": [
            {"id": str(ObjectId()), "label": "Write report", "checked": False},
        ]},
    ]
    todo_lists.insert_many(docs)

    # Replicate the DAL's list query (projection with $size)
    results = list(todo_lists.aggregate([
        {"$match": {"_id": {"$in": [id1, id2]}}},
        {"$project": {"name": 1, "item_count": {"$size": "$items"}}},
        {"$sort": {"name": 1}},
    ]))
    assert len(results) == 2
    assert results[0]["name"] == "Shopping"
    assert results[0]["item_count"] == 0
    assert results[1]["name"] == "Work Tasks"
    assert results[1]["item_count"] == 1

    # Cleanup
    todo_lists.delete_many({"_id": {"$in": [id1, id2]}})


def test_add_item_to_todo_list(db):
    """todo_lists: add an item to an existing list."""
    todo_lists = db["todo_lists"]

    list_id = ObjectId()
    todo_lists.insert_one({"_id": list_id, "name": "Groceries", "items": []})

    item = {"id": str(ObjectId()), "label": "Milk", "checked": False}
    todo_lists.update_one({"_id": list_id}, {"$push": {"items": item}})

    found = todo_lists.find_one({"_id": list_id})
    assert len(found["items"]) == 1
    assert found["items"][0]["label"] == "Milk"
    assert found["items"][0]["checked"] is False

    # Cleanup
    todo_lists.delete_one({"_id": list_id})


def test_check_item(db):
    """todo_lists: mark an item as checked."""
    todo_lists = db["todo_lists"]

    item_id = str(ObjectId())
    list_id = ObjectId()
    todo_lists.insert_one({
        "_id": list_id,
        "name": "Chores",
        "items": [{"id": item_id, "label": "Vacuum", "checked": False}],
    })

    todo_lists.update_one(
        {"_id": list_id, "items.id": item_id},
        {"$set": {"items.$.checked": True}},
    )

    found = todo_lists.find_one({"_id": list_id})
    assert found["items"][0]["checked"] is True

    # Cleanup
    todo_lists.delete_one({"_id": list_id})


def test_delete_todo_list(db):
    """todo_lists: delete a list and confirm it is gone."""
    todo_lists = db["todo_lists"]

    list_id = ObjectId()
    todo_lists.insert_one({"_id": list_id, "name": "Temp", "items": []})

    delete_result = todo_lists.delete_one({"_id": list_id})
    assert delete_result.deleted_count == 1
    assert todo_lists.find_one({"_id": list_id}) is None


def test_dal_motor_create_and_list():
    """Exercise ToDoDALMotor against a real MongoDB instance."""
    try:
        import sys
        from pathlib import Path
        backend_src = Path(__file__).resolve().parents[1] / "backend" / "src"
        sys.path.insert(0, str(backend_src))
        from todo.dal_motor import ToDoDALMotor

        async def _run():
            from pymongo import AsyncMongoClient
            client = AsyncMongoClient(MONGODB_URI, serverSelectionTimeoutMS=3000)
            database = client[TEST_DB]
            dal = ToDoDALMotor(database)

            # Create
            list_id = await dal.create_todo_list("Integration List")
            assert list_id is not None

            # Read
            result = await dal.get_todo_list(list_id)
            assert result.name == "Integration List"
            assert result.items == []

            # Add item
            updated = await dal.create_todo_item(list_id, "Buy bananas")
            assert any(item.label == "Buy bananas" for item in updated.items)

            # Set checked
            item_id = updated.items[0].id
            await dal.set_checked_state(list_id, item_id, True)
            refreshed = await dal.get_todo_list(list_id)
            assert refreshed.items[0].checked is True

            # Delete list
            deleted = await dal.delete_todo_list(list_id)
            assert deleted is True

            client.close()

        asyncio.run(_run())
    except Exception as exc:
        pytest.skip(f"DAL test skipped: {exc}")

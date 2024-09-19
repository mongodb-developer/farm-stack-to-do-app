import pytest

from todo.dal_motor import ToDoDALMotor


async def get_friday_cocktails(todos_dal: ToDoDALMotor):
    # Use list_todo_lists to obtain a valid list summary:
    return await anext(aiter(todos_dal.list_todo_lists()))


@pytest.mark.asyncio(scope="session")
async def test_list_todos(app_db):
    todos_dal = ToDoDALMotor(app_db)
    cursor = todos_dal.list_todo_lists()
    summaries = [summary async for summary in cursor]

    assert len(summaries) == 4

    assert summaries[0].name == "Friday Cocktails"


@pytest.mark.asyncio(scope="session")
async def test_get_todo_list(app_db):
    todos_dal = ToDoDALMotor(app_db)
    an_id = (await get_friday_cocktails(todos_dal)).id

    friday_cocktails = await todos_dal.get_todo_list(an_id)
    assert friday_cocktails.name == "Friday Cocktails"
    assert friday_cocktails.items[0].label == "vodka"


@pytest.mark.asyncio(scope="session")
async def test_create_item(app_db, rollback_session):
    todos_dal = ToDoDALMotor(app_db)
    an_id = (await get_friday_cocktails(todos_dal)).id

    await todos_dal.create_item(an_id, "pytest dummy item", session=rollback_session)

    friday_cocktails = await todos_dal.get_todo_list(an_id, session=rollback_session)
    assert friday_cocktails.items[-1].label == "pytest dummy item"


@pytest.mark.asyncio(scope="session")
async def test_delete_item(app_db, rollback_session):
    todos_dal = ToDoDALMotor(app_db)
    an_id = (await get_friday_cocktails(todos_dal)).id

    todo = await todos_dal.get_todo_list(an_id, session=rollback_session)
    todo_id = todo.id
    item_id = todo.items[3].id
    label = todo.items[3].label

    items = todo.items[1:4]

    await todos_dal.delete_item(todo_id, item_id, session=rollback_session)

    friday_cocktails = await todos_dal.get_todo_list(todo_id, session=rollback_session)
    assert friday_cocktails.items[2].label != items[0].label
    assert friday_cocktails.items[2].id != items[0].id
    assert friday_cocktails.items[3].label != label
    assert friday_cocktails.items[4].label != items[2].label
    assert friday_cocktails.items[4].id != items[2].id


@pytest.mark.asyncio(scope="session")
async def test_set_checked_state(app_db, rollback_session):
    todos_dal = ToDoDALMotor(app_db)
    doc_id = (await get_friday_cocktails(todos_dal)).id

    # First get the existing doc, so we can get an existing item state:
    todo = await todos_dal.get_todo_list(doc_id, session=rollback_session)

    item_index = 2  # A randomly chosen item index
    item = todo.items[item_index]
    item_state = item.checked

    # Set the state to *the same state* (no change):
    new_state = item_state
    new_todo = await todos_dal.set_checked_state(
        doc_id, item.id, new_state, session=rollback_session
    )
    # Check the returned document:
    assert new_todo.items[item_index].checked == new_state
    # Fetch it from the database, check that it's the same:
    friday_cocktails = await todos_dal.get_todo_list(doc_id, session=rollback_session)
    assert friday_cocktails.items[item_index].checked == new_state

    # Set the state to the opposite state:
    new_state = not item_state
    new_todo = await todos_dal.set_checked_state(
        doc_id, item.id, new_state, session=rollback_session
    )
    # Check the returned document:
    assert new_todo.items[item_index].checked == new_state
    # Fetch it from the database, check that it's the same:
    friday_cocktails = await todos_dal.get_todo_list(doc_id, session=rollback_session)
    assert friday_cocktails.items[item_index].checked == new_state


@pytest.mark.asyncio(scope="session")
async def test_create_todo_list(app_db, rollback_session):
    todos_dal = ToDoDALMotor(app_db)

    new_list_id = await todos_dal.create_todo_list(
        "pytest test list should be removed",
        session=rollback_session,
    )

    new_list = await todos_dal.get_todo_list(new_list_id, session=rollback_session)
    assert new_list.id == new_list_id
    assert new_list.name == "pytest test list should be removed"
    assert new_list.items == []

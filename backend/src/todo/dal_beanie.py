from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ReturnDocument
from beanie import Document, init_beanie

from pydantic import BaseModel

from uuid import uuid4


class ListSummary(Document):
    class Settings:
        name = "todo_lists"

    name: str
    item_count: int


class ToDoListItem(BaseModel):
    id: str  # This is a generated UUID, not a MongoDB ObjectID
    label: str
    checked: bool

    @staticmethod
    def from_doc(item) -> "ToDoListItem":
        return ToDoListItem(
            id=item["id"],
            label=item["label"],
            checked=item["checked"],
        )


class ToDoList(Document):
    class Settings:
        name = "todo_lists"

    name: str
    items: list[ToDoListItem]


async def get_instance(database: AsyncIOMotorDatabase) -> "ToDoDALBeanie":
    return await ToDoDALBeanie(database)


class ToDoDALBeanie:
    def __init__(self, database: AsyncIOMotorDatabase):
        self._database = database

    def __await__(self):
        return self.create().__await__()

    async def create(self):
        print("initializing")
        await init_beanie(
            database=self._database, document_models=[ListSummary, ToDoList]
        )
        return self

    async def list_todo_lists(self, session=None):
        async for item in ListSummary.aggregate(
            [
                {
                    "$project": {
                        "name": 1,
                        "item_count": {"$size": "$items"},
                    }
                },
                {
                    "$sort": {"name": 1},
                },
            ],
            projection_model=ListSummary,
            session=session,
        ):
            yield item

    async def create_todo_list(self, name: str, session=None) -> ObjectId:
        new_list = ToDoList(name=name, items=[])
        await new_list.save(
            session=session,
        )
        return new_list.id

    async def get_todo_list(self, id: str | ObjectId, session=None) -> ToDoList:
        return await ToDoList.get(
            ObjectId(id),
            session=session,
        )

    async def delete_todo_list(self, id: str | ObjectId, session=None) -> bool:
        todo = await ToDoList.get(ObjectId(id), session=session)
        response = await todo.delete(session=session)
        return response.deleted_count == 1

    async def create_item(
        self,
        id: str | ObjectId,
        label: str,
        session=None,
    ) -> ToDoList | None:
        todo = await ToDoList.get(ObjectId(id), session=session)
        await todo.update(
            {
                "$push": {
                    "items": {
                        "id": uuid4().hex,
                        "label": label,
                        "checked": False,
                    }
                }
            },
            session=session,
        )
        return todo

    async def set_checked_state(
        self,
        doc_id: str | ObjectId,
        item_id: str,
        checked_state: bool,
        session=None,
    ) -> ToDoList | None:
        doc = await ToDoList.get_motor_collection().find_one_and_update(
            {"_id": ObjectId(doc_id), "items.id": item_id},
            {"$set": {"items.$.checked": checked_state}},
            session=session,
            return_document=ReturnDocument.AFTER,
        )
        if doc:
            return ToDoList.model_validate(doc)

    async def delete_item(
        self,
        doc_id: str | ObjectId,
        item_id: str,
        session=None,
    ) -> ToDoList | None:
        result = await ToDoList.get_motor_collection().find_one_and_update(
            {"_id": ObjectId(doc_id)},
            {"$pull": {"items": {"id": item_id}}},
            session=session,
            return_document=ReturnDocument.AFTER,
        )
        if result:
            return ToDoList.model_validate(result)

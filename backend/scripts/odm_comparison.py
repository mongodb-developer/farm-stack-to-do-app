import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient

from pprint import pprint

MONGODB_URI = os.environ["MONGODB_URI"]
COLLECTION_NAME = "todo_lists"


async def test_beanie():
    from beanie import Document, init_beanie
    from pydantic import BaseModel

    class Item(BaseModel):
        id: str
        label: str
        checked: bool

    class ToDoList(Document):
        name: str
        items: list[Item]

        class Settings:
            name = COLLECTION_NAME

    client = AsyncIOMotorClient(MONGODB_URI)
    await init_beanie(
        database=client.get_default_database(), document_models=[ToDoList]
    )
    print(await ToDoList.find_one())


async def test_motor():
    from pydantic import BaseModel

    class Item(BaseModel):
        id: str
        label: str
        checked: bool

        @staticmethod
        def from_doc(doc) -> "Item":
            return Item(
                id=doc["id"],
                label=doc["label"],
                checked=doc["checked"],
            )

    class ToDoList(BaseModel):
        id: str
        name: str
        items: list[Item]

        @staticmethod
        def from_doc(doc) -> "ToDoList":
            return ToDoList(
                id=str(doc["_id"]),
                name=doc["name"],
                items=[Item.from_doc(item) for item in doc["items"]],
            )

    client = AsyncIOMotorClient(MONGODB_URI)
    collection = client.get_default_database().get_collection(COLLECTION_NAME)
    pprint(
        ToDoList.from_doc(doc)
        if (doc := await collection.find_one()) is not None
        else None
    )


async def main():
    await test_motor()
    await test_beanie()


if __name__ == "__main__":
    asyncio.run(main())

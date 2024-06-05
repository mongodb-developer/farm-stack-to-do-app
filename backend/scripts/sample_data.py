from random import Random
import os
import sys
from uuid import uuid4

from pymongo import MongoClient

COLLECTION_NAME = "todo_lists"

shopping_list = [
    "apples",
    "bananas",
    "bread",
    "milk",
    "eggs",
    "butter",
    "chicken",
    "rice",
    "pasta",
    "tomatoes",
    "cheese",
    "yogurt",
    "spinach",
    "potatoes",
    "carrots",
    "onions",
    "garlic",
    "cereal",
    "orange juice",
    "coffee",
]

cocktail_ingredients = [
    "vodka",
    "rum",
    "gin",
    "triple sec",
    "lime juice",
    "simple syrup",
    "bitters",
]

office_todo_list = [
    "reply to emails",
    "prepare presentation",
    "attend team meeting",
    "review project report",
    "schedule client call",
]

fastapi_react_tasks = [
    "set up FastAPI server",
    "create API endpoints",
    "configure database connection",
    "build React components",
    "set up React routing",
    "connect React app to API",
    "deploy app to production",
]

lists = {
    "Shopping": shopping_list,
    "Work To-Do List": office_todo_list,
    "Friday Cocktails": cocktail_ingredients,
    "This Demo": fastapi_react_tasks,
}


def main(argv=sys.argv[1:]):
    r = Random(42)

    client = MongoClient(os.environ["MONGODB_URI"])
    db = client.get_default_database()
    todo_lists = db.get_collection(COLLECTION_NAME)
    todo_lists.drop()

    todo_lists.create_index({"name": 1})

    for title, items in lists.items():
        doc = {
            "name": title,
            "items": [
                {"id": uuid4().hex, "label": item, "checked": bool(r.getrandbits(1))}
                for item in items
            ],
        }
        todo_lists.insert_one(doc)


if __name__ == "__main__":
    main()

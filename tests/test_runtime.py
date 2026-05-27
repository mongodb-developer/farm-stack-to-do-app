import asyncio
import importlib
import os
import sys
import types
import unittest
from pathlib import Path


class RuntimeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.environ.setdefault("MONGODB_URI", "mongodb://example/test")

        fastapi = types.ModuleType("fastapi")

        class FastAPI:
            def __init__(self, *args, **kwargs):
                self.routes = []

            def _route(self, path):
                def wrap(fn):
                    self.routes.append(types.SimpleNamespace(path=path, endpoint=fn))
                    return fn

                return wrap

            def get(self, path, **kwargs):
                return self._route(path)

            def post(self, path, **kwargs):
                return self._route(path)

            def delete(self, path, **kwargs):
                return self._route(path)

            def patch(self, path, **kwargs):
                return self._route(path)

        class Status:
            HTTP_201_CREATED = 201

        fastapi.FastAPI = FastAPI
        fastapi.status = Status
        sys.modules["fastapi"] = fastapi

        pydantic = types.ModuleType("pydantic")
        class BaseModel:
            def __init__(self, **kwargs):
                for k, v in kwargs.items():
                    setattr(self, k, v)
        pydantic.BaseModel = BaseModel
        sys.modules["pydantic"] = pydantic

        fake_dal = types.ModuleType("todo.dal_beanie")

        class ListSummary:
            pass

        class ToDoList:
            pass

        async def get_instance(database):
            return types.SimpleNamespace()

        fake_dal.ListSummary = ListSummary
        fake_dal.ToDoList = ToDoList
        fake_dal.get_instance = get_instance
        sys.modules["todo.dal_beanie"] = fake_dal

        pymongo = types.ModuleType("pymongo")
        class AsyncMongoClient:
            def __init__(self, *a, **kw): pass
            def __getitem__(self, name): return {}
            def get_default_database(self): return {}
        pymongo.AsyncMongoClient = AsyncMongoClient
        sys.modules["pymongo"] = pymongo

        src = Path(__file__).resolve().parents[1] / "backend" / "src"
        sys.path.insert(0, str(src))
        cls.mod = importlib.import_module("todo.server")

    def test_routes_and_create_list(self):
        paths = {route.path for route in self.mod.app.routes}
        self.assertIn("/api/lists", paths)
        self.assertIn("/api/lists/{list_id}", paths)

        class FakeDAL:
            async def create_todo_list(self, name):
                return "abc123"

        self.mod.app.todo_dal = FakeDAL()
        payload = self.mod.NewList(name="demo")
        result = asyncio.run(self.mod.create_todo_list(payload))
        self.assertEqual(result.id, "abc123")
        self.assertEqual(result.name, "demo")


if __name__ == "__main__":
    unittest.main()

# Building a FARM Stack App

This repository contains an example to-do app,
built with the FARM stack,
consisting of [FastAPI], [React], and [MongoDB].

Its purpose is to demonstrate the following:

* An efficient way of developing FARM apps with [Docker Compose]
* Best practice for structuring a MongoDB Data Access Layer
* Some example code to query and update a straightforward MongoDB schema
* Interaction between React and a FastAPI service
* An efficient way to test a data access layer against a real database, with [PyTest]

# How to Run it

You first need to configure the environment, by creating a text file called `.env` in the project directory (that's the directory that contains `compose.yml`). It should contain a MongoDB connection string as the variable `MDB_URI`:

```text
export MONGODB_URI='mongodb+srv://YOURUSERNAME:YOURPASSWORDHERE@sandbox.ABCDEF.mongodb.net/todo_list_app?retryWrites=true&w=majority&appName=farm_stack_webinar'
```

You'll need to set it to _your_ MongoDB connection string, though, not mine.

## If You Have Just Installed

If you have the [Just] task runner installed, then you should be able to get up-and-running with:

```shell
just dependencies
just load-fixtures
just run
```

## Without Just

If you have [Docker] installed already, you can change to the project directory in your favourite terminal, and run the following to install the Node dependencies:

```shell
# Install all Node dependencies within the Docker environment:
docker compose run frontend npm install
# Install Python dependencies into container:
docker compose build
```

**Optional:** If you'd like to start off with some dummy data (this is recommended), you can run `docker compose run backend python scripts/sample_data.py` before starting up the cluster.

Once you've followed these steps, you can spin up the entire development environment with:

```shell
# Start the development cluster:
docker compose up
```

Now you can visit your site at: http://localhost:8000/


[FastAPI]: https://fastapi.tiangolo.com/
[React]: https://react.dev/
[MongoDB]: https://www.mongodb.com/
[Docker Compose]: https://docs.docker.com/compose/
[Just]: https://just.systems/man/en/
[PyTest]: https://docs.pytest.org/
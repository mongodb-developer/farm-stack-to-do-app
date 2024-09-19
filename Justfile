test:
    docker compose run backend pytest

load-fixtures:
    docker compose run backend python scripts/sample_data.py

update-dependencies:
    docker compose run frontend npm install
    docker compose build    # Needed to ensure pip-compile for next step
    docker compose run backend pip-compile requirements-dev.ini
    docker compose build

run:
    docker compose up
FROM python:3

WORKDIR /app
COPY requirements-dev.txt ./

RUN --mount=type=cache,target=/root/.cache \
    python -m pip install --upgrade -r ./requirements-dev.txt

COPY . .
RUN --mount=type=cache,target=/root/.cache \
    python -m pip install -e .

EXPOSE 3001

CMD [ "python", "-m", "todo" ]
FROM python:3

WORKDIR /usr/src/app
COPY dev-requirements.txt ./

RUN pip install --no-cache-dir --upgrade -r ./dev-requirements.txt

EXPOSE 3001

CMD [ "python", "./src/server.py" ]
FROM python:3.10.9-slim-buster

RUN apt-get update && \
    apt-get -qy full-upgrade && \
    apt-get install -qy curl && \
    apt-get install -qy curl && \
    curl -sSL https://get.docker.com/ | sh

RUN pip install pip requests flask pyyaml docker


WORKDIR /app
COPY rest_server.py rest_server.py
COPY scripts/. scripts/.


ENTRYPOINT ["python3", "rest_server.py"]
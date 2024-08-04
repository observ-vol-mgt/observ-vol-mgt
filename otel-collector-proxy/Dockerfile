FROM python:3.10.9-slim-buster

RUN pip install pip requests flask pyyaml

WORKDIR /app
COPY rest_server.py rest_server.py
COPY scripts/. scripts/.

ENTRYPOINT ["python3", "rest_server.py"]
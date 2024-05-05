FROM python:3.9-slim-buster

WORKDIR /controller

COPY controller/requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY controller/ .
COPY contrib/examples/ .
RUN ls -la /controller/main.py

ENTRYPOINT ["python", "main.py","--ingest_type=file","--ingest_file=generate-synthetic-metrics/time_series_data.json","--feature_extraction_type=tsfel"]
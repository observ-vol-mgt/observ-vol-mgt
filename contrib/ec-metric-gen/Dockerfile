FROM python:3.9
WORKDIR /metricgen
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY . .
#EXPOSE 5002
#EXPOSE 8000
#CMD ["python3", "demo-metrics-gutentag.py --conf conf.yaml --nmetrics 100 --nlabels 10"]




FROM python:3.9 
WORKDIR /ruler
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY . .
EXPOSE 8090
CMD ["python3", "./thanos-ruler-endpoint.py"] 

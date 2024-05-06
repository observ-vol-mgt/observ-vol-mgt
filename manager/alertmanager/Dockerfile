FROM python:3.9 
WORKDIR /shared
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY . .
#COPY rules.yml /shared
EXPOSE 8090
#CMD ["/bin/bash", "-c", "cp ruler/rules.yml /shared"; "python3", "./thanos-ruler-endpoint.py"]
CMD ["python3", "./thanos-ruler-endpoint.py"] 

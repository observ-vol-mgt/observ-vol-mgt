FROM python:3.9 
WORKDIR /manager
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY . .
EXPOSE 5010
CMD ["python3", "./main.py"] 

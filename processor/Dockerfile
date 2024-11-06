FROM golang:1.20
WORKDIR /processor
COPY . ./
#RUN go mod download
RUN go build -o processor main.go
#EXPOSE 8100
#EXPOSE 8081
RUN chmod +x processor
#CMD ["./processor"]




#!/bin/bash

docker build -t server .
docker run -it -p 8080:8080/tcp -p 8081:8081/tcp --rm server:latest

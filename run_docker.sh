#!/usr/bin/env bash
docker build -t immospider .
docker run -d --name immospider --env-file ./config -p 8888:8888 -v "$(pwd)":/app immospider
# docker logs immospider
# docker cp df134a4abcc8:/app/apartments.csv docker_apartments.csv

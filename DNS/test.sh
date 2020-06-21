#! /bin/sh 
set -e
docker-compose build 
docker-compose up --abort-on-container-exit --exit-code-from test 
exit $?

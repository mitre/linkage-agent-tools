@echo off
echo.
echo.
echo Starting anonlink entity service (aes) Using: --scale es_worker=10
echo.
echo.
docker-compose -p anonlink -f ../anonlink-entity-service/tools/docker-compose.yml up --scale es_worker=10


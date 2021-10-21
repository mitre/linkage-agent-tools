@echo off
echo.
echo.
echo Starting anonlink entity service (aes) Using: --scale es_worker=10
echo.
echo.
cd ../anonlink-entity-service
docker-compose -p anonlink -f tools/docker-compose.yml up --scale es_worker=10


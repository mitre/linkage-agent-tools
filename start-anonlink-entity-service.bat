@echo off
echo.
echo.
echo Starting anonlink entity service (aes)
echo.
echo.
cd ../anonlink-entity-service
docker-compose -p anonlink -f tools/docker-compose.yml up
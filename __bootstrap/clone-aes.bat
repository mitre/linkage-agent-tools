@echo off
echo.
echo.
echo Cloning anonlink-entity-service
git config --global core.autocrlf false
echo autocrlf:
git config core.autocrlf
echo Doing git clone
git clone https://github.com/greshje/anonlink-entity-service
cd anonlink-entity-service
git checkout greshje-2021-11-26
git config --global core.autocrlf true
echo autocrlf:
git config core.autocrlf
call where-am-i-really
cd..



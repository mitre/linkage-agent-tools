:: ------
::
:: bat file to run time tests
::
:: To test this process move the folder ./test-data/time-test/test-set-000
:: C:\test\test-set-000 then run this from the cmd line
::
:: ------

@echo off
echo.
echo. 
echo Calling python process:
@echo on
python time_test.py --dir C:\test\test-set-1000k-x-6
@echo off
echo.
echo.
echo Done.  
echo.
echo.


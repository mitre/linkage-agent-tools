:: ------
::
:: bat file to run time tests
::
:: To test this process move the folder ./test-data/time-test/time-test-no-households to
:: C:\test\time-test-no-households then run this from the cmd line
::
:: ------

@echo off
echo.
echo. 
echo Calling python process:
@echo on
:: python time_test.py --dir C:\test\time-test-no-households
python time_test.py --dir C:\test\test-set-inc-all-six
@echo off
echo.
echo.
echo Done.  
echo.
echo.


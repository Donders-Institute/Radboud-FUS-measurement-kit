@echo off
setlocal

REM Define environment variables
set VENV_NAME=SONOROVER_ONE
set IDE=spyder

REM Activate the virtual environment and launch the IDE
call workon %VENV_NAME%
start %IDE%

endlocal
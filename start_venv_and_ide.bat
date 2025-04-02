@echo off
setlocal

REM Define environment variables
set "DEFAULT_VENV_PATH=%USERPROFILE%\Envs\SONOROVER_ONE"
set "DEFAULT_IDE=spyder"

set "VENV_PATH=%~1"
if "%VENV_PATH%"=="" set "VENV_PATH=%DEFAULT_VENV_PATH%"

set "IDE=%~2"
if "%IDE%"=="" set "IDE=%DEFAULT_IDE%"

REM Activate the virtual environment and launch the IDE
call "%VENV_PATH%\Scripts\activate"
start "" "%IDE%"

endlocal
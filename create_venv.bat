@echo off

:: Download and install Python 3.10 from https://www.python.org/downloads/release/python-31011/

:: Set the Python executable path (ensure Python 3.10 is correctly installed and specify the correct path)
set "DEFAULT_PYTHON_PATH=C:\Program Files\Python310\python.exe"

:: Set a default virtual environment name
set "DEFAULT_VENV_NAME=SONOROVER_ONE"

:: Set a default virtual environment directory
set "DEFAULT_VENV_DIR=%USERPROFILE%\Envs"

:: Collect input parameters with fallbacks to defaults
set "PYTHON_PATH=%~1"
if "%PYTHON_PATH%"=="" set "PYTHON_PATH=%DEFAULT_PYTHON_PATH%"

set "VENV_NAME=%~2"
if "%VENV_NAME%"=="" set "VENV_NAME=%DEFAULT_VENV_NAME%"

set "VENV_DIR=%~3"
if "%VENV_DIR%"=="" set "VENV_DIR=%DEFAULT_VENV_DIR%"

:: Check if the Envs directory exists; if not, create it
if not exist "%VENV_DIR%" (
    mkdir "%VENV_DIR%"
    echo Created directory "%VENV_DIR%"
)

:: Check if Python 3.10 is installed at the specified path
for /f "delims=" %%a in ('"%PYTHON_PATH%" --version 2^>nul') do set "PYTHON_VERSION=%%a"

:: Extract the major and minor version numbers
for /f "tokens=2 delims= " %%b in ("%PYTHON_VERSION%") do set "PYTHON_VERSION=%%b"
echo %PYTHON_VERSION% | findstr /r "^3\.10" >nul
if errorlevel 1 (
    echo Python 3.10 is not installed at the specified path or the version is not correct. Please check the path or install Python 3.10.
    exit /b 1
)

:: Ensure that virtualenv is installed
"%PYTHON_PATH%" -m pip show virtualenv >nul 2>&1
if errorlevel 1 (
    echo Installing virtualenv package...
    "%PYTHON_PATH%" -m pip install virtualenv
) else (
    echo virtualenv is already installed.
)

set "VENV_PATH=%VENV_DIR%\%VENV_NAME%"

:: Check if the virtual environment already exists
if exist "%VENV_PATH%\Scripts\activate" (
    echo Virtual environment already exists at "%VENV_PATH%".
) else (
    echo Creating virtual environment at "%VENV_PATH%".
    "%PYTHON_PATH%" -m virtualenv "%VENV_PATH%"
)

:: Activate the virtual environment
call "%VENV_PATH%\Scripts\activate"

:: Install project-specific dependencies
echo Installing requirements from requirements.txt...
pip install -r requirements.txt

:: Clone and install the FDS software package
git clone https://github.com/Donders-Institute/Radboud-FUS-driving-system-software.git

:: Navigate to the subdirectory containing setup.py
cd Radboud-FUS-driving-system-software

:: Install the package
pip install -r requirements.txt

:: Upgrade pip in virtual environment
python.exe -m pip install --upgrade pip

echo Setup complete. To activate the virtual environment, run: call "%VENV_PATH%\Scripts\activate"
echo The virtual environment is located at: "%VENV_PATH%"

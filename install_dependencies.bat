@echo off

:: Set the Python executable path (ensure Python 3.10 is correctly installed and specify the correct path)
set PYTHON_PATH="C:\Program Files\Python310\python.exe"

:: Set a default virtual environment name (can be overridden by input)
set VENV_NAME=SONOROVER_ONE

:: Check if a virtual environment name was passed as an argument
if "%~1"=="" (
    echo No virtual environment name provided. Using default: %VENV_NAME%
) else (
    set VENV_NAME=%~1
    echo Using provided virtual environment name: %VENV_NAME%
)

:: Check if Python 3.10 is installed by verifying the version output
%PYTHON_PATH% --version 2>nul | findstr /r "^Python 3\.10" >nul
if errorlevel 1 (
    echo Python 3.10 is not installed at the specified path or is not set as the default Python interpreter. Please check the path or install Python 3.10.
    pause
    exit /b 1
)

:: Check if the WORKON_HOME environment variable is set, and set it if not
if "%WORKON_HOME%"=="" (
    echo WORKON_HOME is not set. Setting it temporarily for this session.
    set WORKON_HOME=C:\Users\Public\Envs
    setx WORKON_HOME "C:\Users\Public\Envs"
) else (
    echo WORKON_HOME is set to: %WORKON_HOME%
)

:: Ensure that virtualenv is installed
pip install virtualenv

:: Create the virtual environment inside the WORKON_HOME directory
set VENV_PATH=%WORKON_HOME%\%VENV_NAME%
%PYTHON_PATH% -m venv %VENV_PATH%

:: Activate the virtual environment
call %VENV_NAME%\Scripts\activate

:: Upgrade pip (optional but recommended)
%PYTHON_PATH% -m pip install --upgrade pip

:: Install project-specific dependencies
pip install -r requirements.txt

:: Clone and install the FDS software package
git clone https://github.com/Donders-Institute/Radboud-FUS-driving-system-software.git

:: Navigate to the subdirectory containing setup.py
cd Radboud-FUS-driving-system-software\fus_ds_package

:: Install the package
pip install .

echo Setup complete. To activate the virtual environment, run 'workon %VENV_NAME%'. 
echo The virtual environment is located at %VENV_PATH%.

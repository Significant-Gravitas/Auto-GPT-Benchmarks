setlocal enabledelayedexpansion

@echo off

:: Find the Python executable
for /f "tokens=* usebackq" %%a in (`where python`) do set PYTHON_EXE=%%a
echo Found Python executable: %PYTHON_EXE%

:: Use the Python executable for creating a virtual environment
%PYTHON_EXE% -m venv venv

echo Checking for Python 3.9...
where %PYTHON_EXE% 2> NUL | findstr /R /C:"python.exe" > NUL
if errorlevel 1 (
    set PYTHON_NOT_INSTALLED=1
) else (
    for /f "tokens=* USEBACKQ" %%F in (`%PYTHON_EXE% --version 2^>^&1`) do (
        set PYTHON_VERSION=%%F
    )
    echo !PYTHON_VERSION! | findstr /R "^Python 3.9" > NUL
)

if defined PYTHON_NOT_INSTALLED (
    echo Installing Python 3.9...
    powershell -Command "iwr -outf python-installer.exe https://www.python.org/ftp/python/3.9.10/python-3.9.10-amd64.exe"
    powershell -Command "Start-Process -Wait -FilePath .\python-installer.exe -ArgumentList '/quiet InstallAllUsers=1 PrependPath=1 Include_test=0'"
    del python-installer.exe
) else (
    echo Python 3.9 is already installed.
)

echo Checking for Git...
git --version 2> NUL | findstr /R "^git version" > NUL
if errorlevel 1 (
    echo Installing Git...
    powershell -Command "iwr -outf git-installer.exe https://github.com/git-for-windows/git/releases/download/v2.37.0.windows.1/Git-2.37.0-64-bit.exe"
    powershell -Command "Start-Process -Wait -FilePath .\git-installer.exe -ArgumentList '/VERYSILENT'"
    del git-installer.exe
) else (
    echo Git is already installed.
)

echo Cloning Auto-GPT-Benchmarks repository...
git clone https://github.com/Significant-Gravitas/Auto-GPT-Benchmarks.git
cd Auto-GPT-Benchmarks

echo Creating virtual environment...
%PYTHON_EXE% -m venv venv  || exit /b

echo Activating virtual environment...
call venv\Scripts\activate.bat  || exit /b

echo Installing requirements...
pip install -r requirements.txt  || exit /b

echo Cloning Auto-GPT repository...
cd ..
git clone https://github.com/Significant-Gravitas/Auto-GPT.git

echo Copying API key from .env file...
copy ".env" "Auto-GPT\.env"

echo Update any other necessary configurations in the Auto-GPT\.env file.
echo After configuration, run the run.bat script to execute the first evaluation.
pause

cd Auto-GPT-Benchmarks
call venv\Scripts\activate.bat  || exit /b

echo Building Docker image for Auto-GPT...
cd ..\Auto-GPT
docker build -t autogpt .

echo Running the first evaluation...
cd ..\Auto-GPT-Benchmarks
%PYTHON_EXE% auto_gpt_benchmarking test-match --auto-gpt-path ..\Auto-GPT

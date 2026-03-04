@echo off
cd /d "%~dp0"

REM Load environment variables from .env file if it exists
if exist .env (
    echo Loading environment variables from .env file...
    for /f "usebackq tokens=*" %%a in (".env") do (
        set "%%a"
    )
)

echo Starting Document Download Web Application...
start "" http://localhost:5000
python app.py

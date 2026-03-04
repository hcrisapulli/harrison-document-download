@echo off
cd /d "%~dp0"
echo Starting Document Download Web Application...
start "" http://localhost:5000
python app.py

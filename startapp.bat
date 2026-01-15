@echo off
cd /d "%~dp0"
REM Acctvate Virtual Enviroment
call .\venv\Scripts\activate

REM Run the Application
"pythonw.exe" "main.py"

pause
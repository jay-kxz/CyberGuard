@echo off
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe ( echo Python environment missing. Run first_time_setup.bat first. & pause & exit /b 1 )
start "CyberGuard Python service" .venv\Scripts\python.exe python\app.py
timeout /t 2 /nobreak >nul
call run.bat
echo.
echo The server has stopped.
pause

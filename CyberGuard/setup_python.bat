@echo off
cd /d "%~dp0"
where python >nul 2>nul && (set PY=python) || (set PY=py -3)
if not exist .venv\Scripts\python.exe %PY% -m venv .venv
if errorlevel 1 ( echo Could not create the virtual environment. & exit /b 1 )
.venv\Scripts\python.exe -m pip install flask
if errorlevel 1 ( echo Could not install Flask. Check your internet connection. & exit /b 1 )
echo Python environment is ready.

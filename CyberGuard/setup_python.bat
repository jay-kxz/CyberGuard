@echo off
cd /d "%~dp0"
where python >nul 2>nul && (set PY=python) || (set PY=py -3)
if not exist .venv\Scripts\python.exe %PY% -m venv .venv
if errorlevel 1 ( echo Could not create the virtual environment. & exit /b 1 )
.venv\Scripts\python.exe -m pip install -r python\requirements.txt
if errorlevel 1 (
  echo.
  echo WARNING: not every package could be installed. The analysis tools will still
  echo work; the database features need python-oracledb. If the message above says
  echo that no version could be found, use Python 3.12 or 3.13 for the virtual
  echo environment and run this file again.
  .venv\Scripts\python.exe -m pip install flask
  if errorlevel 1 ( echo Could not install Flask. Check your internet connection. & exit /b 1 )
)
echo Python environment is ready.

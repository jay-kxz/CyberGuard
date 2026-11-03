@echo off
cd /d "%~dp0"
if exist .venv\Scripts\python.exe ( set PY=.venv\Scripts\python.exe ) else ( where python >nul 2>nul && (set PY=python) || (set PY=py -3) )
%PY% -m unittest discover -s tests\python_tests -v

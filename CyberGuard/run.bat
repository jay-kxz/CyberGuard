@echo off
set "PATH=C:\msys64\ucrt64\bin;%PATH%"
cd /d "%~dp0"
if not exist backend\cyberguard.exe ( echo Run build.bat first. & exit /b 1 )
backend\cyberguard.exe frontend 8080

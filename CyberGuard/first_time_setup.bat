@echo off
cd /d "%~dp0"
echo === Step 1 of 3: downloading the C++ libraries ===
call setup.bat
if errorlevel 1 goto fail
echo.
echo === Step 2 of 3: setting up Python ===
call setup_python.bat
if errorlevel 1 goto fail
echo.
echo === Step 3 of 3: building the C++ server ===
call build.bat
if errorlevel 1 goto fail
echo.
echo ALL DONE. Now double-click run_all.bat to start CyberGuard.
pause
exit /b 0
:fail
echo.
echo Something failed. Read the message above, then check README.md.
pause
exit /b 1

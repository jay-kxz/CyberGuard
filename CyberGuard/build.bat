@echo off
setlocal
set "PATH=C:\msys64\ucrt64\bin;%PATH%"
cd /d "%~dp0"
if not exist backend\vendor\httplib.h ( echo Missing backend\vendor\httplib.h - run setup.bat first. & exit /b 1 )
if not exist backend\vendor\json.hpp ( echo Missing backend\vendor\json.hpp - run setup.bat first. & exit /b 1 )
echo Compiling CyberGuard...
g++ -std=c++17 -O2 -Wall -Wextra -Ibackend -Ibackend\vendor ^
  backend\main.cpp backend\server.cpp ^
  backend\modules\identifier_analyzer.cpp backend\modules\score_calculator.cpp ^
  backend\modules\pointer_operations.cpp backend\modules\user_assessment.cpp ^
  -o backend\cyberguard.exe -lws2_32 -lpthread
if errorlevel 1 ( echo. & echo BUILD FAILED. Read the first error above. & exit /b 1 )
echo BUILD OK: backend\cyberguard.exe

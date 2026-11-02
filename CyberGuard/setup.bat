@echo off
cd /d "%~dp0"
if not exist backend\vendor mkdir backend\vendor
if not exist backend\vendor\httplib.h powershell -NoProfile -Command "Invoke-WebRequest https://raw.githubusercontent.com/yhirose/cpp-httplib/v0.18.7/httplib.h -OutFile backend\vendor\httplib.h"
if not exist backend\vendor\json.hpp powershell -NoProfile -Command "Invoke-WebRequest https://github.com/nlohmann/json/releases/download/v3.11.3/json.hpp -OutFile backend\vendor\json.hpp"
if exist backend\vendor\httplib.h if exist backend\vendor\json.hpp ( echo Libraries are ready. & exit /b 0 )
echo Download failed. Check your internet connection and run setup.bat again.
exit /b 1

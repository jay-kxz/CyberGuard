@echo off
set "PATH=C:\msys64\ucrt64\bin;%PATH%"
cd /d "%~dp0\..\.."
g++ -std=c++17 -Wall -Wextra -Ibackend tests\cpp_tests\test_modules.cpp backend\modules\identifier_analyzer.cpp backend\modules\score_calculator.cpp backend\modules\pointer_operations.cpp backend\modules\user_assessment.cpp backend\modules\file_integrity.cpp -o tests\cpp_tests\test_modules.exe
if errorlevel 1 ( echo COMPILE FAILED & exit /b 1 )
tests\cpp_tests\test_modules.exe

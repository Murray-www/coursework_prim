@echo off
rem Build the coursework (Prim's algorithm) with MSVC (Visual Studio 2022).
setlocal

set "VCVARS=C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat"
if not exist "%VCVARS%" (
    echo Error: vcvars64.bat not found. Check the Visual Studio install path.
    exit /b 1
)

call "%VCVARS%" >nul
if errorlevel 1 (
    echo Error: failed to set up the MSVC environment.
    exit /b 1
)

cl /nologo /EHsc /std:c++17 /I inc src\main.cpp src\graph.cpp src\prim.cpp /Fe:prim.exe
if errorlevel 1 (
    echo Build failed.
    exit /b 1
)

echo Build finished: prim.exe
endlocal

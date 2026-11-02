@echo off
REM Build a standalone PhotoConverter.exe for Windows.
setlocal EnableExtensions

cd /d "%~dp0\.."

if not defined PYTHON set PYTHON=python

echo ==^> Ensuring dependencies...
"%PYTHON%" -m pip install -r requirements.txt
if errorlevel 1 exit /b 1

echo ==^> Generating icons...
"%PYTHON%" scripts\generate_icon.py
if errorlevel 1 exit /b 1

echo ==^> Cleaning previous build artifacts...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo ==^> Running PyInstaller...
"%PYTHON%" -m PyInstaller --noconfirm photo_converter.spec
if errorlevel 1 exit /b 1

echo.
echo Build complete for Windows.
dir dist
echo.
echo Run the binary: dist\PhotoConverter.exe
endlocal

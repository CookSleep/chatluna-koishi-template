@echo off
setlocal
chcp 65001 >nul

set "SCRIPT_DIR=%~dp0"
set "SCRIPT=%SCRIPT_DIR%scripts\setup_windows_desktop.py"

if not exist "%SCRIPT%" (
  echo [Error] Setup script not found: %SCRIPT%
  pause
  exit /b 1
)

where python >nul 2>nul
if %errorlevel% equ 0 (
  python "%SCRIPT%"
  goto :finish
)

where py >nul 2>nul
if %errorlevel% equ 0 (
  py -3 "%SCRIPT%"
  goto :finish
)

echo [Error] Python was not found.
echo Please install Python 3 and enable "Add python.exe to PATH" during installation.

:finish
pause

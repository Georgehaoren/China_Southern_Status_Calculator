@echo off
setlocal EnableExtensions EnableDelayedExpansion

rem =============================================================
rem China Southern Status Calculator - CLI Launcher bootstrap
rem 南航明珠等级测算 WebUI - Windows 命令行启动器入口
rem
rem UNC-safe for Parallels Desktop shared folders, e.g. \\Mac\Home\...
rem =============================================================

title China Southern Status Calculator CLI Launcher
chcp 65001 >nul 2>nul

set "SCRIPT_DIR=%~dp0"

rem CMD cannot use UNC paths as current directory. pushd maps UNC to a temp drive.
pushd "%SCRIPT_DIR%" >nul 2>nul
if errorlevel 1 (
    echo.
    echo [ERROR] Failed to enter project directory:
    echo %SCRIPT_DIR%
    echo.
    echo If this project is in a macOS shared folder such as \\Mac\Home\..., try copying it to:
    echo C:\Users\%USERNAME%\Desktop\China_Southern_Status_Calculator
    echo.
    pause
    exit /b 1
)

set "PROJECT_ROOT=%CD%"
set "LOG_DIR=%PROJECT_ROOT%\logs"
set "BATCH_LOG=%LOG_DIR%\batch_bootstrap.log"

if not exist "%LOG_DIR%" mkdir "%LOG_DIR%" >nul 2>nul

call :log "============================================================"
call :log "Starting China Southern Status Calculator CLI Launcher"
call :log "Original script dir: %SCRIPT_DIR%"
call :log "Project root: %PROJECT_ROOT%"

if not exist "%PROJECT_ROOT%\tools\cli_launcher.py" (
    call :log "ERROR: tools\cli_launcher.py was not found."
    echo.
    echo [ERROR] tools\cli_launcher.py was not found under:
    echo %PROJECT_ROOT%
    echo.
    echo Please make sure you copied the launcher patch into the repository root.
    echo.
    pause
    popd
    exit /b 1
)

if not exist "%PROJECT_ROOT%\app.py" (
    call :log "ERROR: app.py was not found."
    echo.
    echo [ERROR] app.py was not found under:
    echo %PROJECT_ROOT%
    echo.
    echo Please run this script from the repository root.
    echo.
    pause
    popd
    exit /b 1
)

call :find_python
if not defined PYTHON_CMD (
    call :log "ERROR: Python was not found."
    echo.
    echo [ERROR] Python 3 was not found.
    echo.
    echo Please install Python 3.9 or newer, then run this file again.
    echo Recommended: https://www.python.org/downloads/windows/
    echo.
    pause
    popd
    exit /b 1
)

call :log "Python command: %PYTHON_CMD%"
echo.
echo Starting China Southern Status Calculator CLI Launcher...
echo Project root: %PROJECT_ROOT%
echo Log file: %BATCH_LOG%
echo.

%PYTHON_CMD% "%PROJECT_ROOT%\tools\cli_launcher.py" %*
set "EXIT_CODE=%ERRORLEVEL%"

call :log "CLI launcher exited with code %EXIT_CODE%."

if not "%EXIT_CODE%"=="0" (
    echo.
    echo Launcher exited with an error.
    echo Batch bootstrap log:
    echo %BATCH_LOG%
    echo.
    echo Python launcher logs may be under:
    echo %PROJECT_ROOT%\logs\launcher.log
    echo %PROJECT_ROOT%\logs\flask_server.log
    echo.
    pause
)

popd
exit /b %EXIT_CODE%

:find_python
    set "PYTHON_CMD="

    py -3 --version >nul 2>nul
    if not errorlevel 1 (
        set "PYTHON_CMD=py -3"
        exit /b 0
    )

    python --version >nul 2>nul
    if not errorlevel 1 (
        set "PYTHON_CMD=python"
        exit /b 0
    )

    python3 --version >nul 2>nul
    if not errorlevel 1 (
        set "PYTHON_CMD=python3"
        exit /b 0
    )

    exit /b 0

:log
    set "MSG=%~1"
    echo [%DATE% %TIME%] %MSG%>>"%BATCH_LOG%"
    exit /b 0

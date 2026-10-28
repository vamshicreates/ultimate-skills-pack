@echo off
setlocal enabledelayedexpansion

echo ============================================================
echo  Ultimate Skills Pack - Windows Launcher
echo ============================================================

where python >nul 2>nul
if %ERRORLEVEL% equ 0 (
    echo [i] Python detected. Launching universal installer...
    python "%~dp0install.py" %*
    goto :end
)

where py >nul 2>nul
if %ERRORLEVEL% equ 0 (
    echo [i] Python launcher detected. Launching universal installer...
    py "%~dp0install.py" %*
    goto :end
)

echo [i] Python not found. Launching PowerShell installer...
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0install.ps1" %*

:end
endlocal

@echo off
rem Single toggle: turns the wake listener OFF if running, ON if stopped
cd /d "%~dp0"
if exist wake_off.flag (
    del wake_off.flag
    start "" "C:\Users\DINESH KUMAR T\AppData\Local\Temp\opencode\jv_venv\Scripts\pythonw.exe" wake.py
    echo Wake listener is ON.
) else (
    echo off> wake_off.flag
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Get-CimInstance Win32_Process -Filter \"Name = 'pythonw.exe'\" | Where-Object { $_.CommandLine -like '*wake.py*' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }"
    echo Wake listener is OFF.
)

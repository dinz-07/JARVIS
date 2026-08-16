@echo off
rem Wake listener OFF - writes the flag (wake.py exits / skips auto-start) and stops any running instance
cd /d "%~dp0"
echo off> wake_off.flag
powershell -NoProfile -ExecutionPolicy Bypass -Command "Get-CimInstance Win32_Process -Filter \"Name = 'pythonw.exe'\" | Where-Object { $_.CommandLine -like '*wake.py*' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }"
echo Wake listener is OFF. To turn it back on, run wake_on.bat

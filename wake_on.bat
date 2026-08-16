@echo off
rem Wake listener ON - deletes the flag and restarts the background listener
cd /d "%~dp0"
if exist wake_off.flag del wake_off.flag
start "" "C:\Users\DINESH KUMAR T\AppData\Local\Temp\opencode\jv_venv\Scripts\pythonw.exe" wake.py
echo Wake listener is ON.

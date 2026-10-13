@echo off
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (
  py -3 start_offline.py
) else (
  python start_offline.py
)
if errorlevel 1 pause

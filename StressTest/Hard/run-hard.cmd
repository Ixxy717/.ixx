@echo off
setlocal
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0run-hard.ps1"
exit /b %ERRORLEVEL%
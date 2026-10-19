@echo off
title Medical Diary
cd /d "%~dp0"
echo ===================================================
echo  Starting Medical Diary...
echo  Opening browser at http://127.0.0.1:8000
echo ===================================================
start http://127.0.0.1:8000
".\.venv\Scripts\python.exe" run.py
pause

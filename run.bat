@echo off
cd /d "%~dp0"
echo ===================================================
echo   Starting AI Interview & Preparation Platform
echo ===================================================
echo.
echo Opening server at http://127.0.0.1:8000 ...
echo Press CTRL+C to stop the server.
echo.
.\.venv\Scripts\python.exe -m uvicorn backend.app:app --host 127.0.0.1 --port 8000 --reload
pause

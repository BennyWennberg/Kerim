@echo off
echo ============================================
echo TenderScout AI - Starte System...
echo ============================================

:: Setze PATH fuer Node.js und Python
set PATH=%PATH%;%USERPROFILE%\AppData\Local\Programs\Python\Python312;%USERPROFILE%\AppData\Local\Programs\Python\Python312\Scripts
set PATH=%PATH%;C:\Program Files\nodejs;%APPDATA%\npm

:: Starte Frontend und Backend
echo.
echo Starte Frontend (Port 3000) und Backend (Port 8000)...
echo.

start "TenderScout Backend" cmd /k "cd backend && python -m uvicorn api:app --reload --host 0.0.0.0 --port 8000"
timeout /t 3 /nobreak >nul
start "TenderScout Frontend" cmd /k "npm run frontend"

echo.
echo ============================================
echo Frontend: http://localhost:3000
echo Backend:  http://localhost:8000
echo ============================================
echo.
echo Druecke eine Taste um den Browser zu oeffnen...
pause >nul

start http://localhost:3000


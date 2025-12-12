# TenderScout AI - Start Script
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "TenderScout AI - Starte System..." -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan

# Aktualisiere PATH
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

# Pruefe ob npm verfuegbar
$npmPath = Get-Command npm -ErrorAction SilentlyContinue
if (-not $npmPath) {
    Write-Host "FEHLER: npm nicht gefunden!" -ForegroundColor Red
    Write-Host "Bitte Node.js installieren: https://nodejs.org/" -ForegroundColor Yellow
    exit 1
}

# Pruefe ob python verfuegbar
$pythonPath = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonPath) {
    Write-Host "FEHLER: Python nicht gefunden!" -ForegroundColor Red
    Write-Host "Bitte Python installieren: https://python.org/" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "Starte Backend (Port 8000)..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\backend'; python -m uvicorn api:app --reload --host 0.0.0.0 --port 8000"

Start-Sleep -Seconds 3

Write-Host "Starte Frontend (Port 3000)..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot'; npm run frontend"

Start-Sleep -Seconds 5

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "Backend:  http://localhost:8000" -ForegroundColor White
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Oeffne Browser
Start-Process "http://localhost:3000"

Write-Host "System gestartet! Browser wird geoeffnet..." -ForegroundColor Green


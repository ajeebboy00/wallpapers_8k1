<#
.SYNOPSIS
    Wallpapers_8k1 Development Automation Script
.DESCRIPTION
    Helper script to run, test, and manage the backend, admin, and mobile services.
#>

param (
    [Parameter(Position=0)]
    [ValidateSet('backend', 'admin', 'test', 'migrate', 'seed', 'clean')]
    [string]$Action = 'backend'
)

$ErrorActionPreference = "Stop"
$ProjectRoot = $PSScriptRoot

switch ($Action) {
    'backend' {
        Write-Host "==> Starting FastAPI Backend..." -ForegroundColor Cyan
        Set-Location "$ProjectRoot/backend"
        if (Test-Path "venv/Scripts/python.exe") {
            & "venv/Scripts/uvicorn.exe" app.main:app --reload --port 8000
        } else {
            python -m uvicorn app.main:app --reload --port 8000
        }
    }
    'admin' {
        Write-Host "==> Starting Admin Panel (Vite)..." -ForegroundColor Cyan
        Set-Location "$ProjectRoot/admin"
        npm run dev
    }
    'test' {
        Write-Host "==> Running Pytest Backend Tests..." -ForegroundColor Cyan
        Set-Location "$ProjectRoot/backend"
        if (Test-Path "venv/Scripts/pytest.exe") {
            & "venv/Scripts/pytest.exe" -v
        } else {
            pytest -v
        }
    }
    'migrate' {
        Write-Host "==> Running Database Migrations..." -ForegroundColor Cyan
        Set-Location "$ProjectRoot"
        if (Test-Path "backend/venv/Scripts/alembic.exe") {
            & "backend/venv/Scripts/alembic.exe" upgrade head
        } else {
            alembic upgrade head
        }
    }
    'clean' {
        Write-Host "==> Cleaning temporary caches..." -ForegroundColor Yellow
        Get-ChildItem -Path "$ProjectRoot" -Recurse -Include "__pycache__", ".pytest_cache" | Remove-Item -Recurse -Force
        Write-Host "Cleaned caches successfully." -ForegroundColor Green
    }
}

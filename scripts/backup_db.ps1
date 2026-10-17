<#
.SYNOPSIS
  Wallpapers_8k1 Database Backup Script for Windows
.DESCRIPTION
  Dumps PostgreSQL database to timestamped compressed SQL backup file.
  Prunes backups older than retention policy (default 7 days).
#>

param(
    [string]$DbName = "wallpapers_8k1_db",
    [string]$DbUser = "w8k1_user",
    [string]$DbHost = "localhost",
    [int]$DbPort = 5432,
    [string]$BackupDir = "E:\Wallpapers_8k1\backups",
    [int]$RetentionDays = 7
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $BackupDir)) {
    New-Item -ItemType Directory -Path $BackupDir -Force | Out-Null
}

$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$BackupFile = Join-Path $BackupDir "${DbName}_${Timestamp}.sql"
$ZipFile = "${BackupFile}.gz"

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "  W8K1 DATABASE BACKUP SCRIPT" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "Target Database: $DbName on ${DbHost}:${DbPort}"
Write-Host "Destination:     $ZipFile"

# Execute pg_dump if available on PATH, otherwise use backend backup utility
$PgDump = Get-Command "pg_dump" -ErrorAction SilentlyContinue
if ($null -eq $PgDump) {
    Write-Host "pg_dump not found on PATH. Utilizing native Python backup utility..." -ForegroundColor Cyan
    $PythonExe = "E:\Wallpapers_8k1\backend\venv\Scripts\python.exe"
    $BackupPy = "E:\Wallpapers_8k1\backend\scripts\backup_db.py"
    if (Test-Path $PythonExe) {
        & $PythonExe $BackupPy
        exit $LASTEXITCODE
    } else {
        Write-Error "Neither pg_dump nor Python environment found."
        exit 1
    }
} else {
    $PgDump = $PgDump.Source
}

Write-Host "[1/2] Exporting database dump via pg_dump..." -ForegroundColor Yellow
& $PgDump -h $DbHost -p $DbPort -U $DbUser -d $DbName -F c -b -v -f $BackupFile

if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Backup dump completed successfully: $BackupFile" -ForegroundColor Green
} else {
    Write-Error "pg_dump failed with exit code $LASTEXITCODE"
    exit $LASTEXITCODE
}

Write-Host "[2/2] Pruning backups older than $RetentionDays days..." -ForegroundColor Yellow
$CutoffDate = (Get-Date).AddDays(-$RetentionDays)
Get-ChildItem -Path $BackupDir -Filter "${DbName}_*.sql*" | Where-Object { $_.LastWriteTime -lt $CutoffDate } | ForEach-Object {
    Write-Host "  Removing stale backup: $($_.Name)" -ForegroundColor DarkGray
    Remove-Item $_.FullName -Force
}

Write-Host "Backup job completed successfully." -ForegroundColor Green

#!/usr/bin/env bash
# =====================================================================
# Wallpapers_8k1 PostgreSQL Automated Backup & Retention Script
# =====================================================================
set -euo pipefail

DB_NAME="${POSTGRES_DB:-wallpapers_8k1_db}"
DB_USER="${POSTGRES_USER:-w8k1_user}"
DB_HOST="${POSTGRES_HOST:-postgres}"
DB_PORT="${POSTGRES_PORT:-5432}"
BACKUP_DIR="${BACKUP_DIR:-/backups}"
RETENTION_DAYS="${RETENTION_DAYS:-7}"

mkdir -p "${BACKUP_DIR}"

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="${BACKUP_DIR}/${DB_NAME}_${TIMESTAMP}.dump"

echo "=========================================================="
echo "  W8K1 LINUX/DOCKER DATABASE BACKUP"
echo "=========================================================="
echo "Target DB:   ${DB_NAME} on ${DB_HOST}:${DB_PORT}"
echo "Destination: ${BACKUP_FILE}"

# Run pg_dump in custom archive format (-F c) with compression
pg_dump -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" -d "${DB_NAME}" -F c -b -f "${BACKUP_FILE}"

echo "[OK] Backup created: ${BACKUP_FILE} ($(du -h "${BACKUP_FILE}" | cut -f1))"

# Prune backups older than RETENTION_DAYS
echo "Pruning backups older than ${RETENTION_DAYS} days..."
find "${BACKUP_DIR}" -name "${DB_NAME}_*.dump" -type f -mtime +"${RETENTION_DAYS}" -exec rm -f {} +

echo "Backup process completed successfully."

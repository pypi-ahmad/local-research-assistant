#!/usr/bin/env bash
set -euo pipefail

STAMP="$(date +%Y%m%d_%H%M%S)"
BACKUP_DIR="/tmp/lra_backup_${STAMP}"
mkdir -p "${BACKUP_DIR}"

docker exec lra-postgres pg_dump -U lra lra > "${BACKUP_DIR}/postgres.sql"
docker run --rm -v qdrant_data:/qdrant_data -v "${BACKUP_DIR}":/backup alpine tar czf /backup/qdrant.tar.gz -C / qdrant_data
docker run --rm -v neo4j_data:/neo4j_data -v "${BACKUP_DIR}":/backup alpine tar czf /backup/neo4j.tar.gz -C / neo4j_data
docker run --rm -v minio_data:/minio_data -v "${BACKUP_DIR}":/backup alpine tar czf /backup/minio.tar.gz -C / minio_data

echo "Backup saved to ${BACKUP_DIR}"

#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <backup_dir>"
  exit 1
fi

BACKUP_DIR="$1"

cat "${BACKUP_DIR}/postgres.sql" | docker exec -i lra-postgres psql -U lra -d lra
docker run --rm -v qdrant_data:/qdrant_data -v "${BACKUP_DIR}":/backup alpine sh -c "cd / && tar xzf /backup/qdrant.tar.gz"
docker run --rm -v neo4j_data:/neo4j_data -v "${BACKUP_DIR}":/backup alpine sh -c "cd / && tar xzf /backup/neo4j.tar.gz"
docker run --rm -v minio_data:/minio_data -v "${BACKUP_DIR}":/backup alpine sh -c "cd / && tar xzf /backup/minio.tar.gz"

echo "Restore completed from ${BACKUP_DIR}"

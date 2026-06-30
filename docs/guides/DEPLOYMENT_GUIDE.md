# Deployment Guide

## Target
Self-hosted Docker deployment on single machine.

## Steps
1. Configure `.env`.
2. `docker compose up -d`.
3. Run migrations from API container:

```bash
docker compose exec api uv run alembic -c apps/api/alembic.ini upgrade head
```

4. Bootstrap admin account.
5. Verify health endpoints and Grafana dashboards.

## Security Hardening
- Set strong secrets in `.env`.
- Restrict API port exposure to trusted network.
- Rotate refresh tokens regularly.
- Enable host firewall and TLS termination via reverse proxy.


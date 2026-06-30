# Folder Structure

```text
local-research-assistant/
  apps/
    api/
      src/lra_api/
        api/               # REST routes and dependencies
        core/              # config, logging, security, rate limiting
        db/                # models, session, migration target metadata
        schemas/           # pydantic contracts
        services/          # auth, ingestion, retrieval, graph, study, monitoring
        workers/           # celery queue app + tasks
      alembic/             # schema migrations
      tests/               # unit + integration tests
    web/
      src/
        app/               # route registration
        pages/             # product pages
        components/        # reusable UI shells
        services/          # API client
        stores/            # local state stores
  infra/
    docker/                # Dockerfiles
    prometheus/            # scrape config
    grafana/               # datasource/dashboard provisioning
    scripts/               # bootstrap + backup/restore scripts
  docs/
    architecture/
    api/
    guides/
```


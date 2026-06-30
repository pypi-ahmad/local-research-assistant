# Database Documentation

## Relational Database (Postgres)

### Core Tables
- `users`: single-user auth account, activation status.
- `refresh_tokens`: rotating refresh token ledger.
- `notebooks`: research workspaces.
- `documents`: source metadata + storage pointers + indexing status.
- `document_chunks`: chunk text units for retrieval/citations.
- `chats`, `messages`, `citations`: conversation history with provenance.
- `highlights`, `annotations`: user research notes linked to sources.
- `search_history`: persistent query history.
- `study_materials`, `flashcards`, `quizzes`: learning artifacts.
- `user_settings`: runtime preferences.
- `audit_events`: security/operations event trail.

## Vector Database (Qdrant)

Collection: `document_chunks`
- Vector: embedding from `qwen3-embedding:4b`.
- Payload fields: `document_id`, `chunk_id`, `text`, `source_name`.

## Graph Database (Neo4j)

Graph schema:
- Nodes: `(:Entity {name})`
- Edges: `(:Entity)-[:RELATED_TO {document_id, relation}]->(:Entity)`

## Object Storage (MinIO)

Buckets:
- `raw-documents`: original uploaded/imported files.
- `derived-artifacts`: future place for previews, parsed outputs, OCR intermediates.

## Migration Strategy
- Alembic migration source: `apps/api/alembic/versions`.
- Apply with:

```bash
uv run alembic -c apps/api/alembic.ini upgrade head
```


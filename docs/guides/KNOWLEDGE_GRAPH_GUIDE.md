# Knowledge Graph Guide

## Purpose
Expose entity relationships across imported research material.

## Pipeline
1. Extract entities/relations from text.
2. Upsert to Neo4j (`Entity` nodes, `RELATED_TO` edges).
3. Query via `/api/v1/graph/query`.

## Current Extraction Strategy
Heuristic capitalized-token extraction with relation linking. This keeps runtime local and lightweight.

## Upgrade Path
You can replace extractor with:
- spaCy NER pipeline
- transformer NER model
- local LLM structured extraction prompt


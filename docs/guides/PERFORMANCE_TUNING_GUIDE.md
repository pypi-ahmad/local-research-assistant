# Performance Tuning Guide

## Ingestion Throughput
- Increase Celery worker concurrency carefully.
- Batch embeddings where model latency allows.
- Keep chunk overlap moderate (100-200 chars).

## Retrieval Latency
- Lower `top_k` from 10 to 6 for interactive chat.
- Disable reranker on constrained CPUs.
- Keep Postgres indexes vacuumed and analyzed.

## GPU/VRAM
- Prefer 3B-4B models for low-latency interactive flow.
- Use lighter fallback model for long sessions.
- Monitor `nvidia-smi` for memory spikes.


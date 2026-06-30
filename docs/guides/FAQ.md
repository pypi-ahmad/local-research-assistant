# FAQ

## Is data sent to cloud LLM providers?
No. Inference is local via Ollama.

## Can I run fully air-gapped?
Yes. Disable web/GitHub/YouTube imports and upload local files only.

## Which model handles embeddings?
Configured embedding model (`qwen3-embedding:4b`) via `.env`.

## Does app support GPU fallback?
Yes. If GPU unavailable, services continue on CPU with higher latency.

## Can I add more users?
Current release is single-user local-first with RBAC-ready schema.


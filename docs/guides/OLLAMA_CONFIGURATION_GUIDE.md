# Ollama Configuration Guide

## Required Local Models
- `granite4.1:3b`
- `qwen3.5:4b`
- `qwen3.5:2b`
- `qwen3-embedding:4b`
- `glm-ocr`
- `phi4-mini:3.8b`
- `translategemma:4b`

## Pull Missing Models

```bash
ollama pull qwen3.5:4b
ollama pull qwen3-embedding:4b
ollama pull glm-ocr
```

## Routing
Model names configured in `.env` and consumed centrally by `OllamaClient`.


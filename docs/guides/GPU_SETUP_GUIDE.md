# GPU Setup Guide

## Goal
Use local NVIDIA GPU for Ollama inference where possible and fall back to CPU when unavailable.

## Verify GPU

```bash
nvidia-smi
```

Expected: RTX 4060 Laptop GPU and CUDA version visible.

## Verify Ollama Sees GPU

```bash
ollama ps
```

## Runtime Notes
- 8 GB VRAM is suitable for 2B-4B models with moderate context windows.
- Prefer balanced routing defaults (`qwen3.5:4b`, `granite4.1:3b`).
- For memory pressure, route to `phi4-mini:3.8b` or `qwen3.5:2b`.


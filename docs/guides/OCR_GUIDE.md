# OCR Guide

## Primary OCR Model
- `glm-ocr` (local Ollama model)

## Trigger Logic
OCR runs when parser yields empty text and source appears scanned/image-based.

## Supported Inputs
- Scanned PDFs
- Screenshots
- Camera photos
- Handwritten notes (best effort)

## Endpoint
`POST /api/v1/documents/ocr` with multipart file.

## Quality Tips
- Use high-contrast images.
- Pre-crop noisy borders.
- For handwriting, increase image resolution where possible.


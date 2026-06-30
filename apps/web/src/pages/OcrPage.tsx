import { Surface } from "../components/Surface";

export function OcrPage() {
  return (
    <Surface title="OCR" subtitle="Scanned PDFs, screenshots, photos, and handwritten notes">
      <p className="text-sm text-slate-300">
        OCR runs through local `glm-ocr` model during ingestion when parser detects image/scanned content.
      </p>
    </Surface>
  );
}

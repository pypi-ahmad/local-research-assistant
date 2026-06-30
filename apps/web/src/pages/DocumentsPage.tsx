import { ChangeEvent, useMemo, useState } from "react";

import { Surface } from "../components/Surface";
import { api } from "../services/api";

export function DocumentsPage() {
  const [notebookId, setNotebookId] = useState("");
  const [dragActive, setDragActive] = useState(false);
  const [uploadState, setUploadState] = useState<string>("");

  const dropClass = useMemo(
    () =>
      `rounded-2xl border-2 border-dashed p-10 text-center transition ${
        dragActive ? "border-accent-400 bg-accent-500/10" : "border-base-700 bg-base-900/30"
      }`,
    [dragActive]
  );

  const onUpload = async (file: File) => {
    if (!notebookId) {
      setUploadState("Enter notebook ID first.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    const response = await api.post(`/documents/upload/${notebookId}`, formData, {
      headers: { "Content-Type": "multipart/form-data" }
    });
    setUploadState(`Queued ingestion job: ${response.data.job_id}`);
  };

  const handleInput = async (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      await onUpload(file);
    }
  };

  return (
    <Surface title="Documents" subtitle="Drag-and-drop ingestion across supported formats">
      <div className="mb-4">
        <input
          className="w-full rounded-xl border border-base-700 bg-base-950 px-4 py-3"
          value={notebookId}
          onChange={(event) => setNotebookId(event.target.value)}
          placeholder="Notebook ID"
        />
      </div>
      <label
        className={dropClass}
        onDragOver={(event) => {
          event.preventDefault();
          setDragActive(true);
        }}
        onDragLeave={() => setDragActive(false)}
        onDrop={(event) => {
          event.preventDefault();
          setDragActive(false);
          const file = event.dataTransfer.files?.[0];
          if (file) {
            void onUpload(file);
          }
        }}
      >
        <input className="hidden" type="file" onChange={(event) => void handleInput(event)} />
        <p className="text-lg font-semibold">Drop file here or click to upload</p>
        <p className="mt-2 text-sm text-slate-400">PDF, DOCX, TXT, CSV, XLSX, PPTX, images, scanned notes</p>
      </label>
      <p className="mt-4 text-sm text-accent-400">{uploadState}</p>
    </Surface>
  );
}

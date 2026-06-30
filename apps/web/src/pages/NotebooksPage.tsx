import { useState } from "react";

import { Surface } from "../components/Surface";
import { api } from "../services/api";

export function NotebooksPage() {
  const [title, setTitle] = useState("");
  const [createdId, setCreatedId] = useState("");

  const createNotebook = async () => {
    const response = await api.post("/notebooks", { title, tags: [] });
    setCreatedId(response.data.id);
    setTitle("");
  };

  return (
    <Surface title="Notebooks" subtitle="Create and manage research workspaces">
      <div className="flex gap-3">
        <input
          className="flex-1 rounded-xl border border-base-700 bg-base-950 px-4 py-3"
          value={title}
          onChange={(event) => setTitle(event.target.value)}
          placeholder="Notebook title"
        />
        <button className="rounded-xl bg-accent-500 px-5 py-3 font-semibold text-base-950" onClick={() => void createNotebook()} type="button">
          Create
        </button>
      </div>
      <p className="mt-3 text-sm text-accent-400">{createdId ? `Created notebook: ${createdId}` : ""}</p>
    </Surface>
  );
}

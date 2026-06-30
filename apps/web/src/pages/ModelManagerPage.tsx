import { useEffect, useState } from "react";

import { Surface } from "../components/Surface";
import { api } from "../services/api";

interface ModelInfo {
  name: string;
  size: string;
  modified: string;
}

export function ModelManagerPage() {
  const [models, setModels] = useState<ModelInfo[]>([]);

  useEffect(() => {
    void api.get("/system/models").then((response) => setModels(response.data ?? []));
  }, []);

  return (
    <Surface title="Model Manager" subtitle="Available local Ollama models and routing targets">
      <div className="space-y-3">
        {models.map((model) => (
          <div key={model.name} className="rounded-xl border border-base-800 bg-base-950 p-3">
            <p className="font-medium text-white">{model.name}</p>
            <p className="text-xs text-slate-400">size: {model.size}</p>
            <p className="text-xs text-slate-400">modified: {new Date(model.modified).toLocaleString()}</p>
          </div>
        ))}
      </div>
    </Surface>
  );
}

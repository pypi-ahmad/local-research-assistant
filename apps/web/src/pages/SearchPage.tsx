import { useState } from "react";

import { Surface } from "../components/Surface";
import { api } from "../services/api";

interface Hit {
  chunk_id: string;
  source_name: string;
  score: number;
  text: string;
}

export function SearchPage() {
  const [query, setQuery] = useState("");
  const [hits, setHits] = useState<Hit[]>([]);

  const run = async () => {
    const response = await api.post("/search/query", { query, top_k: 10 });
    setHits(response.data.hits ?? []);
  };

  return (
    <div className="space-y-6">
      <Surface title="Hybrid Search" subtitle="Semantic + keyword retrieval with filters">
        <div className="flex flex-col gap-3 sm:flex-row">
          <input
            className="flex-1 rounded-xl border border-base-700 bg-base-950 px-4 py-3"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Search indexed content"
          />
          <button className="rounded-xl bg-accent-500 px-5 py-3 font-semibold text-base-950" onClick={() => void run()} type="button">
            Search
          </button>
        </div>
      </Surface>
      <Surface title="Results" subtitle="Relevance ranked and source linked">
        <ul className="space-y-3">
          {hits.map((hit) => (
            <li key={hit.chunk_id} className="rounded-xl border border-base-800 bg-base-950 p-3">
              <div className="flex items-center justify-between">
                <p className="text-sm font-semibold text-accent-400">{hit.source_name}</p>
                <p className="text-xs text-slate-400">score: {hit.score.toFixed(3)}</p>
              </div>
              <p className="mt-1 text-sm text-slate-300">{hit.text}</p>
            </li>
          ))}
          {!hits.length ? <li className="text-sm text-slate-400">No results yet.</li> : null}
        </ul>
      </Surface>
    </div>
  );
}

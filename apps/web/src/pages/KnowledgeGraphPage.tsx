import { useState } from "react";

import { Surface } from "../components/Surface";
import { api } from "../services/api";

interface NodeItem {
  id: string;
  label: string;
}

interface EdgeItem {
  source: string;
  target: string;
  relation: string;
}

export function KnowledgeGraphPage() {
  const [query, setQuery] = useState("AI");
  const [nodes, setNodes] = useState<NodeItem[]>([]);
  const [edges, setEdges] = useState<EdgeItem[]>([]);

  const run = async () => {
    const response = await api.post("/graph/query", { query, limit: 80 });
    setNodes(response.data.nodes ?? []);
    setEdges(response.data.edges ?? []);
  };

  return (
    <div className="space-y-6">
      <Surface title="Knowledge Graph" subtitle="Entity and relationship discovery">
        <div className="flex gap-3">
          <input
            className="flex-1 rounded-xl border border-base-700 bg-base-950 px-4 py-3"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
          />
          <button className="rounded-xl bg-accent-500 px-5 py-3 font-semibold text-base-950" onClick={() => void run()} type="button">
            Search Graph
          </button>
        </div>
      </Surface>
      <Surface title="Graph Snapshot" subtitle="Interactive canvas can be added with Cytoscape or Sigma">
        <p className="text-sm text-slate-400">Nodes: {nodes.length} | Edges: {edges.length}</p>
        <div className="mt-3 grid gap-2 sm:grid-cols-2">
          {edges.slice(0, 20).map((edge, index) => (
            <div key={`${edge.source}-${edge.target}-${index}`} className="rounded-lg border border-base-800 bg-base-950 p-2 text-sm">
              {edge.source} <span className="text-accent-400">{edge.relation}</span> {edge.target}
            </div>
          ))}
        </div>
      </Surface>
    </div>
  );
}

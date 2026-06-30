import { useState } from "react";
import { marked } from "marked";

import { Surface } from "../components/Surface";
import { api } from "../services/api";

interface Citation {
  source_name: string;
  quote: string;
}

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:18000/api/v1";

export function ChatPage() {
  const [notebookId, setNotebookId] = useState("");
  const [query, setQuery] = useState("");
  const [chatId, setChatId] = useState("");
  const [answer, setAnswer] = useState("");
  const [citations, setCitations] = useState<Citation[]>([]);
  const [loading, setLoading] = useState(false);

  const run = async () => {
    if (!notebookId) {
      setAnswer("Notebook ID required.");
      return;
    }

    setLoading(true);
    try {
      let activeChatId = chatId;
      if (!activeChatId) {
        const created = await api.post("/chat/sessions", {
          notebook_id: notebookId,
          title: "Research Session"
        });
        activeChatId = created.data.chat_id;
        setChatId(activeChatId);
      }

      const token = localStorage.getItem("lra_access_token");
      const response = await fetch(`${API_BASE_URL}/chat/sessions/${activeChatId}/stream`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(token ? { Authorization: `Bearer ${token}` } : {})
        },
        body: JSON.stringify({ query, top_k: 6 })
      });

      if (!response.body) {
        setAnswer("No stream body returned.");
        return;
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder("utf-8");
      let buffer = "";
      setAnswer("");
      setCitations([]);

      while (true) {
        const { done, value } = await reader.read();
        if (done) {
          break;
        }

        buffer += decoder.decode(value, { stream: true });
        const events = buffer.split("\n\n");
        buffer = events.pop() || "";

        for (const eventBlock of events) {
          const lines = eventBlock.split("\n");
          const eventType = lines.find((line) => line.startsWith("event:"))?.replace("event:", "").trim();
          const dataLine = lines.find((line) => line.startsWith("data:"));
          const data = dataLine ? dataLine.replace("data:", "").trim() : "";

          if (eventType === "start" && data) {
            const parsed = JSON.parse(data);
            setCitations(parsed.citations || []);
          }
          if (eventType === "token" && data) {
            setAnswer((prev) => `${prev}${prev ? " " : ""}${data}`);
          }
        }
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <Surface title="Chat" subtitle="Grounded research assistant with streamed citations">
        <div className="mb-3">
          <input
            className="w-full rounded-xl border border-base-700 bg-base-950 px-4 py-3"
            value={notebookId}
            onChange={(event) => setNotebookId(event.target.value)}
            placeholder="Notebook ID"
          />
        </div>
        <div className="flex flex-col gap-3 sm:flex-row">
          <input
            className="flex-1 rounded-xl border border-base-700 bg-base-950 px-4 py-3"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Ask grounded question from indexed sources"
            onKeyDown={(event) => {
              if (event.key === "Enter") {
                void run();
              }
            }}
          />
          <button
            className="rounded-xl bg-accent-500 px-5 py-3 font-semibold text-base-950 disabled:opacity-40"
            onClick={() => void run()}
            disabled={loading || !query.trim()}
            type="button"
          >
            {loading ? "Streaming..." : "Ask"}
          </button>
        </div>
      </Surface>
      <Surface title="Answer" subtitle="Markdown-rendered, source-grounded output">
        <article className="prose prose-invert max-w-none" dangerouslySetInnerHTML={{ __html: marked.parse(answer || "No answer yet.") }} />
      </Surface>
      <Surface title="Citations" subtitle="Linked evidence snippets">
        <ul className="space-y-3">
          {citations.map((citation, index) => (
            <li key={`${citation.source_name}-${index}`} className="rounded-xl border border-base-800 bg-base-950 p-3">
              <p className="text-sm font-medium text-accent-400">{citation.source_name}</p>
              <p className="mt-1 text-sm text-slate-300">{citation.quote}</p>
            </li>
          ))}
          {!citations.length ? <li className="text-sm text-slate-400">No citations yet.</li> : null}
        </ul>
      </Surface>
    </div>
  );
}

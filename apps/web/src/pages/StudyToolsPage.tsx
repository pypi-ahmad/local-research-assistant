import { useState } from "react";

import { Surface } from "../components/Surface";
import { api } from "../services/api";

export function StudyToolsPage() {
  const [notebookId, setNotebookId] = useState("");
  const [topic, setTopic] = useState("");
  const [difficulty, setDifficulty] = useState("intermediate");
  const [result, setResult] = useState("");

  const generate = async () => {
    const response = await api.post("/study/generate", {
      notebook_id: notebookId,
      topic,
      difficulty
    });
    setResult(response.data.study_guide);
  };

  return (
    <Surface title="Study Tools" subtitle="Generate guides, flashcards, quiz sets, and revision notes">
      <div className="grid gap-3 sm:grid-cols-3">
        <input className="rounded-xl border border-base-700 bg-base-950 px-4 py-3" placeholder="Notebook ID" value={notebookId} onChange={(event) => setNotebookId(event.target.value)} />
        <input className="rounded-xl border border-base-700 bg-base-950 px-4 py-3" placeholder="Topic" value={topic} onChange={(event) => setTopic(event.target.value)} />
        <select className="rounded-xl border border-base-700 bg-base-950 px-4 py-3" value={difficulty} onChange={(event) => setDifficulty(event.target.value)}>
          <option value="beginner">Beginner</option>
          <option value="intermediate">Intermediate</option>
          <option value="advanced">Advanced</option>
        </select>
      </div>
      <button className="mt-3 rounded-xl bg-accent-500 px-5 py-3 font-semibold text-base-950" onClick={() => void generate()} type="button">
        Generate
      </button>
      <article className="mt-4 whitespace-pre-wrap rounded-xl border border-base-800 bg-base-950 p-3 text-sm text-slate-200">{result || "No study guide generated yet."}</article>
    </Surface>
  );
}

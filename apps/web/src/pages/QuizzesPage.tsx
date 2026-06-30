import { useState } from "react";

import { Surface } from "../components/Surface";
import { api } from "../services/api";

interface Quiz {
  question: string;
  options: string[];
  answer: string;
}

export function QuizzesPage() {
  const [notebookId, setNotebookId] = useState("");
  const [quizzes, setQuizzes] = useState<Quiz[]>([]);

  const load = async () => {
    const response = await api.get(`/study/quizzes/${notebookId}`);
    const payload: Quiz[][] = response.data ?? [];
    setQuizzes(payload.flat());
  };

  return (
    <Surface title="Quizzes" subtitle="Practice tests and interview-style questions">
      <div className="flex gap-3">
        <input className="flex-1 rounded-xl border border-base-700 bg-base-950 px-4 py-3" placeholder="Notebook ID" value={notebookId} onChange={(event) => setNotebookId(event.target.value)} />
        <button className="rounded-xl bg-accent-500 px-5 py-3 font-semibold text-base-950" onClick={() => void load()} type="button">Load</button>
      </div>
      <div className="mt-4 space-y-3">
        {quizzes.map((quiz, index) => (
          <article key={`${quiz.question}-${index}`} className="rounded-xl border border-base-800 bg-base-950 p-3">
            <p className="font-medium text-white">Q{index + 1}. {quiz.question}</p>
            <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-slate-300">
              {quiz.options.map((option) => (
                <li key={option}>{option}</li>
              ))}
            </ul>
            <p className="mt-2 text-sm text-accent-400">Answer: {quiz.answer}</p>
          </article>
        ))}
      </div>
    </Surface>
  );
}

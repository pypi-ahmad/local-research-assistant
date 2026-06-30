import { useState } from "react";

import { Surface } from "../components/Surface";
import { api } from "../services/api";

interface Card {
  front: string;
  back: string;
}

export function FlashcardsPage() {
  const [notebookId, setNotebookId] = useState("");
  const [cards, setCards] = useState<Card[]>([]);

  const load = async () => {
    const response = await api.get(`/study/flashcards/${notebookId}`);
    setCards(response.data ?? []);
  };

  return (
    <Surface title="Flashcards" subtitle="Review generated card decks">
      <div className="flex gap-3">
        <input className="flex-1 rounded-xl border border-base-700 bg-base-950 px-4 py-3" placeholder="Notebook ID" value={notebookId} onChange={(event) => setNotebookId(event.target.value)} />
        <button className="rounded-xl bg-accent-500 px-5 py-3 font-semibold text-base-950" onClick={() => void load()} type="button">Load</button>
      </div>
      <div className="mt-4 grid gap-3 sm:grid-cols-2">
        {cards.map((card, index) => (
          <div key={`${card.front}-${index}`} className="rounded-xl border border-base-800 bg-base-950 p-3">
            <p className="text-xs uppercase text-accent-400">Front</p>
            <p className="mb-2 text-sm">{card.front}</p>
            <p className="text-xs uppercase text-signal-blue">Back</p>
            <p className="text-sm">{card.back}</p>
          </div>
        ))}
      </div>
    </Surface>
  );
}

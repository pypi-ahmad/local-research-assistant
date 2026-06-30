import { Moon, Sun } from "lucide-react";
import { NavLink, Outlet } from "react-router-dom";
import { useEffect, useState } from "react";

const links = [
  ["Dashboard", "/"],
  ["Research Workspace", "/workspace"],
  ["Chat", "/chat"],
  ["Documents", "/documents"],
  ["Knowledge Base", "/knowledge-base"],
  ["Search", "/search"],
  ["OCR", "/ocr"],
  ["Notebooks", "/notebooks"],
  ["Knowledge Graph", "/knowledge-graph"],
  ["Study Tools", "/study-tools"],
  ["Flashcards", "/flashcards"],
  ["Quizzes", "/quizzes"],
  ["Settings", "/settings"],
  ["Model Manager", "/model-manager"],
  ["System Monitoring", "/monitoring"]
] as const;

export function Layout() {
  const [dark, setDark] = useState(true);

  useEffect(() => {
    const handler = (event: KeyboardEvent) => {
      if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "d") {
        event.preventDefault();
        setDark((value) => !value);
      }
      if (event.altKey && event.key.toLowerCase() === "c") {
        event.preventDefault();
        window.location.assign("/chat");
      }
      if (event.altKey && event.key.toLowerCase() === "s") {
        event.preventDefault();
        window.location.assign("/search");
      }
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, []);

  return (
    <div className={dark ? "dark" : ""}>
      <div className="min-h-screen bg-base-950 text-slate-100 lg:flex">
        <aside className="w-full border-b border-base-800 bg-base-900/80 backdrop-blur lg:w-72 lg:border-b-0 lg:border-r">
          <div className="flex items-center justify-between p-5">
            <div>
              <h1 className="font-display text-2xl text-white">Local Research Assistant</h1>
              <p className="text-sm text-slate-400">Offline, private, production-grade</p>
            </div>
            <button
              className="rounded-lg border border-base-700 p-2 hover:bg-base-800"
              onClick={() => setDark((value) => !value)}
              type="button"
            >
              {dark ? <Sun size={16} /> : <Moon size={16} />}
            </button>
          </div>
          <nav className="grid max-h-[70vh] grid-cols-2 gap-2 overflow-auto p-3 lg:grid-cols-1">
            {links.map(([label, path]) => (
              <NavLink
                key={path}
                to={path}
                className={({ isActive }) =>
                  `rounded-lg px-3 py-2 text-sm transition ${
                    isActive ? "bg-accent-500/20 text-accent-400" : "text-slate-300 hover:bg-base-800"
                  }`
                }
              >
                {label}
              </NavLink>
            ))}
          </nav>
        </aside>
        <main className="flex-1 p-4 sm:p-6 lg:p-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
}

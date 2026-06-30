import { Surface } from "../components/Surface";

const cards = [
  ["Indexed Documents", "0"],
  ["Active Notebooks", "0"],
  ["Queued Jobs", "0"],
  ["Model Health", "Unknown"]
];

export function DashboardPage() {
  return (
    <div className="space-y-6">
      <Surface title="Dashboard" subtitle="Workspace health and research velocity">
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          {cards.map(([label, value]) => (
            <article key={label} className="rounded-xl border border-base-800 bg-base-800/40 p-4">
              <p className="text-xs uppercase tracking-wide text-slate-400">{label}</p>
              <p className="mt-2 text-2xl font-semibold text-white">{value}</p>
            </article>
          ))}
        </div>
      </Surface>
      <Surface title="Quick Actions" subtitle="Jump into common workflows">
        <div className="grid gap-3 sm:grid-cols-2">
          <button className="rounded-xl bg-accent-500 px-4 py-3 font-medium text-base-950 hover:bg-accent-400">Upload documents</button>
          <button className="rounded-xl border border-base-700 px-4 py-3 hover:bg-base-800">Create notebook</button>
          <button className="rounded-xl border border-base-700 px-4 py-3 hover:bg-base-800">Start RAG session</button>
          <button className="rounded-xl border border-base-700 px-4 py-3 hover:bg-base-800">Run system diagnostics</button>
        </div>
      </Surface>
    </div>
  );
}

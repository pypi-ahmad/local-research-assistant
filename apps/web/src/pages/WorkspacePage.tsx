import { Surface } from "../components/Surface";

export function WorkspacePage() {
  return (
    <Surface title="Research Workspace" subtitle="Session memory, notes, highlights, and active context">
      <div className="grid gap-4 lg:grid-cols-2">
        <textarea
          className="min-h-60 rounded-xl border border-base-700 bg-base-950 p-3 text-sm"
          placeholder="Write research notes, hypotheses, and findings..."
        />
        <div className="space-y-3">
          <div className="rounded-xl border border-base-700 bg-base-950 p-3">
            <p className="text-sm text-slate-300">Session memory timeline will appear here after chat/search activity.</p>
          </div>
          <div className="rounded-xl border border-base-700 bg-base-950 p-3">
            <p className="text-sm text-slate-300">Pinned citations and highlights appear here.</p>
          </div>
        </div>
      </div>
    </Surface>
  );
}

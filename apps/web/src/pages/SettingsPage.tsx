import { Surface } from "../components/Surface";

export function SettingsPage() {
  return (
    <Surface title="Settings" subtitle="Model routing, privacy, retention, and workspace preferences">
      <div className="grid gap-3 sm:grid-cols-2">
        <label className="flex items-center justify-between rounded-xl border border-base-700 bg-base-950 p-3 text-sm">
          Dark mode
          <input type="checkbox" defaultChecked />
        </label>
        <label className="flex items-center justify-between rounded-xl border border-base-700 bg-base-950 p-3 text-sm">
          Persist search history
          <input type="checkbox" defaultChecked />
        </label>
      </div>
    </Surface>
  );
}

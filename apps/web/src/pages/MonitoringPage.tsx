import { useEffect, useState } from "react";

import { Surface } from "../components/Surface";
import { api } from "../services/api";

interface Status {
  cpu_percent: number;
  memory_percent: number;
  gpu_utilization: number | null;
  gpu_memory_used_mb: number | null;
  queue_depth: number;
}

export function MonitoringPage() {
  const [status, setStatus] = useState<Status | null>(null);

  useEffect(() => {
    const load = () => {
      void api.get("/system/status").then((response) => setStatus(response.data));
    };
    load();
    const timer = setInterval(load, 5000);
    return () => clearInterval(timer);
  }, []);

  return (
    <Surface title="System Monitoring" subtitle="GPU, memory, queue depth, and runtime health">
      {!status ? (
        <p className="text-sm text-slate-400">Loading metrics...</p>
      ) : (
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
          <MetricCard label="CPU" value={`${status.cpu_percent.toFixed(1)}%`} />
          <MetricCard label="Memory" value={`${status.memory_percent.toFixed(1)}%`} />
          <MetricCard label="GPU Util" value={status.gpu_utilization !== null ? `${status.gpu_utilization.toFixed(1)}%` : "N/A"} />
          <MetricCard label="GPU Memory" value={status.gpu_memory_used_mb !== null ? `${status.gpu_memory_used_mb.toFixed(0)} MB` : "N/A"} />
          <MetricCard label="Queue" value={`${status.queue_depth}`} />
        </div>
      )}
    </Surface>
  );
}

function MetricCard({ label, value }: { label: string; value: string }) {
  return (
    <article className="rounded-xl border border-base-800 bg-base-950 p-3">
      <p className="text-xs uppercase text-slate-400">{label}</p>
      <p className="mt-1 text-xl font-semibold text-white">{value}</p>
    </article>
  );
}

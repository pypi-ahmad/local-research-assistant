import { PropsWithChildren } from "react";

interface SurfaceProps extends PropsWithChildren {
  title: string;
  subtitle?: string;
}

export function Surface({ title, subtitle, children }: SurfaceProps) {
  return (
    <section className="rounded-2xl border border-base-800 bg-base-900/70 p-5 shadow-lg shadow-black/20">
      <header className="mb-4">
        <h2 className="text-xl font-semibold text-white">{title}</h2>
        {subtitle ? <p className="mt-1 text-sm text-slate-400">{subtitle}</p> : null}
      </header>
      {children}
    </section>
  );
}

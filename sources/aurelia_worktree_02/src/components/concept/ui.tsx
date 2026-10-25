import type { ReactNode } from "react";
import { cn } from "@/lib/utils";

export function PageHeader({
  chapter,
  kicker,
  title,
  lead,
}: {
  chapter: string;
  kicker: string;
  title: string;
  lead: string;
}) {
  return (
    <header className="max-w-3xl">
      <p className="text-sm font-medium tracking-[0.18em] text-muted uppercase">
        Kapitel {chapter} · {kicker}
      </p>
      <h1 className="mt-4 font-display text-4xl font-medium text-fg sm:text-5xl">{title}</h1>
      <p className="mt-5 max-w-2xl text-lg leading-relaxed text-muted">{lead}</p>
    </header>
  );
}

export function Reco({ children }: { children: ReactNode }) {
  return (
    <aside
      className="rounded-xl border border-primary/20 bg-primary px-5 py-4 text-primary-fg sm:px-6 sm:py-5"
      aria-label="Empfehlung"
    >
      <p className="text-xs font-medium tracking-[0.16em] uppercase text-primary-fg/70">
        Empfehlung
      </p>
      <div className="mt-2 text-[0.975rem] leading-relaxed text-pretty">{children}</div>
    </aside>
  );
}

export function Callout({
  title,
  children,
}: {
  title: string;
  children: ReactNode;
}) {
  return (
    <aside className="rounded-xl border border-border bg-elevated px-5 py-4 sm:px-6 sm:py-5">
      <p className="text-xs font-medium tracking-[0.16em] text-muted uppercase">{title}</p>
      <div className="mt-2 text-[0.975rem] leading-relaxed text-fg text-pretty">{children}</div>
    </aside>
  );
}

export function Spec({ rows }: { rows: Array<[string, string]> }) {
  return (
    <dl className="divide-y divide-border overflow-hidden rounded-xl border border-border bg-elevated">
      {rows.map(([k, v]) => (
        <div key={k} className="grid gap-1 px-5 py-4 sm:grid-cols-[13rem_1fr] sm:gap-6 sm:px-6">
          <dt className="text-sm font-medium text-muted">{k}</dt>
          <dd className="text-[0.975rem] leading-relaxed text-fg">{v}</dd>
        </div>
      ))}
    </dl>
  );
}

export function Cards({
  items,
}: {
  items: Array<{ title: string; body: string; kicker?: string }>;
}) {
  return (
    <ul className="grid gap-3 sm:grid-cols-2">
      {items.map((item) => (
        <li
          key={item.title}
          className="rounded-xl border border-border bg-elevated p-5 sm:p-6"
        >
          {item.kicker ? (
            <p className="text-xs font-medium tracking-[0.14em] text-muted uppercase">
              {item.kicker}
            </p>
          ) : null}
          <h3 className={cn("font-display text-xl font-medium", item.kicker ? "mt-2" : "")}>
            {item.title}
          </h3>
          <p className="mt-2 text-[0.975rem] leading-relaxed text-muted">{item.body}</p>
        </li>
      ))}
    </ul>
  );
}

export function Stack({ children }: { children: ReactNode }) {
  return <div className="flex flex-col gap-8 sm:gap-10">{children}</div>;
}

export function H2({ children }: { children: ReactNode }) {
  return <h2 className="font-display text-2xl font-medium text-fg sm:text-3xl">{children}</h2>;
}

export function P({ children }: { children: ReactNode }) {
  return <p className="max-w-3xl text-[1.05rem] leading-relaxed text-fg">{children}</p>;
}

export function List({ items }: { items: string[] }) {
  return (
    <ul className="max-w-3xl space-y-2.5">
      {items.map((item) => (
        <li key={item} className="flex gap-3 text-[1.05rem] leading-relaxed">
          <span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-primary" aria-hidden />
          <span>{item}</span>
        </li>
      ))}
    </ul>
  );
}

export function DataTable({
  caption,
  headers,
  rows,
}: {
  caption: string;
  headers: string[];
  rows: Array<{ key: string; cells: string[] }>;
}) {
  return (
    <div>
      <ul className="grid gap-3 lg:hidden">
        {rows.map((row) => (
          <li key={row.key} className="rounded-xl border border-border bg-elevated p-4">
            <p className="font-mono text-xs text-subtle">{row.cells[0]}</p>
            <dl className="mt-3 space-y-2">
              {headers.slice(1).map((h, i) => (
                <div key={h}>
                  <dt className="text-xs font-medium tracking-[0.12em] text-muted uppercase">
                    {h}
                  </dt>
                  <dd className="mt-0.5 text-sm leading-relaxed text-fg">{row.cells[i + 1]}</dd>
                </div>
              ))}
            </dl>
          </li>
        ))}
      </ul>
      <div className="hidden overflow-x-auto rounded-xl border border-border bg-elevated lg:block">
        <table className="w-full min-w-[64rem] text-left text-sm">
          <caption className="sr-only">{caption}</caption>
          <thead>
            <tr className="border-b border-border bg-surface/80">
              {headers.map((h) => (
                <th
                  key={h}
                  scope="col"
                  className="px-4 py-3 text-xs font-medium tracking-[0.12em] text-muted uppercase"
                >
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row.key} className="border-b border-border last:border-0 align-top">
                {row.cells.map((c, i) => (
                  <td
                    key={`${row.key}-${headers[i]}`}
                    className={cn(
                      "px-4 py-3 leading-relaxed text-fg",
                      i === 0 ? "font-mono text-xs whitespace-nowrap text-muted" : "text-[0.925rem]",
                    )}
                  >
                    {c}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

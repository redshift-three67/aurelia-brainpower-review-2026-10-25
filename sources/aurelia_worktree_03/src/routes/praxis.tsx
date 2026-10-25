import { useEffect, useState } from "react";
import { createFileRoute, Link } from "@tanstack/react-router";
import { RedirectToSignIn, UserButton } from "@/lib/auth/gates";
import { useCurrentUserState } from "@/lib/auth/use-current-user";
import {
  addSecondTenant,
  ensurePrimaryTenant,
  roleLabel,
  type MembershipRow,
} from "@/lib/praxis/memberships";

export const Route = createFileRoute("/praxis")({ component: Praxis });

function Praxis() {
  const { user, isPending } = useCurrentUserState();
  const [rows, setRows] = useState<MembershipRow[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (!user) return;
    let cancelled = false;
    void (async () => {
      try {
        const next = await ensurePrimaryTenant();
        if (!cancelled) setRows(next);
      } catch (err) {
        if (!cancelled) setError(err instanceof Error ? err.message : "Mandant konnte nicht geladen werden.");
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [user]);

  if (isPending) {
    return (
      <main className="grid min-h-dvh place-items-center bg-bg">
        <div className="h-12 w-48 animate-pulse rounded-xl bg-surface" />
      </main>
    );
  }
  if (!user) return <RedirectToSignIn />;

  async function onSecond() {
    setBusy(true);
    setError(null);
    try {
      setRows(await addSecondTenant());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Zweiter Mandant fehlgeschlagen.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="min-h-dvh bg-bg">
      <header className="border-b border-border bg-elevated/90">
        <div className="mx-auto flex max-w-5xl items-center justify-between gap-4 px-4 py-4 sm:px-8">
          <div>
            <p className="text-xs font-medium tracking-[0.16em] text-muted uppercase">Phase 1 · Gehäuse</p>
            <h1 className="font-display text-2xl font-medium text-fg">Praxis</h1>
          </div>
          <div className="flex items-center gap-3">
            <Link to="/" className="text-sm text-muted underline decoration-from-font">
              Verfassung
            </Link>
            <UserButton />
          </div>
        </div>
      </header>

      <div className="mx-auto max-w-5xl px-4 py-10 sm:px-8">
        <p className="max-w-2xl text-[1.05rem] leading-relaxed text-fg">
          Angemeldet als {user.displayName ?? user.primaryEmail ?? "Praktiker"}. Hier
          entstehen Mandant und Rolle. Klienten, Zeugen, Analyse und Timer kommen
          in späteren Phasen. dataClass bleibt synthetic.
        </p>

        {error ? <p className="mt-4 text-sm text-danger">{error}</p> : null}

        <section className="mt-10">
          <h2 className="font-display text-xl font-medium">Ihre Mandanten</h2>
          {!rows ? (
            <div className="mt-4 h-24 animate-pulse rounded-xl bg-surface" />
          ) : (
            <ul className="mt-4 grid gap-3">
              {rows.map((r) => (
                <li
                  key={r.tenant_id}
                  className="rounded-xl border border-border bg-elevated px-5 py-4"
                >
                  <p className="font-medium text-fg">{r.name}</p>
                  <p className="mt-1 text-sm text-muted">
                    {roleLabel(r.role)} · {r.data_class} · {r.tenant_id.slice(0, 8)}…
                  </p>
                </li>
              ))}
            </ul>
          )}
          {rows && rows.length < 2 ? (
            <button
              type="button"
              disabled={busy}
              onClick={() => void onSecond()}
              className="mt-4 min-h-11 rounded-lg border border-border bg-elevated px-4 text-sm font-medium text-fg disabled:opacity-60"
            >
              {busy ? "Anlegen…" : "Zweiten Mandanten anlegen (Isolationstest)"}
            </button>
          ) : null}
        </section>

        <section className="mt-12 grid gap-3 sm:grid-cols-3">
          {[
            ["Klienten", "Phase 2", "Noch leer. Keine echten Personen."],
            ["Analyse / Timer", "Phase 4–5", "Keine CUDA, kein USB in diesem Gehäuse."],
            [
              "Ausgeschlossene Medienphase",
              "gestrichen",
              "O08 / D10: Video, WebRTC, TURN und Aufzeichnung sind vollständig ausgeschlossen.",
            ],
          ].map(([t, k, b]) => (
            <article key={t} className="rounded-xl border border-border bg-elevated p-5">
              <p className="text-xs font-medium tracking-[0.14em] text-muted uppercase">{k}</p>
              <h3 className="mt-2 font-display text-lg font-medium">{t}</h3>
              <p className="mt-2 text-sm leading-relaxed text-muted">{b}</p>
            </article>
          ))}
        </section>
      </div>
    </main>
  );
}

import { useEffect, useMemo, useState } from "react";
import { createFileRoute, Link } from "@tanstack/react-router";
import { ConceptShell } from "@/components/concept/shell";
import { PageHeader, Reco, Stack, H2, P, DataTable, Callout } from "@/components/concept/ui";
import { ID_FAMILIEN, D08_D12 } from "@/lib/concept/id-legend";
import {
  DECISIONS,
  DECISION_STORAGE_KEY,
  LOCK_LABEL,
  type DecisionLock,
  type Vote,
  type VoteMap,
} from "@/lib/concept/decisions";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/entscheidungen")({ component: Page });

const VOTE_LABEL: Record<Vote, string> = {
  zustimmen: "Zustimmen",
  aendern: "Ändern",
  offen: "Offen",
};

function lockClass(lock: DecisionLock, active: boolean) {
  if (lock === "gesetzt") return active ? "text-primary-fg/80" : "text-primary";
  if (lock === "zur-bestaetigung") return active ? "text-primary-fg/80" : "text-warn";
  return active ? "text-primary-fg/70" : "text-subtle";
}

function Page() {
  const [votes, setVotes] = useState<VoteMap>({});
  const [ready, setReady] = useState(false);

  useEffect(() => {
    try {
      const raw = localStorage.getItem(DECISION_STORAGE_KEY);
      if (raw) setVotes(JSON.parse(raw) as VoteMap);
    } catch {
      /* ignore broken local state */
    }
    setReady(true);
  }, []);

  useEffect(() => {
    if (!ready) return;
    localStorage.setItem(DECISION_STORAGE_KEY, JSON.stringify(votes));
  }, [votes, ready]);

  const counts = useMemo(() => {
    const locked = DECISIONS.filter((d) => d.lock === "gesetzt").length;
    const pending = DECISIONS.filter((d) => d.lock === "zur-bestaetigung").length;
    const open = DECISIONS.filter((d) => d.lock === "empfohlen").length;
    const all = DECISIONS.map((d) => votes[d.id] ?? "offen");
    return {
      locked,
      pending,
      open,
      aendern: all.filter((v) => v === "aendern").length,
    };
  }, [votes]);

  function setVote(id: string, vote: Vote) {
    setVotes((prev) => ({ ...prev, [id]: vote }));
  }

  return (
    <ConceptShell>
      <Stack>
        <PageHeader
          chapter="10"
          kicker="Entscheidungen"
          title="D-Punkte sind Leitentscheidungen, keine Dokumente."
          lead="D08, D10, D12 gesetzt. D09 und D11 bleiben Wiedervorlage. X akzeptiert. Phase 1 läuft."
        />

        <Reco>
          {counts.locked} gesetzt · {counts.pending} zur Bestätigung · {counts.open} empfohlen ·{" "}
          {counts.aendern} Änderungswunsch in diesem Browser. Tabellen:{" "}
          <Link to="/freigabe" className="underline decoration-from-font">
            Kapitel 00b Freigabe
          </Link>
          .
        </Reco>

        <div>
          <H2>Was die Buchstaben bedeuten</H2>
          <P>
            D01 ist keine Datei. docs/01-vision.md ist keine Leitentscheidung. Dieselbe
            Zahl in zwei Alphabeten trifft sich nur zufällig.
          </P>
          <div className="mt-5">
            <DataTable
              caption="ID-Familien"
              headers={["Präfix", "Name", "Bedeutung", "Beispiel"]}
              rows={ID_FAMILIEN.map((f) => ({
                key: f.prefix,
                cells: [f.prefix, f.name, f.bedeutet, f.beispiel],
              }))}
            />
          </div>
        </div>

        <div>
          <H2>D08–D12 nach dem 24. August</H2>
          <P>
            Das sind fünf Leitentscheidungen hinter dem Kern. Sie sind nicht unklar.
            Sie sind nachrangig, weil Auth noch aus ist und Video/Abo/Codec nicht den
            Timer oder die Ada tragen.
          </P>
          <div className="mt-5">
            <DataTable
              caption="D08–D12 empfohlen"
              headers={["ID", "Titel", "Kern", "Warum noch empfohlen"]}
              rows={D08_D12.map((d) => ({
                key: d.id,
                cells: [d.id, d.titel, d.kern, d.warumEmpfohlen],
              }))}
            />
          </div>
        </div>

        <Callout title="Gesetzt vs. empfohlen">
          Gesetzt bindet den nächsten Slice. Empfohlen ist die bevorzugte Lösung,
          sobald der Slice dran ist — Sie können sie noch kippen, ohne den Kern zu
          öffnen. H1–H3 / D24 sind gesetzt. Wo Sie noch entscheiden:{" "}
          <Link to="/offen" className="underline decoration-from-font">
            Offen
          </Link>
          .
        </Callout>

        <H2>Alle Leitentscheidungen</H2>

        <ol className="space-y-6">
          {DECISIONS.map((d) => {
            const vote = votes[d.id] ?? "offen";
            const pending = d.lock === "zur-bestaetigung";
            return (
              <li
                key={d.id}
                className="rounded-xl border border-border bg-elevated p-5 sm:p-6"
              >
                <p className="text-xs font-medium tracking-[0.16em] text-muted uppercase">
                  {d.id} · {d.chapter}
                  <span className={cn("ml-3 tracking-[0.08em]", lockClass(d.lock, false))}>
                    {LOCK_LABEL[d.lock]}
                  </span>
                </p>
                <h2 className="mt-2 font-display text-2xl font-medium text-fg">{d.title}</h2>
                <p className="mt-3 text-[1.02rem] leading-relaxed text-fg">{d.summary}</p>
                {pending ? (
                  <p className="mt-2 text-sm text-warn">
                    Wartet auf C-IDs in der Freigabe. Nicht still als gesetzt behandeln.
                  </p>
                ) : null}

                <div className="mt-5 grid gap-4">
                  <Block kicker="Empfehlung" text={d.recommendation} />
                  <Block kicker="Warum" text={d.why} />
                  <Block kicker="Alternative" text={d.alternative} />
                  <Block kicker="Risiko bei Ignorieren" text={d.riskIfIgnored} />
                </div>

                <div
                  className="mt-5 flex flex-col gap-2 sm:flex-row"
                  role="group"
                  aria-label={`Abstimmung ${d.id}`}
                >
                  {(["zustimmen", "aendern", "offen"] as Vote[]).map((v) => (
                    <button
                      key={v}
                      type="button"
                      onClick={() => setVote(d.id, v)}
                      className={cn(
                        "min-h-11 flex-1 rounded-lg border px-4 py-2.5 text-sm font-medium transition-colors duration-150",
                        vote === v
                          ? "border-primary bg-primary text-primary-fg"
                          : "border-border bg-bg text-fg hover:bg-surface",
                      )}
                    >
                      {VOTE_LABEL[v]}
                    </button>
                  ))}
                </div>
              </li>
            );
          })}
        </ol>
      </Stack>
    </ConceptShell>
  );
}

function Block({ kicker, text }: { kicker: string; text: string }) {
  return (
    <div>
      <p className="text-xs font-medium tracking-[0.14em] text-muted uppercase">{kicker}</p>
      <p className="mt-1 text-[0.975rem] leading-relaxed text-fg">{text}</p>
    </div>
  );
}

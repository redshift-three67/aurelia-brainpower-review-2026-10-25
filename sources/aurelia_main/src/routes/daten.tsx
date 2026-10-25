import { createFileRoute } from "@tanstack/react-router";
import { ConceptShell } from "@/components/concept/shell";
import { Callout, Cards, H2, List, P, PageHeader, Reco, Spec, Stack } from "@/components/concept/ui";

export const Route = createFileRoute("/daten")({ component: Page });

function Page() {
  return (
    <ConceptShell>
      <Stack>
        <PageHeader
          chapter="04"
          kicker="Datenhaltung"
          title="Mehrdimensional heißt: würfelbar, zeitfähig, isoliert."
          lead="Keine Marketing-„Multi-DB“. Ein hartes Postgres mit Timescale, Vektor und JSONB, dazu ein analytischer Side-Car. Jede Zahl hat Mandant, Zeit, Kernel und Zweck."
        />

        <Reco>
          PostgreSQL 16 + TimescaleDB + pgvector + JSONB auf Debian. MinIO für Medien.
          DuckDB/Arrow nur als Lesewarehouse für Trends und Reports — niemals als Akte.
        </Reco>

        <Spec
          rows={[
            ["OLTP", "Mandanten, Nutzer, Gruppen, Sitzungen, Einwilligungen, Quotas."],
            ["Zeitreihe", "Timescale-Hypertables für Timer-Ticks, GPU-Telemetrie, Harmonisierungskurven."],
            ["Würfel", "Dimensionen: Mandant, Praktiker, Klient, Rate-Achse, Protokollversion, Hardwareprofil, Zeit."],
            ["Sparse Maße", "JSONB oder tensor-artige Arrays für mehrdimensionale Scores; Schema versioniert."],
            ["Ähnlichkeit", "pgvector für Rate-Muster und Verlaufsnachbarn innerhalb desselben Mandanten."],
            ["Hierarchie", "ltree für Rate-Kataloge und Gruppen."],
            ["Objekte", "MinIO, serverseitig verschlüsselt, Keys pro Mandant."],
            ["OLAP", "Nachtweiser Export anonymisierter Aggregate in DuckDB für Reports."],
          ]}
        />

        <div>
          <H2>Fachliche Verwaltungen</H2>
          <div className="mt-5">
            <Cards
              items={[
                {
                  title: "Analyseverwaltung",
                  body: "Jeder Scan ist ein Lauf mit Passport. Rohfeatures bleiben an die Kernel-Version gebunden. Vergleichbarkeit nur bei gleichem Kernel oder ausgewiesener Migration.",
                },
                {
                  title: "Zwischenablage",
                  body: "AnalysisDraft zwischen den Kernen. Anpassen, CopyGuard, Promote. Harmonisierung startet nie aus dem Rohscan.",
                },
                {
                  title: "Harmonisierungsverwaltung",
                  body: "Spuren, Fenster, parallele Kanäle, Intensitätskurven. Timer schreibt Ist. queued → armed → running ⇄ paused → stopped.",
                },
                {
                  title: "Archivverwaltung",
                  body: "WORM-ähnliche Periode nach Abschluss. Kein stilles Überschreiben. Löschung nur über das Löschkonzept (Frist, Antrag, Mandantenende).",
                },
                {
                  title: "Trendverwaltung",
                  body: "Continuous Aggregates über Zeit und Rate-Achsen. Keine klinischen Vorhersagen. Trends sind Beschreibungen, nicht Prognosen.",
                },
                {
                  title: "Reportverwaltung",
                  body: "Vorlagen, signierbare PDFs, Mandantenbranding. Jeder Report zitiert Ausweis-IDs. Export für Auskunft (Art. 15) ist derselbe Pfad.",
                },
                {
                  title: "Dienstverwaltung",
                  body: "Angebote, Kontingente, Termine, Erinnerungen — organisatorisch, ohne Gesundheitsclaim im Leistungstext.",
                },
              ]}
            />
          </div>
        </div>

        <div>
          <H2>Leistungsregeln</H2>
          <div className="mt-4">
            <List
              items={[
                "Jede Tabelle mit Personenbezug trägt tenant_id, RLS, und wo nötig encryption_key_id.",
                "Hot-Path-Writes bleiben schmal; große JSONB-Dokumente nicht im Timer-Tick.",
                "Indizes entlang der echten Queries: (tenant_id, client_id, time), (tenant_id, kernel, time).",
                "Vacuum, Hypertables-Kompression, zstd auf Archive — RAM und Platte sind Teil der Akkuratesse.",
                "Mandanten-Export und -Löschung sind Jobs mit Protokoll, keine Handarbeit in psql.",
              ]}
            />
          </div>
        </div>

        <Callout title="Zukunft">
          Wenn ein Mandant Isolation-SLA kauft, wandert er in ein eigenes Schema oder
          eine eigene Datenbank — hinter derselben API. Der Würfel ändert sich nicht,
          nur die physische Trennwand.
        </Callout>
      </Stack>
    </ConceptShell>
  );
}

import { createFileRoute, Link } from "@tanstack/react-router";
import { ConceptShell } from "@/components/concept/shell";
import { Callout, Cards, H2, List, P, PageHeader, Reco, Stack } from "@/components/concept/ui";
import { HybridDiagram } from "@/components/concept/diagrams";
import { NAV } from "@/lib/concept/nav";

export const Route = createFileRoute("/")({ component: Home });

function Home() {
  return (
    <ConceptShell>
      <Stack>
        <PageHeader
          chapter="00"
          kicker="Überblick"
          title="C01–C12 gesetzt. Die Uhr liegt auf der Platte, die Ada rechnet."
          lead="AURELIA bleibt Wellbeing-Software auf dem GPU Server M G1. Virtuelle Harmonisierungstimer sind viele und klein. Nach einem Reset zählt Postgres, nicht VRAM. CopyGuard sitzt im RAM. Phase 1 läuft ausschließlich synthetisch."
        />

        <Reco>
          C01–C12 und der X-Katalog sind gesetzt. Phase 1:{" "}
          <Link to="/praxis" className="underline decoration-from-font">
            Praxis
          </Link>
          . Wiedervorlage:{" "}
          <Link to="/offen" className="underline decoration-from-font">
            Kapitel 00c
          </Link>
          .
        </Reco>

        <section className="grid gap-3 sm:grid-cols-3">
          {[
            ["Gegenstand", "Web-App plus souveräner GPU-Kern auf Debian Bookworm für Praxis, Gruppen und Administration."],
            ["Nicht-Gegenstand", "Medizinprodukt, Diagnose, Heilversprechen, Torsionsphysik, Browser-USB, Lovable als Akte, LLM auf der Ada."],
            ["Methode", "Phase 1 Gehäuse. X akzeptiert. Kein Video. Wiedervorlage: Backup und Preise."],
          ].map(([t, b]) => (
            <article key={t} className="rounded-xl border border-border bg-elevated p-5">
              <h2 className="font-display text-xl font-medium">{t}</h2>
              <p className="mt-2 text-sm leading-relaxed text-muted">{b}</p>
            </article>
          ))}
        </section>

        <div>
          <H2>Was feststeht, unabhängig von der Freigabe</H2>
          <div className="mt-5">
            <List
              items={[
                "Host: Ryzen 5 9600X, RTX 4000 SFF Ada 20 GB, 128 GB DDR5, 2×1 TB NVMe, 2×1 Gbit/s.",
                "Zweck: Wellbeing. Kein MDR, kein HWG-Heilspruch.",
                "Art. 9 nur Debian EU. Lovable nicht in der Laufzeit (H1–H3).",
                "Server ist die Uhr. Spooky2 nur über aurelia-emitterd.",
                "Sextett andocken, nicht /opt/radiquant4 kopieren.",
                "Berechnungsausweis mit Quelle und copyguard_digest.",
              ]}
            />
          </div>
        </div>

        <div>
          <H2>Hybrid in einem Blick</H2>
          <P>
            Harte Grenze zwischen öffentlicher Kante und souveränem Kern. Die Ada ist
            Job-Pool, der Wächter sitzt daneben im RAM.
          </P>
          <div className="mt-6">
            <HybridDiagram />
          </div>
        </div>

        <Callout title="Stop-Gates unverändert">
          Nicht schreiben: /opt/radiquant4. Lovable nicht trennen. Keine echte Engine,
          kein USB, kein Publish, kein Build 0 von Null. Nächster fachlicher Slice im
          Altprodukt: Preview-Abnahme, dann read-only RadiMorphic-Intake.
        </Callout>

        <div>
          <H2>Kapitel dieses Konzepts</H2>
          <ul className="mt-5 grid gap-2">
            {NAV.filter((n) => n.href !== "/").map((item) => (
              <li key={item.href}>
                <Link
                  to={item.href}
                  className="flex items-baseline justify-between gap-4 rounded-xl border border-border bg-elevated px-5 py-4 no-underline transition-colors duration-150 hover:bg-surface"
                >
                  <span>
                    <span className="font-mono text-xs text-subtle">{item.chapter}</span>
                    <span className="ml-3 font-medium text-fg">{item.label}</span>
                  </span>
                  <span className="hidden text-sm text-muted sm:inline">{item.blurb}</span>
                </Link>
              </li>
            ))}
          </ul>
        </div>

        <Cards
          items={[
            {
              kicker: "Jetzt",
              title: "Phase 1 Gehäuse",
              body: "Anmelden, Mandant anlegen, Isolationstest. Keine Klientenakten, keine CUDA, kein USB, kein Video.",
            },
            {
              kicker: "Timer",
              title: "Uhr auf der Platte",
              body: "Viele virtuelle Kanäle pro Klient. Postgres überlebt den Reset. Die Ada rechnet DSP, speichert keine Zeit.",
            },
          ]}
        />
      </Stack>
    </ConceptShell>
  );
}

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
          lead="AURELIA bleibt Wellbeing-Software auf GPU Server M G1. Die Phase-1-Schale mit Authentifizierung, Datenbank und Mandantenbasis ist technisch vorhanden; ausschließlich synthetische Daten. Produktarbeit bleibt bis G0-SRV-12 pausiert."
        />

        <Reco>
          C01–C12 sind gesetzt, X01–X20 sind akzeptiert. Die technische Schale
          bleibt bis G0-SRV-12 ohne weitere Produktarbeit. Wiedervorlage:{" "}
          <Link to="/offen" className="underline decoration-from-font">
            Kapitel 00c
          </Link>
          .
        </Reco>

        <section className="grid gap-3 sm:grid-cols-3">
          {[
            ["Gegenstand", "Web-App plus souveräner GPU-Kern auf Ubuntu Server 24.04.4 LTS amd64 für Praxis, Gruppen und Administration."],
            ["Nicht-Gegenstand", "Medizinprodukt, Diagnose, Heilversprechen, Torsionsphysik, Browser-USB, Lovable als Akte, LLM auf der Ada."],
            ["Methode", "Phase-1-Schale vorhanden; Produktarbeit bis G0-SRV-12 pausiert. X akzeptiert. Video ausgeschlossen."],
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
                "Host: Ryzen 5 9600X, RTX 4000 SFF Ada 20 GB, 128 GB DDR5; geplant 2×2 TB WD_BLACK SN850X mit RAID1/LUKS2/LVM.",
                "Zweck: Wellbeing. Kein MDR, kein HWG-Heilspruch.",
                "Art.-9-Klartext gesperrt; später ausschließlich auf M G1 in der EU. Lovable nicht in der Laufzeit (H1–H3).",
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
          kein USB, kein Publish, kein Build 0 von Null. Vor dem dokumentiert bestandenen
          G0-SRV-12 beginnt keine weitere Produktarbeit und kein Prototypen-Intake.
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
              title: "Phase-1-Schale vorhanden",
              body: "Authentifizierung, Datenbank und Mandantenbasis technisch vorhanden; ausschließlich synthetische Daten. Produktarbeit pausiert bis G0-SRV-12. Kein CUDA, kein USB, kein Art.-9-Klartext.",
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

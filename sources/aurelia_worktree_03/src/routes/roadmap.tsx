import { createFileRoute, Link } from "@tanstack/react-router";
import { ConceptShell } from "@/components/concept/shell";
import { Callout, H2, P, PageHeader, Reco, Stack } from "@/components/concept/ui";

export const Route = createFileRoute("/roadmap")({ component: Page });

const PHASES = [
  {
    id: "0",
    title: "Konzept und Verfassung",
    status: "abgenommen",
    items: [
      "Verfassung, C01–C12, X-Katalog akzeptiert, H1–H3, Kozyrev K1–K5.",
    ],
  },
  {
    id: "1",
    title: "Gehäuse",
    status: "Schale vorhanden · Produktarbeit pausiert bis G0-SRV-12",
    items: [
      "Authentifizierung, Datenbank und Mandantenbasis technisch vorhanden; ausschließlich synthetic.",
      "Produktpfad auf M G1 unter Ubuntu: Passkeys (WV03). Keine weitere Produktarbeit vor G0-SRV-12.",
    ],
  },
  {
    id: "2",
    title: "Praxisorganisation",
    status: "Danach · WV01 Backup-Ort vor Art. 9",
    items: ["Klienten, Gruppen, Dienste, Einwilligungen, Zwischenablage. Nur synthetic bis Grant."],
  },
  {
    id: "3",
    title: "Kernel-ABI und Rate-Katalog",
    status: "Danach",
    items: [
      "Vertrag, Registry, erste gewrappte Prototypen im Labor-Mandanten.",
      "Prototypen-Intake bleibt bis zum dokumentiert bestandenen G0-SRV-12 pausiert.",
    ],
  },
  {
    id: "4",
    title: "Analyse strikt (CPU, dann CUDA)",
    status: "Kern",
    items: ["Passport, CPU-Referenz, erst danach GPU-Hot-Path. Akkuratesse vor Tempo."],
  },
  {
    id: "5",
    title: "Harmonisierung und Timerd",
    status: "Kern",
    items: ["Parallele Timer, Zustandsmaschine, Reboot-Festigkeit, Telemetrie, Emitter-Lease deklarativ."],
  },
  {
    id: "6",
    title: "Archiv, Trend, Report",
    status: "Später",
    items: ["Continuous Aggregates, PDF. WV06 Codecs. Zeugen nie ins CDN."],
  },
  {
    id: "7",
    title: "GPU-Härtung und VRAM-Allocator",
    status: "Später",
    items: ["Budget 2/16/2, Attestation, Queue-Policy zwischen Abo-Stufen."],
  },
  {
    id: "8",
    title: "Quanteninspirierte Kernel",
    status: "Opt-in",
    items: ["cuQuantum/PennyLane hinter ABI, nur Forschung/explizit, nie CopyGuard-VRAM stehlen."],
  },
  {
    id: "9",
    title: "Ausgeschlossene Medienphase",
    status: "gestrichen",
    items: ["O08 / D10: Video, WebRTC, TURN und Aufzeichnung sind vollständig ausgeschlossen."],
  },
  {
    id: "10",
    title: "Abos, Quotas, Betrieb",
    status: "Betrieb · WV02 Preise, WV03 Passkeys, WV05 Mini-VPS",
    items: ["Admin-Stufen scharf, Backup-Restore, TOM. Hardware-Gate erst hier."],
  },
];

function Page() {
  return (
    <ConceptShell>
      <Stack>
        <PageHeader
          chapter="09"
          kicker="Phasenplan"
          title="Qualität vor Menge: ein harter Kern schlägt zwölf Attrappen."
          lead="Jede Phase hat ein Abnahmekriterium. Wir ziehen die nächste nur, wenn die vorige in Produktion ehrlich wäre — auch wenn sie noch klein ist."
        />

        <Reco>
          Phase 0 ist abgenommen. Die Phase-1-Schale ist technisch vorhanden;
          Authentifizierung und Datenbank sind aktiv und verarbeiten ausschließlich
          synthetische Daten. Weitere Produktarbeit und jeder Prototypen-Intake bleiben
          bis zum dokumentiert bestandenen G0-SRV-12 pausiert.
        </Reco>

        <ol className="space-y-3">
          {PHASES.map((phase) => (
            <li
              key={phase.id}
              className="rounded-xl border border-border bg-elevated px-5 py-4 sm:px-6 sm:py-5"
            >
              <div className="flex flex-wrap items-baseline justify-between gap-2">
                <h2 className="font-display text-xl font-medium">
                  <span className="font-mono text-sm text-subtle">Phase {phase.id}</span>
                  <span className="ml-3">{phase.title}</span>
                </h2>
                <p className="text-xs font-medium tracking-[0.14em] text-muted uppercase">
                  {phase.status}
                </p>
              </div>
              <ul className="mt-3 space-y-1">
                {phase.items.map((item) => (
                  <li key={item} className="text-[0.975rem] leading-relaxed text-muted">
                    {item}
                  </li>
                ))}
              </ul>
            </li>
          ))}
        </ol>

        <div>
          <H2>Zwei Schreibziele, eine Zeit</H2>
          <P>
            AURELIA ist die Verfassung dieser Session. radiquant-cloud-build bleibt das
            bisherige Produkt mit Build 0 (65868a6, 151 Tests). Ein Writer pro
            Zeitfenster. Lovable bleibt am Cloud-Build-Repo. Wer später den Produktcode
            anfasst, liest zuerst Kapitel 11 dort — nicht diese Seite als Ersatz.
          </P>
        </div>

        <div>
          <H2>Abnahme je Phase</H2>
          <P>
            Build und Typen grün, echte Bildschirmprüfung, keine Konsolenfehler,
            Kontrast und Tastatur, leere Zustände. Für Compute-Phasen zusätzlich:
            Replay-Test des Ausweises, Isolationstest über zwei Mandanten, CopyGuard
            fail-closed gegen ein Heilsatz-Korpus.
          </P>
        </div>

        <Callout title="Ihre Rolle">
          Gesetzte Karten in{" "}
          <Link to="/entscheidungen" className="underline decoration-from-font">
            Kapitel 10
          </Link>{" "}
          bleiben verbindlich. D08, D10 und D12 sind gesetzt; ausschließlich D09
          und D11 bleiben empfohlen und werden später wiedervorgelegt. Ein neuer
          Phasenschritt braucht erst G0-SRV-12 und danach eine eigene Freigabe.
        </Callout>
      </Stack>
    </ConceptShell>
  );
}

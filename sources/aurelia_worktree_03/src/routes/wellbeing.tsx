import { createFileRoute, Link } from "@tanstack/react-router";
import { ConceptShell } from "@/components/concept/shell";
import { Callout, Cards, H2, List, P, PageHeader, Reco, Stack } from "@/components/concept/ui";

export const Route = createFileRoute("/wellbeing")({ component: Page });

function Page() {
  return (
    <ConceptShell>
      <Stack>
        <PageHeader
          chapter="07b"
          kicker="Wellbeing"
          title="Der Wächter bleibt an. Er rutscht von der Ada in den RAM."
          lead="CopyGuard prüft weiter jeden Satz — UI, Analyse, Zwischenablage, Harmonisierung, Report, Katalog. Nur der Ort ändert sich: DDR5 plus NVMe, nicht VRAM. C02 und D13 sind gesetzt."
        />

        <Reco>
          Lexikon fail-closed, dann Phi-4-mini Q4 oder Gemma 3 4B Q4 im RAM, Gewichte
          mmap von NVMe, Replica auf der zweiten Platte. CPU-Fallback Gemma 3 1B.
          Kein Cloud-LLM, kein CUDA-Resident.
        </Reco>

        <div>
          <H2>Rechtsrahmen</H2>
          <div className="mt-4">
            <List
              items={[
                "Keine medizinische Zweckbestimmung (MDR bleibt aus).",
                "HWG: keine Werbung mit Krankheitsbehandlung.",
                "UWG / EEAT: keine unverifizierbaren Wirkclaims, keine Torsionsfeld-Nachweise.",
                "Zwischenablage und Klienten-Edits laufen durch dasselbe Gate.",
                "Art. 9 bleibt relevant, sobald echte Zeugen existieren — bis dahin synthetisch.",
              ]}
            />
          </div>
        </div>

        <div>
          <H2>Warum RAM, warum schmal</H2>
          <P>
            Die Ada ist für parallele Echtzeitjobs da. Ein residenter Wächter auf
            VRAM würde genau diese Jobs verdrängen. 128 GB DDR5 tragen 4B Q4 mühelos.
            Redundanz heißt: Gewichte auf beiden NVMe, eine Runtime, Fallback 1B wenn
            die große Instanz stirbt — nicht zwei heiße 4B-Prozesse (U07).
          </P>
        </div>

        <div>
          <H2>Gates</H2>
          <div className="mt-5">
            <Cards
              items={[
                {
                  title: "allow",
                  body: "Text ist wellbeingsicher. Digest in den Passport und in den Draft.",
                },
                {
                  title: "rewrite",
                  body: "Heilsversprechen entfernt, Neutralfassung vorgeschlagen, Mensch bestätigt.",
                },
                {
                  title: "block",
                  body: "Nicht speichern, nicht promoten, nicht drucken. reason_code auditiert.",
                },
              ]}
            />
          </div>
        </div>

        <Callout title="Alte Engines und Kozyrev-Anhänge">
          Radi144 (bio_knowledge) und beide Kozyrev-Dokumente enthalten Heilsprache.
          CopyGuard sitzt vor Re-Export und vor der Zwischenablage. Details:{" "}
          <Link to="/kozyrev" className="underline decoration-from-font">
            Kapitel 05b
          </Link>
          .
        </Callout>
      </Stack>
    </ConceptShell>
  );
}

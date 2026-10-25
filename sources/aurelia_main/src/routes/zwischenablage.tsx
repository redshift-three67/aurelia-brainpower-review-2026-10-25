import { createFileRoute } from "@tanstack/react-router";
import { ConceptShell } from "@/components/concept/shell";
import { Callout, Cards, H2, List, P, PageHeader, Reco, Spec, Stack } from "@/components/concept/ui";
import { ClipboardDiagram } from "@/components/concept/diagrams";

export const Route = createFileRoute("/zwischenablage")({ component: Page });

function Page() {
  return (
    <ConceptShell>
      <Stack>
        <PageHeader
          chapter="04b"
          kicker="Zwischenablage"
          title="Erst ablegen. Dann anpassen. Dann erst die Spur."
          lead="Module reichen sich Artefakte über eine klientenbezogene Zwischenablage. Harmonisierung startet nie aus einem Rohscan. C06, C07, C12 sind gesetzt. Viele parallele Spuren: Kapitel 03c."
        />

        <Reco>
          AnalysisDraft ist der einzige Speicher zwischen den Kernen. Promote durch
          die Praktikerin, CopyGuard vorher, Spur danach. Start, Pause, Stop,
          Archiv, Löschen sind Serverbefehle mit ACK über den WebSocket.
        </Reco>

        <ClipboardDiagram />

        <div>
          <H2>Zustände</H2>
          <div className="mt-5">
            <Spec
              rows={[
                ["draft", "Analyse liegt. Praktiker sieht alles, Klient nur freigegebene Felder."],
                ["client_review", "Klient darf die freigegebenen Felder ändern. CopyGuard bei jedem Speichern."],
                ["ready", "Promote erlaubt. Step-up später (D08)."],
                ["promoted", "Unveränderliche Referenz in der HarmonizationLane. Draft bleibt lesbar."],
                ["discarded", "Nicht in der Spur. Audit bleibt."],
              ]}
            />
          </div>
        </div>

        <div>
          <H2>Harmonisierungsspur</H2>
          <P>
            queued → armed → running ⇄ paused → stopped → archived | deleted. Zeitquelle:
            aurelia-timerd. Mehrere Spuren parallel je Mandant, bis zur Quota. Der
            Generator ist davon unabhängig und bleibt exklusiv.
          </P>
          <div className="mt-4">
            <List
              items={[
                "Start, Pause, Stop, Archiv, Löschen: autorisierter Command, Server-ACK, Zustand in Postgres.",
                "Zeitgesteuert: Fenster und Pflichtzyklus sind Parameter der Spur, nicht der Browser-Tab.",
                "Parallel: Kanäle isoliert, tenant_id auf jedem Tick.",
                "WebSocket liefert Ticks und ACK, nicht die Autorität.",
                "Kein stiller Copy aus der Zwischenablage. Promote ist der Schnitt.",
              ]}
            />
          </div>
        </div>

        <Cards
          items={[
            {
              title: "Was der Klient darf (Vorschlag C12)",
              body: "Nur Felder in client_editable_fields. Kein Kernel-Wechsel, kein Passport-Rewrite, kein Emitter-Arming.",
            },
            {
              title: "Was der Klient nicht darf",
              body: "Rolle client bleibt fail-closed für Akten, fremde Mandanten, GPU-Jobs und Generator. D04 gilt.",
            },
          ]}
        />

        <Callout title="TTL (U10, Default)">
          Sieben Tage in draft/client_review, dann Archiv-Vorschlag an die Praktikerin.
          Kein Auto-Delete von Klientendaten. Löschen ist ein Job mit Protokoll.
        </Callout>
      </Stack>
    </ConceptShell>
  );
}

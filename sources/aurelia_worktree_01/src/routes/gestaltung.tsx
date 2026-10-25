import { createFileRoute } from "@tanstack/react-router";
import { ConceptShell } from "@/components/concept/shell";
import { Callout, Cards, H2, List, PageHeader, Reco, Spec, Stack } from "@/components/concept/ui";

export const Route = createFileRoute("/gestaltung")({ component: Page });

function Page() {
  return (
    <ConceptShell>
      <Stack>
        <PageHeader
          chapter="08"
          kicker="Gestaltung"
          title="Heilsam ist ruhig, lesbar und ehrlich — nicht gold und Glow."
          lead="Die Oberfläche dieses Konzepts ist bereits das Design-Versprechen: warmes Papier, tiefes Sage, serifenbetonte Ruhe, WCAG 2.2 AA, BFSG, keine Heilästhetik aus dem Baukasten. Live-Symbole und Audio folgen derselben Ruhe."
        />

        <Reco>
          Ein Design-System von Phase 1 an. Derselbe Satz Tokens für Website und App.
          Barrierefreiheit ist Abnahmekriterium, nicht Politur. 44-px-Ziele, eine Spalte
          auf dem Handy, kein Overflow, reduced-motion ohne Stroboskop.
        </Reco>

        <div>
          <H2>Visuelle Verfassung</H2>
          <div className="mt-5">
            <Spec
              rows={[
                ["Flächen", "Pergament #F3EFE6, Erhebung #FAF7F0, Tinte #1C241E."],
                ["Akzent", "Sage #2C4A3E — ein Ton, sparsam, für Handlungen und Fokus."],
                ["Schrift", "Fraunces für Titel (editorial), Source Sans 3 für Körper (Screen, AA). Selbst gehostet."],
                ["Bewegung", "150–250 ms, opacity und transform. prefers-reduced-motion: statische Frames, kein Tick-Stroboskop."],
                ["Radien", "Konzentrisch. Karten größer als Knöpfe."],
                ["Live", "SVG/Canvas für Symbole, Opus für Cues, WebSocket für Ticks. Keine PNG-Folien."],
                ["Verbot", "Lila-Nebel, Neon, Emoji als Icon, Heilsversprechen als Headline."],
              ]}
            />
          </div>
        </div>

        <div>
          <H2>EEAT in der Oberfläche</H2>
          <div className="mt-4">
            <List
              items={[
                "Wer betreibt das System, steht im Footer und auf einer Personen-Seite.",
                "Was die Software nicht ist, steht in jeder Sitzung, nicht nur in den AGB.",
                "Autoren von Methoden-Texten sind benannt.",
                "Kernel-Version, Ausweis und CopyGuard-Stempel sind für den Praktiker sichtbar.",
                "Marketingseiten und App-Akte teilen keine irreführenden Claims.",
                "Jede Zahl trägt eine Quelle: simulated / measured / derived / manual / ai-generated.",
              ]}
            />
          </div>
        </div>

        <div>
          <H2>Barrierefreiheit und Mobile</H2>
          <div className="mt-5">
            <Cards
              items={[
                {
                  title: "Bedienung",
                  body: "Tastaturpfade, sichtbarer Fokus, 44-px-Ziele, Skip-Link, sinnvolle Überschriften-Hierarchie. Eine Spalte unter 640 px.",
                },
                {
                  title: "Wahrnehmung",
                  body: "Kontrast AA, High-Contrast-Option, Text statt Farbe allein, keine blinkenden Harmonisierungseffekte.",
                },
                {
                  title: "Sprache",
                  body: "Deutsche UI, klare Sätze, keine esoterischen Neologismen ohne Glossar. Klienten-Ansicht in Alltagssprache. CopyGuard vor Veröffentlichung.",
                },
                {
                  title: "Ruhe und Wischen",
                  body: "Wenig gleichzeitige Animation. Timer-Ticks ohne Stroboskop. Sound nur nach Opt-in. Sitzungsende leert Object-URLs, Cache API und IndexedDB.",
                },
              ]}
            />
          </div>
        </div>

        <Callout title="Website und App">
          Die öffentliche Website ist Teil des Produkts: Leistung, Grenzen, Rechtstexte,
          Preise der Stufen, Kontakt. Core Web Vitals und mobile Lesbarkeit sind
          Abnahme. Kein Cookie-Wall für essenziellen Betrieb. Service Worker in Phase
          0/1 aus — wie Build 0.
        </Callout>
      </Stack>
    </ConceptShell>
  );
}

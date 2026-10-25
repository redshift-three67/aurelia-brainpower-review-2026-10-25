import { createFileRoute } from "@tanstack/react-router";
import { ConceptShell } from "@/components/concept/shell";
import { Callout, Cards, H2, List, P, PageHeader, Reco, Spec, Stack } from "@/components/concept/ui";

export const Route = createFileRoute("/module")({ component: Page });

function Page() {
  return (
    <ConceptShell>
      <Stack>
        <PageHeader
          chapter="05"
          kicker="Fachmodule"
          title="Module sind Verträge. Prototypen werden Kernel."
          lead="Die radionische Substanz existiert. Wir gießen sie nicht neu in Marketingnamen, sondern hinter eine ABI, die Version, Hash, Budget, CopyGuard und Reproduzierbarkeit erzwingt."
        />

        <Reco>
          Kernel-ABI v1 zuerst. Kanonisches Sextett andocken, nicht kopieren.
          Laufzeit Full: 144 → Works → Morphic → Blohm → Thoms → Copen. Migration:
          Morphic zuerst. Schreibziel der Cores ist die ABI, nicht /opt/radiquant4.
        </Reco>

        <Spec
          rows={[
            ["id + SemVer", "Stabiler Name, kein stilles Überschreiben."],
            ["hash", "SHA-256 des Kernel-Artefakts. Steht im Passport."],
            ["schemas", "JSON-Schema für Eingabe und Ausgabe."],
            ["class", "cpu | cuda | quantum"],
            ["repro", "strict | seeded | stochastic"],
            ["budget", "vram_mb, cpu_ms_est, max_batch — muss ins 12-GB-Jobfenster passen."],
            ["entry", "Python-Modul oder WASM. Keine versteckten Netzaufrufe."],
            ["copy", "Jeder menschenlesbare String durch CopyGuard im RAM, bevor er die UI, die Zwischenablage oder ein PDF erreicht."],
          ]}
        />

        <div>
          <H2>Sextett (Referenz, nicht Merge)</H2>
          <div className="mt-4">
            <List
              items={[
                "Radi144 — bio_knowledge und Reportpfade: CopyGuard-Risiko, deshalb Wächter vor Re-Export.",
                "RadiWorks — Werkbank, folgt 144 in der Full-Sitzung.",
                "RadiMorphic — nächster read-only Intake (/opt/Prototypen/Radimorphic @ 217dcf9).",
                "RadiBlohm, RadiThoms, RadiCopen — Rest der Full-Kette, nach Morphic.",
                "Kozyrev-DSP sind Kernel hinter derselben ABI (Kapitel 05b), kein siebtes Marketingmodul ohne Vertrag.",
                "Code aus redshift-three67/radiquant4 (main cd9e9b4f) nur als Vertrag/Muster. Workflows A/B/C bleiben deklarativ (executable: false), bis WorkflowPort steht.",
              ]}
            />
          </div>
        </div>

        <div>
          <H2>Modulkarte</H2>
          <div className="mt-5">
            <Cards
              items={[
                {
                  kicker: "Zeuge",
                  title: "Witness Vault",
                  body: "Foto, Zeichen, Textanker — verschlüsselt, komprimiert, mit perceptual hash nur intern. Niemals im öffentlichen CDN, niemals im Disk-Cache des Browsers.",
                },
                {
                  kicker: "Katalog",
                  title: "Rate Library",
                  body: "Klassische und mandanteneigene Raten, ltree, Freigabe je Gruppe. Import läuft durch CopyGuard. Änderungen erzeugen Versionen.",
                },
                {
                  kicker: "Analyse",
                  title: "Scan Engine",
                  body: "Mehrdimensionaler Lauf über gewählte Achsen. CUDA-Default, CPU-Fallback. Ergebnis plus Passport plus CopyGuard-Stempel.",
                },
                {
                  kicker: "Harmonisierung",
                  title: "Field Scheduler",
                  body: "Parallele Kanäle, Kurven, Start/Stopp mit Step-up-Auth. Timerd ist Autorität. Emitter-Lease getrennt vom GPU-Job.",
                },
                {
                  kicker: "Protokoll",
                  title: "Session Graph",
                  body: "Eine Sitzung verbindet Zeuge, Scans, Harmonisierung, Notizen, Report. Graph, kein Haufen Dateien.",
                },
                {
                  kicker: "Dienste",
                  title: "Practice Ops",
                  body: "Termine, Kontingente, Erinnerungen, Rechnungsvorbereitung — klar getrennt von der Modellrechnung.",
                },
              ]}
            />
          </div>
        </div>

        <div>
          <H2>Analyse- und Harmonisierungslogik</H2>
          <P>
            Die Logik muss schnell sein, aber vor allem wiederholt denselben Weg gehen.
            Deshalb: feste Pipeline-Schritte, keine versteckte Heuristik in der UI,
            Fusion erst nach den Kernels, menschliche Interpretation als eigene,
            gekennzeichnete Schicht (Notiz des Praktikers, nicht „Befund der KI“).
          </P>
          <div className="mt-4">
            <List
              items={[
                "Eingaben validieren gegen das Kernel-Schema — sonst kein Start.",
                "Budget reservieren oder ablehnen (12 GB Jobs, CopyGuard bleibt sitzen).",
                "Kerne isoliert ausführen, Zwischenwerte nur intern.",
                "Fusion schreibt Maße plus Unsicherheit, wenn der Kernel sie liefert.",
                "CopyGuard über Kommentar, Report und Katalog — allow / rewrite / block.",
                "Praktiker-Kommentar ist Autorentext, nicht Modelloutput.",
                "Harmonisierung startet nur mit gültigem Scan oder bewusstem Override (auditiert).",
              ]}
            />
          </div>
        </div>

        <Callout title="Innovation, die trägt">
          Der Berechnungsausweis ist das eigentliche neue Artefakt: er macht radionische
          Arbeit zitierbar, vergleichbar und archivfest. Dazu ein Labor-Mandant, in dem
          Prototypen leben dürfen, ohne Produktionsarchive zu vergiften. Build 0 nicht
          von Null wiederholen.
        </Callout>
      </Stack>
    </ConceptShell>
  );
}

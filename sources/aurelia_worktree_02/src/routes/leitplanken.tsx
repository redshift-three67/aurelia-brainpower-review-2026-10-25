import { createFileRoute } from "@tanstack/react-router";
import { ConceptShell } from "@/components/concept/shell";
import { Callout, Cards, H2, List, P, PageHeader, Reco, Spec, Stack } from "@/components/concept/ui";

export const Route = createFileRoute("/leitplanken")({ component: Page });

function Page() {
  return (
    <ConceptShell>
      <Stack>
        <PageHeader
          chapter="01"
          kicker="Leitplanken"
          title="Authentisch heißt: sagbar, prüfbar, begrenzt."
          lead="EEAT, DSGVO und ein heilsames Produkt vertragen keine Überhöhung. Radionik wird hier als dokumentierte, modellbasierte Wellbeing-Praxis geführt — nicht als Physikbeweis, nicht als Heilkundeersatz, nicht als Medizinprodukt."
        />

        <Reco>
          AURELIA ist Wellbeing- und Organisationssoftware für ausgebildete Praktiker.
          Keine Diagnose, keine Therapiezusage, kein MDR-Zweck. Jeder sichtbare Satz
          (UI, Analyse, Harmonisierung, Report, Katalog) läuft durch CopyGuard.
        </Reco>

        <div>
          <H2>Vier Wahrheiten, die das Produkt tragen</H2>
          <div className="mt-5">
            <Cards
              items={[
                {
                  title: "Modell, nicht Magie",
                  body: "Kozyrev- und Quantenmodule sind versionierte Rechenkerne. Sie werden als solche benannt. Physikalische oder klinische Wirkbehauptungen gehören nicht in die UI.",
                },
                {
                  title: "Nachvollziehbarkeit vor Eindruck",
                  body: "Ein Lauf ohne Berechnungsausweis gilt als fehlgeschlagen. Archive speichern Parameter, Kernel-Version und CopyGuard-Digest, nicht nur ein Bild.",
                },
                {
                  title: "Person vor Payload",
                  body: "Klientenakten, Zeugen und Sitzungen sind besondere Kategorien. Jede Funktion fragt zuerst: Rechtsgrundlage, Zweck, Löschung, Auskunft.",
                },
                {
                  title: "Sprache ohne Überhöhung",
                  body: "Keine Wunder, keine Frequenzheilung als Claim, keine erfundenen Studien. Google YMYL, HWG und UWG bestrafen dasselbe Verhalten.",
                },
              ]}
            />
          </div>
        </div>

        <div>
          <H2>Was wir bewusst nicht tun</H2>
          <div className="mt-4">
            <List
              items={[
                "Keine automatische „Diagnose“ aus Fotos, Namen oder Proben.",
                "Keine stillen Lernmodelle auf Klientendaten ohne gesonderte, enge Einwilligung und Opt-out.",
                "Keine Videogespräche in AURELIA; D10 schließt Video und WebRTC aus.",
                "Keine US-Cloud und kein Lovable für Zeugen und Ergebnisse.",
                "Keine Timer, deren Wahrheit im Handy-Tab liegt.",
                "Keine Vermischung von Marketing-Blog und Sitzungsakte.",
                "Kein Cloud-LLM über Akten-Copy — CopyGuard bleibt lokal.",
              ]}
            />
          </div>
        </div>

        <Spec
          rows={[
            ["Zweckbindung", "Praxisorganisation, modellbasierte Analyse, gesteuerte Harmonisierung, Dokumentation — Wellbeing, nicht Heilkunde."],
            ["Zielgruppe", "Therapeutinnen/Praktiker, Assistenz, Klientinnen mit Freigabe, Mandanten-Admins, Plattform-Admins."],
            ["Nicht-Zielgruppe", "Laien-Selbstbehandlung schwerer Erkrankungen, klinische Entscheidungsunterstützung."],
            ["EEAT-Pflichtseiten", "Impressum, Datenschutz, AGB, Verantwortliche Personen, Methodengrenzen, Barrierefreiheit."],
            ["Kennzeichnung in der UI", "Dauerhaft sichtbarer Hinweis: kein Medizinprodukt, kein Ersatz ärztlicher Leistung."],
            ["CopyGuard", "Lexikon fail-closed plus Phi-4-mini lokal. allow / rewrite / block vor jeder Veröffentlichung."],
          ]}
        />

        <Callout title="Google-Richtlinien, konkret">
          <P>
            Hilfreiche Inhalte, Experience, Expertise, Authoritativeness, Trust. Für
            Gesundheitsnähe gilt: Autorenschaft benennen, Grenzen sagen, keine
            unverifizierbaren Wirksamkeitsclaims, Core Web Vitals, Mobiltauglichkeit,
            HTTPS, klare Navigation. Structured Data nur als Organization und
            SoftwareApplication — niemals als MedicalTherapy.
          </P>
        </Callout>
      </Stack>
    </ConceptShell>
  );
}

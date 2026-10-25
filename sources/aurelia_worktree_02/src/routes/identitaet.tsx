import { createFileRoute } from "@tanstack/react-router";
import { ConceptShell } from "@/components/concept/shell";
import { Callout, Cards, H2, List, P, PageHeader, Reco, Spec, Stack } from "@/components/concept/ui";

export const Route = createFileRoute("/identitaet")({ component: Page });

function Page() {
  return (
    <ConceptShell>
      <Stack>
        <PageHeader
          chapter="06"
          kicker="Mandanten & Rollen"
          title="Mehrbenutzer ist kein Feature — es ist Isolation."
          lead="Mandanten, Gruppen, Therapeuten, Klienten und Abos teilen Hardware, niemals Akten. Quotas schützen die 20 GB VRAM vor Höflichkeit."
        />

        <Reco>
          Phase 1: Anmeldung in der Vorschau per E-Mail/Passwort. Auf Debian
          Passkeys plus TOTP. Kein Social-Login als Produktpfad. Kein Video.
        </Reco>

        <div>
          <H2>Rollen</H2>
          <div className="mt-5">
            <Cards
              items={[
                {
                  title: "Plattform-Admin",
                  body: "Mandanten anlegen, Abos setzen, Worker-Gesundheit, globale Kernel-Freigabe. Kein stilles Lesen fremder Sitzungsinhalte.",
                },
                {
                  title: "Mandanten-Admin",
                  body: "Nutzer, Gruppen, lokale Raten, Speicher, Löschanträge, Abo-sichtbar aber nicht selbst kaufbar im MVP.",
                },
                {
                  title: "Therapeut",
                  body: "Klienten, Zeugen, Scans, Harmonisierung, Reports im eigenen Scope und in freigegebenen Gruppen.",
                },
                {
                  title: "Assistenz",
                  body: "Organisation, Termine, Aktenvorbereitung. Kein Start von Harmonisierung ohne Step-up des Therapeuten.",
                },
                {
                  title: "Klient",
                  body: "Nur Freigegebenes: Termine, eigene Berichte, Einwilligungen. Keine fremden Raten, kein Worker-Einblick.",
                },
                {
                  title: "System",
                  body: "Worker-Identität. Kein Mensch. Engste Rechte, attestierte Keys.",
                },
              ]}
            />
          </div>
        </div>

        <div>
          <H2>Gruppen und Klienten</H2>
          <P>
            Gruppen leben innerhalb eines Mandanten (Praxisgemeinschaft, Supervisionskreis,
            Forschungscohort). Freigaben sind explizit, zeitlich begrenzt und auditiert.
            Klientenakten haben einen Verantwortlichen. Vertretung ist delegierbar, nicht
            ererbbar über die URL.
          </P>
        </div>

        <div>
          <H2>Abo-Stufen (Admin)</H2>
          <div className="mt-5">
            <Spec
              rows={[
                ["Orientierung", "1 Nutzer, CPU-only, kleines Archiv, keine parallelen Timer. Zum Kennenlernen der Gehäuse-Logik."],
                ["Praxis", "Team, 1 GPU-Job, 2 Timer-Kanäle, Zeugen-Vault, Reports."],
                ["Gruppe", "Mehrere Therapeuten, 2 GPU-Jobs, Gruppenfreigaben, mehr Speicher."],
                ["Forschung", "Stochastische Ensembles, API-Export, Labor-Kernel, höhere Queue-Priorität — nie auf Kosten laufender Praxis-Jobs ohne Policy."],
              ]}
            />
          </div>
        </div>

        <div>
          <H2>Administration</H2>
          <div className="mt-4">
            <List
              items={[
                "Mandant anlegen, sperren, exportieren, löschen (mit Karenz).",
                "Abo setzen, Quota überschreiben nur mit Begründung im Audit.",
                "Kernel global oder mandantweise freigeben.",
                "Störung: Worker drain, Queue pause, Wartungstext in der UI.",
                "Auskunfts- und Löschjobs im Auftrag des Mandanten anstoßen.",
              ]}
            />
          </div>
        </div>

        <Callout title="Step-up">
          Harmonisierung starten, Zeugen löschen, Mandant exportieren: frische
          Authentifizierung. Eine offene Praxissitzung am Empfang darf das nicht
          aus Versehen auslösen.
        </Callout>
      </Stack>
    </ConceptShell>
  );
}

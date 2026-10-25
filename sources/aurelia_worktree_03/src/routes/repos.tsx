import { createFileRoute } from "@tanstack/react-router";
import { ConceptShell } from "@/components/concept/shell";
import { Callout, H2, List, P, PageHeader, Reco, Spec, Stack } from "@/components/concept/ui";

export const Route = createFileRoute("/repos")({ component: Page });

function Page() {
  return (
    <ConceptShell>
      <Stack>
        <PageHeader
          chapter="02b"
          kicker="Repo-Matrix"
          title="Drei Bäume. Der Codename ‚radiquant4‘ ist eine Falle."
          lead="Kapitel 11 vom 23. August 2026 bleibt verbindlich für den Altstand. Diese Session schreibt nur AURELIA. WinSCP an Ihren Root-Server ist von hier aus nicht möglich."
        />

        <Reco>
          Nicht schreiben: /opt/radiquant4 und GitHub redshift-three67/radiquant4.
          Lovable nicht disconnecten. Kein Force-Push auf Branch radiquant4.
          AURELIA ist die Verfassung dieser Session, nicht ein stiller Ersatz des Cloud-Build-Codes.
        </Reco>

        <Spec
          rows={[
            [
              "AURELIA",
              "github.com/redshift-three67/aurelia · diese Session · Konzept + D01–D24 · einziges Schreibziel",
            ],
            [
              "Cloud-Build (Produkt bisher)",
              "github.com/redshift-three67/radiquant-cloud-build · Branch radiquant4 · Git-HEAD 7dae98e (nur Doku) · src/ seit 5b51b29 unverändert · Build 0 in 65868a6 · 151 Tests · Lovable-Sync",
            ],
            [
              "Alte Plattform (Referenz)",
              "github.com/redshift-three67/radiquant4 · main cd9e9b4f · lokal /opt/radiquant4 · FastAPI + Astro + 6 Python-Engines · nur lesen",
            ],
            [
              "Lovable",
              "Projekt ccecde78-712c-4d23-a30f-437719c6dec6 · an Cloud-Build angebunden · Control-Plane nicht umgesetzt · Publish nie",
            ],
            [
              "Prototyp Morphic",
              "/opt/Prototypen/Radimorphic @ 217dcf9 · historische read-only Referenz · kein Merge; Intake vor G0-SRV-12 pausiert",
            ],
            [
              "Existiert nicht",
              "redshift-three67/redshift-cloud-build",
            ],
          ]}
        />

        <div>
          <H2>SHA-Kette, die man nicht vermischen darf</H2>
          <P>
            Kapitel 11 erfasst den Produktbaum bei 5b51b29. Nachgelagerte
            Status-Commits dürfen HEAD verschieben, solange git diff 5b51b29..HEAD -- src
            leer bleibt. Live 23. August 2026: das gilt für 7dae98e.
          </P>
          <div className="mt-5">
            <Spec
              rows={[
                ["5ec72e1", "2026-08-05 · M7-Handover / letzte belegte Lovable-Preview"],
                ["9d33fb8", "2026-08-22 · Konsolidierungsplan, nur Markdown"],
                ["65868a6", "2026-08-22 · Build 0 Code: Workflows A/B/C executable:false, Hardware deklarativ"],
                ["5b51b29", "2026-08-23 · Erfassungs-HEAD, src/ unverändert seitdem"],
                ["7dae98e", "2026-08-23 · aktueller Git-HEAD, nur Status-Doku"],
                ["cd9e9b4f", "2026-07-18 · altes Repo radiquant4 /opt/radiquant4, nur lesen"],
              ]}
            />
          </div>
        </div>

        <div>
          <H2>Was der Altstand bereits im Code hat — und was nicht</H2>
          <P>
            Foundation plus synthetischer RadiMorphic-Gateway (Tests) plus Build 0:
            Workflows A/B/C mit executable: false, Hardware nur deklarativ, ehrliche Copy.
            Keine echte Engine, keine Hardware, keine Cloud-Persistenz.
          </P>
        </div>

        <div>
          <H2>Stop-Gates (unverändert gültig)</H2>
          <div className="mt-4">
            <List
              items={[
                "Zielpfad /opt/radiquant4 oder Remote radiquant4 als Produkt",
                "Arbeit in alten Worktrees 5ec72e1 / 9d33fb8 als wäre das HEAD",
                "Lovable-Disconnect oder neues Lovable-GitHub-Repo",
                "Publish, echte Daten, echte Engine, USB/GPU aktivieren",
                "Build 0 ein zweites Mal von Null, ohne 65868a6 zu lesen",
                "Zwei Writer parallel auf Branch radiquant4",
              ]}
            />
          </div>
        </div>

        <Callout title="Kein Serverzugriff in K1">
          Diese lokale Kanonkonsolidierung nutzt keinen Serverkonnektor und fordert
          keine Serverbefehle an. Das Zielsystem bleibt M G1 unter Ubuntu Server
          24.04.4 LTS amd64; jeder spätere Intake wartet auf G0-SRV-12 und eine neue,
          ausdrücklich abgegrenzte Freigabe.
        </Callout>
      </Stack>
    </ConceptShell>
  );
}

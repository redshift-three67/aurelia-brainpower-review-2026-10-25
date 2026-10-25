import { createFileRoute } from "@tanstack/react-router";
import { ConceptShell } from "@/components/concept/shell";
import { Callout, DataTable, H2, List, P, PageHeader, Reco, Stack } from "@/components/concept/ui";
import {
  GESETZT_KERNE,
  OFFEN_ERLEDIGT,
  OFFEN_NICHT,
  OFFEN_SPAETER,
  OFFEN_URTEIL,
} from "@/lib/concept/offen";
import { WIEDERVORLAGE } from "@/lib/concept/wiedervorlage";

export const Route = createFileRoute("/offen")({ component: Page });

const HEADERS = ["ID", "Thema", "Lage", "Brauche ich Sie?", "Nächster Schritt"];

function rowsOf(
  list: {
    id: string;
    thema: string;
    lage: string;
    braucheSie: string;
    naechsterSchritt: string;
  }[],
) {
  return list.map((r) => ({
    key: r.id,
    cells: [r.id, r.thema, r.lage, r.braucheSie, r.naechsterSchritt],
  }));
}

function Page() {
  return (
    <ConceptShell>
      <Stack>
        <PageHeader
          chapter="00c"
          kicker="Offen"
          title="X akzeptiert. Phase-1-Schale vorhanden; Produktarbeit pausiert. Was später wiedervorgelegt wird."
          lead={OFFEN_URTEIL.lang}
        />

        <Reco>{OFFEN_URTEIL.kurz}</Reco>

        <div>
          <H2>Erledigt 24. August 2026</H2>
          <div className="mt-5">
            <DataTable caption="Erledigt" headers={HEADERS} rows={rowsOf(OFFEN_ERLEDIGT)} />
          </div>
        </div>

        <div>
          <H2>Wiedervorlage — an der passenden Phase</H2>
          <P>Keine Entscheidung jetzt. Die Frage kommt, wenn der Slice wirklich ansteht.</P>
          <div className="mt-5">
            <DataTable
              caption="Wiedervorlage"
              headers={["ID", "Thema", "Wann", "Phase", "Frage"]}
              rows={WIEDERVORLAGE.map((r) => ({
                key: r.id,
                cells: [r.id, r.thema, r.wann, r.phase, r.frage],
              }))}
            />
          </div>
        </div>

        <div>
          <H2>Später in der Offenen-Liste</H2>
          <div className="mt-5">
            <DataTable caption="Später" headers={HEADERS} rows={rowsOf(OFFEN_SPAETER)} />
          </div>
        </div>

        <div>
          <H2>Default nein — nur bei Widerspruch</H2>
          <div className="mt-5">
            <DataTable caption="Default nein" headers={HEADERS} rows={rowsOf(OFFEN_NICHT)} />
          </div>
        </div>

        <div>
          <H2>Geschlossener Kern</H2>
          <div className="mt-4">
            <List items={GESETZT_KERNE} />
          </div>
        </div>

        <Callout title="Phase-1-Schale">
          Authentifizierung, Datenbank und Mandantenbasis sind technisch vorhanden;
          ausschließlich synthetische Daten. Weitere Produktarbeit bleibt bis zum
          dokumentiert bestandenen G0-SRV-12 pausiert. Kein CUDA, kein USB und kein
          Art.-9-Klartext.
        </Callout>
      </Stack>
    </ConceptShell>
  );
}

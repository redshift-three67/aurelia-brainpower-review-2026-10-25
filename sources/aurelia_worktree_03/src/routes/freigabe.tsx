import { createFileRoute, Link } from "@tanstack/react-router";
import { ConceptShell } from "@/components/concept/shell";
import { Callout, DataTable, H2, P, PageHeader, Reco, Spec, Stack } from "@/components/concept/ui";
import {
  C_GESETZT,
  U_GESETZT,
  X_KATALOG,
  X_LAGE_DEFINITION,
  X_STATUS,
} from "@/lib/concept/freigabe";

export const Route = createFileRoute("/freigabe")({ component: Page });

function Page() {
  return (
    <ConceptShell>
      <Stack>
        <PageHeader
          chapter="00b"
          kicker="Freigabe"
          title="C gesetzt. X-Katalog akzeptiert. Phase-1-Schale vorhanden."
          lead="Authentifizierung und Datenbank sind aktiv; ausschließlich synthetische Daten. Weitere Produktarbeit bleibt bis zum dokumentiert bestandenen G0-SRV-12 pausiert. Video ist ausgeschlossen."
        />

        <Reco>
          {X_STATUS.satz} Schreibziel weiter nur AURELIA. Die technische Schale
          bleibt bis G0-SRV-12 ohne weitere Produktarbeit.
        </Reco>

        <div>
          <H2>A · C-Punkte, gesetzt 23. August 2026</H2>
          <P>
            Inklusive C05 in der von Ihnen nachgeschärften Form und C04 mit
            innerklientlicher Isolation. Folgeentscheidungen D02, D05, D13, D15,
            D17–D21 sind gesetzt.
          </P>
          <div className="mt-5">
            <DataTable
              caption="Gesetzte C-Punkte"
              headers={["ID", "Thema", "Gesetzter Stand", "Warum"]}
              rows={C_GESETZT.map((r) => ({
                key: r.id,
                cells: [r.id, r.thema, r.vorschlag, r.begruendung],
              }))}
            />
          </div>
        </div>

        <div>
          <H2>B · X-Punkte, akzeptiert {X_STATUS.am}</H2>
          <P>
            „Lage“ war zu knapp. Es gibt genau zwei Kategorien. Das ist die
            Definition, die jede Zeile benutzt. Nichts davon ist still verworfen;
            Widerspruch im Chat mit ID.
          </P>
          <div className="mt-5">
            <Spec
              rows={[
                ["nicht umsetzbar", X_LAGE_DEFINITION["nicht umsetzbar"]],
                ["nicht relevant", X_LAGE_DEFINITION["nicht relevant"]],
              ]}
            />
          </div>
          <div className="mt-5">
            <DataTable
              caption="X-Katalog mit Kategorie und Grund"
              headers={["ID", "Thema", "Kategorie", "Grund"]}
              rows={X_KATALOG.map((r) => ({
                key: r.id,
                cells: [r.id, r.thema, r.kategorie, r.begruendung],
              }))}
            />
          </div>
        </div>

        <div>
          <H2>C · U-Punkte, Empfehlung übernommen</H2>
          <P>
            U01 durch Ihre Timer-Präzisierung, U12 durch den HRV-Ohrclip (kein EEG).
            Die übrigen Defaults haben Sie autorisiert.
          </P>
          <div className="mt-5">
            <DataTable
              caption="Übernommene U-Punkte"
              headers={["ID", "Thema", "Gesetzter Stand", "Warum"]}
              rows={U_GESETZT.map((r) => ({
                key: r.id,
                cells: [r.id, r.thema, r.vorschlag, r.begruendung],
              }))}
            />
          </div>
        </div>

        <Callout title="Wo das im Repo liegt">
          Kanon: <code className="font-mono text-sm">src/lib/concept/freigabe.ts</code>,{" "}
          <code className="font-mono text-sm">docs/20-freigabe.md</code>, Timer:{" "}
          <Link to="/timer" className="underline decoration-from-font">
            Kapitel 03c
          </Link>
          , Entscheidungen:{" "}
          <Link to="/entscheidungen" className="underline decoration-from-font">
            Kapitel 10
          </Link>
          .
        </Callout>
      </Stack>
    </ConceptShell>
  );
}

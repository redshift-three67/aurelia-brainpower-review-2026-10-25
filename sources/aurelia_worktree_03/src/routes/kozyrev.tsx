import { createFileRoute, Link } from "@tanstack/react-router";
import { ConceptShell } from "@/components/concept/shell";
import { Callout, DataTable, H2, List, P, PageHeader, Reco, Stack } from "@/components/concept/ui";
import {
  KOZYREV_GESPERRT,
  KOZYREV_GESETZT,
  KOZYREV_SCHALTER,
  KOZYREV_URTEIL,
} from "@/lib/concept/kozyrev-labor";

export const Route = createFileRoute("/kozyrev")({ component: Page });

function Page() {
  return (
    <ConceptShell>
      <Stack>
        <PageHeader
          chapter="05b"
          kicker="Kozyrev"
          title="K1–K5 gesetzt und schaltbar. K6–K8 gesperrt."
          lead="Zweite Prüfung: Filterbanken und leere Labor-Verträge kippen den Kern nicht. Dafür gibt es administrative Schalter (AND-Kette, fail-closed). Autoencoder, Heilmittel und PPS-als-c2 bekommen bewusst keinen Schalter."
        />

        <Reco>{KOZYREV_URTEIL.lang}</Reco>

        <div>
          <H2>Gesetzt — K1 bis K5</H2>
          <P>
            Default nur bei Haar an. Alles andere aus, bis Platform und Mandant
            zustimmen. Jeder Eintrag ist abschaltbar.
          </P>
          <div className="mt-5">
            <DataTable
              caption="Kozyrev K1–K5 gesetzt"
              headers={["ID", "Stück", "Default", "Schalter", "Braucht", "Destabilisiert?"]}
              rows={KOZYREV_GESETZT.map((r) => ({
                key: r.id,
                cells: [r.id, r.stueck, r.defaultOn, r.schalter, r.braucht, r.destabilisiert],
              }))}
            />
          </div>
        </div>

        <div>
          <H2>Gesperrt — K6 bis K8, kein Schalter</H2>
          <div className="mt-5">
            <DataTable
              caption="Kozyrev K6–K8 gesperrt"
              headers={["ID", "Stück", "Warum gesperrt"]}
              rows={KOZYREV_GESPERRT.map((r) => ({
                key: r.id,
                cells: [r.id, r.stueck, r.destabilisiert],
              }))}
            />
          </div>
        </div>

        <div>
          <H2>Administrative Schalter (D23)</H2>
          <P>
            Kette: Superadmin → Mandant → Sitzung. Fehlendes Flag = aus. Umschalten
            wird auditiert. Gesperrte IDs existieren in der Registry nicht.
          </P>
          <div className="mt-5">
            <DataTable
              caption="Kozyrev-Schalter"
              headers={["ID", "Flag", "Default", "Kette", "Wirkung von aus"]}
              rows={KOZYREV_SCHALTER.map((r) => ({
                key: r.id,
                cells: [r.id, r.key, r.defaultOn, r.kette, r.ausWirkung],
              }))}
            />
          </div>
        </div>

        <div>
          <H2>Labor-Regeln, unverändert hart</H2>
          <div className="mt-4">
            <List
              items={[
                "Quelle im Passport: simulated oder derived — nie measured für c2 oder Torsion.",
                "VRAM-Admit im selben 16-GB-Pool. Labor-Quota darf 0 sein.",
                "CopyGuard fail-closed. Labor schreibt kein Client-PDF.",
                "Kein PyTorch-Schwergewicht im Produktiv-Worker-Image.",
                "lab.* bleibt executable: false, bis ein neues gesetztes Gate das ändert — kein Admin-Override.",
              ]}
            />
          </div>
        </div>

        <Callout title="Lovable und X">
          Lovable entscheiden Sie noch — D03 bleibt Preview, nichts ausgebaut.
          X-Katalog bleibt Ihre Pause. K6–K8 sind im Produktivpfad trotzdem gesperrt.{" "}
          <Link to="/lovable" className="underline decoration-from-font">
            Lovable
          </Link>
          .
        </Callout>
      </Stack>
    </ConceptShell>
  );
}

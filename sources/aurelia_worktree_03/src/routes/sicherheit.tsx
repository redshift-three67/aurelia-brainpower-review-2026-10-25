import { createFileRoute } from "@tanstack/react-router";
import { ConceptShell } from "@/components/concept/shell";
import { Callout, Cards, H2, List, P, PageHeader, Reco, Spec, Stack } from "@/components/concept/ui";

export const Route = createFileRoute("/sicherheit")({ component: Page });

function Page() {
  return (
    <ConceptShell>
      <Stack>
        <PageHeader
          chapter="07"
          kicker="Sicherheit"
          title="E2E und DSGVO sind Architektur, nicht ein Banner."
          lead="TLS reicht nicht für Zeugen. Es gibt kein Video in AURELIA (D10). Kompression ohne Schlüsselgrenze ist nur schnell — nicht sicher."
        />

        <Reco>
          Authentifizierung und Datenbank sind aktiv; verarbeitet werden ausschließlich
          synthetische Daten. Art.-9-Klartext bleibt gesperrt. Envelope Encryption ist
          Zielarchitektur. Video ist ausgeschlossen. Codec-Familien bleiben D11/WV06-
          Wiedervorlage; gesetzt sind no-store und das öffentliche CDN-Verbot.
        </Reco>

        <div>
          <H2>DSGVO-Kern</H2>
          <div className="mt-5">
            <Spec
              rows={[
                ["Rollen", "Sie als Verantwortliche; Hosting auf eigenem Server reduziert Auftragsverarbeitung, löscht sie nicht (Support, Mail, DNS)."],
                ["Art. 9", "Einwilligung (Abs. 2 lit. a) plus — wo einschlägig — Gesundheitsberuf (lit. h). Dokumentiert, widerrufbar, zweckgebunden. Bis dahin nur synthetische dataClass."],
                ["TOM", "LUKS, TLS 1.3, RLS, Least Privilege, Backup-Tests, Patch-Fenster, Sperrkonzepte, CopyGuard-Audit."],
                ["Rechte", "Auskunft, Export, Löschung, Einschränkung als Jobs — nicht als E-Mail-Versprechen."],
                ["Verzeichnis", "Aktuell: Login und synthetische Mandantenbasis. Akte, Scan, Harmonisierung und Report erst nach G0-SRV-12 und eigenem Grant."],
                ["Drittland", "Kein Standardpfad. Fonts selbst gehostet. Analytics nur falls anonym und EU. Kein Cloud-LLM auf Akten-Copy."],
              ]}
            />
          </div>
        </div>

        <div>
          <H2>Ende-zu-Ende, praktikabel</H2>
          <P>
            Volle E2E, bei der selbst der GPU-Worker nie Klartext sieht, würde Analyse
            unmöglich machen. Deshalb gestufte E2E:
          </P>
          <div className="mt-4">
            <List
              items={[
                "Transport: TLS 1.3 überall, intern mTLS.",
                "Ruhe: Envelope Encryption, Tenant-Key, Key-Rotation.",
                "Verarbeitung: Unwrap nur in RAM des attestierten Workers, kein Swap, kein Log der Payload.",
                "Nachrichten Therapeut–Klient: MLS (RFC 9420) — der Server reicht Ciphertexte. Video und WebRTC sind vollständig ausgeschlossen.",
                "Browser: Zeugen nicht im HTTP-Cache, nicht im Cache API, nicht in IndexedDB nach Sitzungsende.",
                "Optional später: clientgehaltene Schlüssel, dann nur lokale Vorverarbeitung — eigener Produktzweig.",
              ]}
            />
          </div>
        </div>

        <div>
          <H2>Kompression und Cache</H2>
          <div className="mt-5">
            <Cards
              items={[
                {
                  title: "Bilder",
                  body: "D11/WV06-Empfehlung: AVIF mit WebP-Fallback; JPEG XL als mögliche Archivoption. Fest gesetzt: Zeugen nicht über öffentliches CDN, UI-Marke mit immutable Hash.",
                },
                {
                  title: "Musik / Ton",
                  body: "D11/WV06-Empfehlung: Opus für Live-Cues, FLAC fürs Archiv. Fest gesetzt: Session-Audio no-store und keine Klarnamen in Metadaten.",
                },
                {
                  title: "Draht",
                  body: "zstd für API-Payloads und WebSocket-Frames, Brotli für HTML/JS, HTTP/2 jetzt, HTTP/3 am Proxy sobald stabil.",
                },
              ]}
            />
          </div>
        </div>

        <Callout title="Kein Video">
          D10 / O08: WebRTC ist nicht im Produkt. Fachkanal bleibt der WebSocket
          für Analyse und Harmonisierung.
        </Callout>
      </Stack>
    </ConceptShell>
  );
}

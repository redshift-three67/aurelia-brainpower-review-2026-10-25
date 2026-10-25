# Herkunft und Repo-Matrix

Verbindlicher Altstand: Kapitel 11 in
`redshift-three67/radiquant-cloud-build`
`docs/architecture/2026-08-23-gesamtstand-vor-naechstem-build.md`

Es existiert **kein** Repo `redshift-three67/redshift-cloud-build`.

## SHA-Unterscheidung (Stand 2026-08-23, live geprüft)

| Ref | Bedeutung | `src/`? |
|---|---|---|
| `7dae98e` | Aktueller Git-HEAD Branch `radiquant4` | Nein (nur Status-Doku nach `5b51b29`) |
| `5b51b29` | Erfassungs-HEAD von Kapitel 11 | Nein gegenüber Build 0; `git diff 5b51b29..HEAD -- src` muss leer bleiben |
| `65868a6` | **Build 0 Code** (Workflows A/B/C `executable: false`, Hardware deklarativ, ehrliche Copy) | Ja |
| `9d33fb8` | Konsolidierungsplan | Nein |
| `5ec72e1` | M7-Handover; letzte **belegte** Lovable-Preview (2026-08-05) | Gateway-Stand, nicht Build 0 |
| `cd9e9b4f` | Altes Repo `radiquant4` / `/opt/radiquant4` `main` | anderes Repository |

151 Tests auf dem Tree, der Build 0 enthält.

| Name | Wirklichkeit | Schreiben |
|---|---|---|
| `aurelia` | Verfassung dieser Grok-Session | Ja, nur hier |
| `radiquant-cloud-build` Branch `radiquant4` | Bisheriges Produkt. TanStack Start, Lovable-Sync. Build 0 im Code | Nicht in dieser Session |
| GitHub `radiquant4` / `/opt/radiquant4` | Alte FastAPI+Astro+6-Engines-Plattform, `main` @ `cd9e9b4f` | **Nein** |
| Lovable `ccecde78-…` | Preview des Cloud-Build, Control-Plane leer | Nicht disconnecten, nicht publizieren |
| `/opt/Prototypen/Radimorphic` @ `217dcf9` | Nächster read-only Intake | Dokument, kein Merge |
| `radimorphic`, `radi144` | Prototyp-Evidenz | Nicht verdrahten |

Codename-Falle: intern heißt das Cloud-Build-Produkt „radiquant4“. Das ist der
**Branch-Name**, nicht das alte GitHub-Repo.

Kapitel 11 sagt: Grok Build darf **nur** das Produkt-Repo schreiben. Diese
Session hat AURELIA als Verfassung angelegt (Auftrag des Betreibers). D16:
kein stiller Ersatz, ein Writer pro Zeitfenster, kein Force-Push auf
`radiquant4`.

## Ist im Cloud-Build (nicht wiederholen)

- Foundation in-memory, synthetischer RadiMorphic-Gateway (Tests)
- Build 0: Workflows A/B/C `executable: false`, Hardware deklarativ, ehrliche Copy
- Keine echte Engine, keine Hardware, keine Cloud-Persistenz, 0 Supabase-Migrationen
- Login ist Navigation, `client` fail-closed, `dataClass` synthetisch

## Stop-Gates

Nicht: `/opt/radiquant4` schreiben, Build 0 von Null, Moduladapter jetzt,
Lovable-Disconnect, Force-Push, Publish, reale Daten, USB/GPU aktivieren,
zwei Writer auf Branch `radiquant4`, Arbeit in Worktrees `5ec72e1` / `9d33fb8`
als wäre das HEAD.

WinSCP/SSH aus der Grok-Build-Umgebung: **nicht verfügbar**. Intake per Upload.

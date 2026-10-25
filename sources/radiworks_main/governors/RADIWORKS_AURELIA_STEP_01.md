# RadiWorks → AURELIA: Integrationsschritt 01

Status: priorisiert; Intake-Gate ausführbar, technische Einbettung weiterhin durch AURELIA-G0 blockiert
Erstellt: 2026-09-11T14:25:53+02:00
Owner: Betreiber / Plattform-Governance
Art: read-only Contract-Intake; keine Modul-Adapter-, Registry-, Laufzeit- oder Quellcodeänderung

## Entscheidung

Der erste zulässige Schritt ist keine technische Einbettung von RadiWorks in AURELIA. Er ist ein hashgebundener, rein dokumentierender Intake: den aktuellen RadiWorks-Contract gegen die AURELIA Kernel-ABI v1 und den Modul-Contract abgleichen und die Abweichungen als unverbindlichen Übergabekandidaten erfassen.

Damit wird der RadiWorks-G0-Contract-Freeze vorbereitet, ohne die laufende RadiWorks-WIP oder die pausierte AURELIA-Phase zu umgehen. Die frühere Planungspriorität „Morphic zuerst“ wurde durch Betreiberentscheidung vom 2026-09-11 als technische Abhängigkeit aufgehoben; RadiWorks ist für die schrittweise AURELIA-Integration priorisiert.

## Warum dieser Schritt zuerst kommt

- RadiWorks ist nur S2/S3 nachweisbar; S4 und S5 sind ausdrücklich nicht zertifiziert.
- Die RadiWorks-Strategie verlangt vor jedem Folge-Gate G0: Contract- und Snapshotfrierung.
- Die aktuelle AURELIA-Verfassung pausiert Produktarbeit am `G0-SRV-GROUND-ZERO` und verbietet explizit, jetzt einen Modul-Adapter zu starten.
- Die aufgehobene Reihenfolge erlaubt RadiWorks-Gates parallel zur Morphic-Planung, ersetzt aber weder AURELIAs `G0-SRV-GROUND-ZERO` noch die zwingenden Contract-, Scope-, CopyGuard- und Freigabegates.
- Der laufende RadiWorks-Arbeitsbaum enthält fachliche WIP und ungetrackte Tests; diese dürfen weder bereinigt noch durch diesen Schritt verändert werden.

## Eingangsquellen, revisionsgebunden

| Quelle | Revision | SHA-256 |
|---|---|---|
| RadiWorks Strategie / Gate-DAG | RadiWorks `866f52146ad212157bfb20c9852714cb307a3b12` | `16e4e51f87540c062a06cd99ddd385bec7bd8657fcd2eef4a2520d849b63c075` |
| RadiWorks Modulbeschreibung | RadiWorks `866f52146ad212157bfb20c9852714cb307a3b12` | `6b6eef5b221dc7ef892d3417352c4334d5698253f5cbc52fb44967f78e2e4813` |
| AURELIA Projektverfassung | AURELIA `8706186af01e10e4253e25abb31bf3577110dae4` | `68be8122f7f6e71fd499e8a8dd49619b4d893b3b0dc8ecd78321806faadbe3b4` |
| AURELIA Kernel-ABI v1 | AURELIA `8706186af01e10e4253e25abb31bf3577110dae4` | `9105cf2a4fc13d068b2bfa8b12aecdf81b799a607cd93afac0fe54fdc8466886` |
| Modul-API-Contract v1 | Modul_Templates `041ae65ee5ff2a7aa4a0cc0a1bd82666e4e3ac04` | `f21ff364e208d1194f5d2f0f33679f7076adbe6b265b2ab14b9ff361e750c8c7` |
| Reifegrade | Modul_Templates `041ae65ee5ff2a7aa4a0cc0a1bd82666e4e3ac04` | `fcde7896030716dba5777369919f2c7bfbe95e26708764ca20bb645cd9e7ea87` |
| RadiWorks-Festlegungen | Modul_Templates `041ae65ee5ff2a7aa4a0cc0a1bd82666e4e3ac04` | `0a722ba8860ca434ca9a3f993faa93ef64686762ddddc207aabdbc3ebec58338` |

Jede Änderung einer Eingangsquelle macht diesen Intake-Kandidaten überholt und verlangt eine neue Hashbindung.

## Arbeitsumfang

1. Aus `GET /manifest` und den vorhandenen lokalen Verträgen eine strukturierte Soll/Ist-Matrix erstellen:
   - ABI-ID und SemVer;
   - Artefakt-Hash;
   - `input_schema` und `output_schema`;
   - Kernelklasse, Reproduzierbarkeit und Ressourcenbudget;
   - REST-Operationen, WebSocket-Umschlag und Fehlerform;
   - Computation Passport inklusive `copyguard_digest`;
   - Scope-Kontext `(tenant_id, client_id, job_id)` für HTTP, WebSocket, Persistenz und in-memory-Zustand;
   - CopyGuard- und Hardware-Nichtaktivierungsgrenzen.
2. Jede Abweichung eindeutig als `erfüllt`, `teilweise`, `offen`, `nicht verifizierbar` oder `durch AURELIA-Gate blockiert` kennzeichnen.
3. Die konkrete Intake-Empfehlung auf einen späteren Betreiber-Admin-Akt beschränken: keine automatische Registry-Aufnahme und keine S4/S5-Behauptung.
4. Den Report gegen alle obigen Hashes sowie gegen den aktuellen Git-Status von RadiWorks, AURELIA und Modul_Templates binden.

## Ausdrückliche Ausschlüsse

- Kein FastAPI-/AURELIA-Serverstart, kein Portzugriff und keine Browser-/Netzwerkprobe.
- Keine Änderung unter `radiworks_port/`, `C:/Users/Hubert111/Documents/ChatGPT/Aurelia/` oder `C:/Users/Hubert111/Documents/Modul_Templates/`.
- Keine Kopie von Runtime-, Case-, Draft-, Entropiejournal-, Screenshot- oder Betreiber-Daten.
- Keine Registry-Registrierung, iframe-/Preview-Host-Einbindung, Auth-Bridge, Datenmigration oder Adaptererstellung.
- Kein Commit, Push, Rebase, Cleanup, Staging oder externe Schattenkopie.
- Kein Zugriff auf `/opt/radiquant4` oder darauf basierende Ableitung.

## Abnahmekriterien

- Der Report enthält eine vollständige Feldmatrix für die Kernel-ABI v1 und jede Matrixzeile verweist auf eine konkrete Quelle.
- Alle Quellen, HEADs und SHA-256-Werte werden vor und nach dem Report identisch verifiziert.
- Der Report behauptet weder S4/S5 noch Runtime-, Auth-, Scope- oder Paritätsnachweise, die nicht ausgeführt wurden.
- Der Report hält fest, dass AURELIA weiterhin an `G0-SRV-GROUND-ZERO` pausiert; dieser externe Infrastrukturblocker begrenzt den Schritt auf Contract-Intake, nicht auf eine Modul-Adapterimplementierung.
- Die RadiWorks-WIP ist unverändert; die Statuspopulation besteht ausschließlich aus der bereits vorhandenen WIP plus diesem Governance-Artefakt.
- Zwei unabhängige, read-only Reviews des exakt hashgebundenen Reports ergeben P0–P3 = 0, bevor ein Folgeschritt vorgeschlagen wird.

## Eintrittsbedingung für Schritt 02

Erst wenn der Intake abgenommen ist und AURELIA `G0-SRV-GROUND-ZERO` akzeptiert wurde, darf ein separater Adapter-/Registry-Plan entworfen werden. Die frühere Morphic-Reihenfolge ist keine Eintrittsbedingung mehr. Dieser Folgeplan benötigt eine neue Freeze- und Review-Runde; Schritt 01 erteilt dafür keine Implementierungsfreigabe.

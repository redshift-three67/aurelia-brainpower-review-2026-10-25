# RadiWorks-Modulreferenzen und lokales Vertragsprofil — Ausführungsplan

> Für die Ausführung: Dieses Dokument ist eine Prüfliste für die laufende Arbeit. Die bestehenden Änderungen im externen `Modul_Templates`-Arbeitsstand bleiben erhalten; der gemeinsame Hostvertrag wird hier nicht freigegeben.

**Ziel:** Die Modul_Templates-Referenzen auf den belegten RadiWorks-Kandidaten `a242d24758d53e86ab290454ae4772f0827acc06` bringen und die noch ungeklärten Unterschiede zum gemeinsamen API-Vertrag als versionierten Entwurf sichtbar machen.

**Ansatz:** RadiWorks-spezifische Ist-Aussagen und Belege werden aktualisiert. Der bisherige gemeinsame v1-Vertrag bleibt als solcher erkennbar; ein additiver v1.1-Entwurf beschreibt die lokale Schnittstelle und die Hostlücken, ohne Aurelia-Autorität zu behaupten. Designreferenzen verweisen auf den geplanten Hermes-Template-Abgleich, ohne die Gestaltung vor D0/D1 umzuschalten.

**Quellen:** RadiWorks-Kandidat, `docs/verification/RADIWORKS_TEMPLATE_DELTA_V01_2026-09-29.md`, `docs/verification/RADIWORKS_RELEASE_BOUNDARY_2026-09-29.md`, `docs/AURELIA_DESIGN_TEMPLATE.md`.

## 1. Vorhandene Arbeit und Quellen fixieren

- [x] `git status --short` und gezielte Diffs unter `C:/Users/Hubert111/Documents/Modul_Templates` gelesen: sechs geänderte Dateien und ein ungetracktes `project_memories/`; nichts davon zurücksetzen.
- [x] RadiWorks-Manifest und `AnalysisRequest` im Kandidaten gegen Template-Delta geprüft: lokaler Analyse-Body ohne frei wählbaren Mandanten-/Klienten-Scope, `job_id` im Draft statt Passport.
- [x] Vor jeder externen Änderung SHA-256 der Ziel-Dateien speichern; bei Abweichung vor dem Schreiben erneut prüfen.

## 2. Vertragsentwurf und Referenzen ergänzen

- [x] `C:/Users/Hubert111/Documents/Modul_Templates/standards/RADIOWORKS_LOCAL_PROFILE_V1_1_DRAFT.md` mit Kandidatenidentität, verifiziertem lokalem Request/Manifest, Scope-Grenze, Direktwegen, WebSocket, offenen Hostentscheidungen und Status „Entwurf“ anlegen.
- [x] `C:/Users/Hubert111/Documents/Modul_Templates/standards/API_CONTRACT.md` und `REIFEGRADE.md` um einen datierten Hinweis auf den noch nicht übernommenen Entwurf ergänzen; keine v1-Zeile stillschweigend als implementiert ausgeben und S4 nicht abhaken.
- [x] `C:/Users/Hubert111/Documents/Modul_Templates/MODULE_REGISTRY.md`, `modules/radiworks/PORT_PLAN.md`, `modules/radiworks/FESTLEGUNGEN.md` und `UEBERGABE_AURELIA.md` auf Kandidat, lokale Nachweise und aktuelle Reihenfolge verweisen lassen; historische Quellbelege bleiben als historische Angaben lesbar.
- [x] `C:/Users/Hubert111/Documents/Modul_Templates/standards/UI_DESIGN_STANDARD.md` auf `Brainpower/docs/AURELIA_DESIGN_TEMPLATE.md` und die offene D0/D1-Abstimmung verweisen lassen; keine ungeprüften neuen Farben/Tokens definieren.
- [x] `README.md` und `standards/MODUL_STANDARD.md` auf aktuellen Kandidaten, Manifestidentität und offene Integrationsgrenze bringen.

## 3. Nachweis und Abschluss

- [x] `git diff --check` im Template-Repository; gezielter Link-/Faktenabgleich gegen Kandidat, Manifest und Brainpower-Berichte.
- [x] Nach SHA-256- und Git-Diff-Vergleich nur die vorgesehenen neuen Änderungen melden; vorhandenes WIP, `project_memories/`, RadiWorks-Produktcode und Aurelia unverändert lassen.
- [x] Dokumentierten S4.6/S4.7/S4.8-Stand nur nach neuen Nachweisen ändern; kein Tag, Release, S4-GO oder Aurelia-Hoststart.

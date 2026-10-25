# Pause und Wiederaufnahme: RadiWorks-Template-Abgleich, 30.09.2026

Lokaler Wiederherstellungspunkt: `checkpoints/Hermes-RadiWorks-20260930-TemplatePause`. Bei normaler Fortsetzung die aktuellen Arbeitsdateien verwenden. Nur bei tatsächlichem Verlust nach Prüfung von `VERIFY.json`, `MANIFEST.json` und `SOURCE_STATE.json` gezielt wiederherstellen.

## Gesicherter Stand und Grenzen

- Der getrennte RadiWorks-Kandidat `codex/radiworks-s46-candidate` steht sauber auf `a242d24758d53e86ab290454ae4772f0827acc06`; 105 Moduldateien waren zuletzt bytegleich mit dem RadiWorks-Arbeitsstand. Die aktuelle Fallaktionsprobe mit synthetischen Daten bestätigte sichtbare Meldungen, unterscheidbare Sprachausgabe, sichtbaren Fokus und keine rohen Fallnamen. Der isolierte Browser-Smoke bestand 19/19. Das ist keine vollständige WCAG-Abnahme.
- Die RadiWorks-spezifischen `Modul_Templates`-Referenzen und das lokale Profil v1.1 als Entwurf sind aktualisiert. Der gemeinsame normative API-Vertrag, D0/D1-Designentscheidungen, Hostautorität und Aurelia-Integration sind offen. Der Abgleich und die unveränderte vorhandene Template-WIP sind in `docs/verification/RADIWORKS_TEMPLATE_SYNC_2026-09-30.md` dokumentiert.
- **S4.6 ca. 98 %, S4.7 ca. 88 %, S4.8 0 %** des begrenzten lokalen Prüfpakets; kein S4-GO, Tag oder Release. Ubuntu Server 24.04.4 LTS als Ziel, G0-SRV-GROUND-ZERO, AUDIT-02, D18 und die spätere Betreiberentscheidung bleiben ausstehend. Radi144 auf Port 8090 wurde für diesen Checkpoint nicht gestoppt; Governor auf 8787 wurde regulär beendet. Keine Modelljobs gestartet und automatische Reviews bleiben aus.
- Der Checkpoint enthält persönliche lokale Quell-/Laufzeitkopien sowie ausgewählte externe Referenzen, keine vollständige Git-Historie und keine unabhängige zweite Backup-Location. Externe Dateien nicht automatisch zurückschreiben. Ein vollständiger App-Wiederanlauf aus dem Checkpoint wird nicht durchgeführt.

## Genau hier weiter

1. `VERIFY.json`, `SOURCE_STATE.json`, diese Pausennotiz und `WIEDERAUFNAHME.md` lesen; aktuellen RadiWorks-/Template-Git-Stand und Ports neu feststellen.
2. Die offenen RadiWorks-S4.6-/S4.7-Nachweise gezielt weiterführen, insbesondere Ziel-Ubuntu-24.04.4 und weitere Bedien-/WCAG-Zustände. Template-v1.1 bleibt bis zur versionierten Hostentscheidung ein Entwurf.
3. S4.8 erst mit Betreiberentscheidung nach vollständiger Evidenz. Danach Radi144 und `morphic_v1` als getrennte Prototypen; Matrixplan und Aurelia-Integration folgen späteren Gates.

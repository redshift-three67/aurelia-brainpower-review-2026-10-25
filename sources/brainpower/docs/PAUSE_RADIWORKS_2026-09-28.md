# Pause und Wiederaufnahme: RadiWorks, 28.09.2026

Persönlicher lokaler Wiederherstellungspunkt: `checkpoints/Hermes-RadiWorks-20260928-Pause`. Bei normaler Fortsetzung die Arbeitsdateien weiterverwenden; nur nach tatsächlichem Verlust gezielt aus dem Checkpoint wiederherstellen. Frühere Quellen- und Planbefunde stehen in `docs/PAUSE_RADIWORKS_2026-09-27.md`.

## Aktueller Stand

- Die quellgebundene Funktionsmatrix `docs/verification/RADIWORKS_FUNKTIONSMATRIX_2026-09-27.md` trennt belegte Originalparität, vorhandene Prototypfunktionen und optionale 2.9.0-Kandidaten. Der AetherOnePi-2.9.0-JAR wurde nicht ausgeführt. Keine physische Hardware-, CUDA-, Kozyrev- oder Aurelia-Integrationsabnahme.
- Im lokalen RadiWorks-Prototyp ist der persistierte Draft-Freigabeauftrag umgesetzt. Promote und Legacy-Mix nutzen eine gemeinsame atomare virtuelle Batch-Übernahme; der Draft wird erst nach erfolgreicher Übernahme `promoted`. Eindeutige Auftrags-ID, Versuchshistorie und Neustartabgleich bleiben erhalten. Unterbrochene Versuche werden angezeigt und nicht automatisch erneut gesendet. Direkter Operator-Broadcast bleibt ein eigener CopyGuard-geschützter Weg. Die direkte Statusabkürzung auf `promoted` ist gesperrt.
- Die vollständige RadiWorks-Engine-Suite, JavaScript-Syntax, `git diff --check` und ein synthetischer Browser-Smoke einschließlich 390-px-Ansicht bestanden nach dem letzten Produkt-Fix. Diese Prüfungen belegen den lokalen virtuellen Pfad, keine Exactly-once-Garantie, keinen echten Hardwarelauf und keine Produktfreigabe. Einzelheiten und Dateihashes stehen im Korrekturabschnitt der Funktionsmatrix.
- Der synthetische RadiWorks-Preview nutzt `127.0.0.1:8101` und ein eigenes Runtime-Home. Die reale Radi144-Instanz auf Port 8090 blieb unberührt. Der Governor auf Port 8787 war vor dem Checkpoint geschlossen; automatische Reviews bleiben aus.
- RadiWorks enthält weiterhin vorhandenen und neuen uncommitteten WIP. Kein Commit, keine Änderung an Aurelia oder Modul_Templates und keine Aktivierung eines Produktgates wurden vorgenommen. Die Route-B-Integrationsaussage des letzten echten Hermes-Reviews blieb BLOCK; die stale-Markierung wurde nicht übergangen.

## Genau hier weiter

1. Checkpoint `VERIFY.json`, diese Notiz und die Funktionsmatrix lesen; aktuellen RadiWorks-Quellstand und Ports neu prüfen. Vorhandenen WIP erhalten. Den Preview bei Bedarf aus dem gesicherten `runtime/radiworks-preview-20260927/preview.py` mit rein synthetischen Daten starten.
2. Im RadiWorks-Prototyp die nächsten offenen Original-/Portpfade begrenzt prüfen: R0-WebSocket-Reconnect und Replay-Fehler im Browser, Fall-/GV-Wiederaufnahme, Bild-/Area-, Stick-Pad- und Peggotty-Parität sowie Quellkennzeichnung für Entropie. Nur belegte Gleichheit behaupten.
3. Für Aurelia den erzwungenen Tenant-Scope und die direkten Broadcast-/Bildwege gegen die aktuellen Modul_Templates-Verträge abgleichen; lokale Funktion und Hostfreigabe getrennt halten. Optionale 2.9.0-Funktionen wie Ego Cleaner erst nach Format-, Lizenz-, Bedien- und Regressionstest einzeln entscheiden.
4. Danach lokale RadiWorks-S4-Abnahme, Radi144, `morphic_v1` und neuer Modulprototyp. Vollständiger Matrixplan und Aurelia-Integration bleiben spätere eigene Schritte nach ihren Gates.

Kein Low-Wechsel offen. Die gewählte Chatroute Sol/high mit bedarfsweiser Luna/max- und Astra/medium-Delegation ist eine Betreiberwahl, kein aus dieser Notiz belegbarer aktiver App-Schalter.

# Radi144: M0-Bestandsaufnahme nach RadiWorks

Stand: 30.09.2026. **Quelle:** `C:\Users\Hubert111\Documents\Radi144`, Branch `main`, HEAD `b8ac33a1360f1cb56f06e602fcd37cbda2a9c641`. Der Arbeitsbaum enthält 27 geänderte Einträge, darunter gelöschte historische Übergabedokumente und zwei vorgemerkte Projektgedächtnisse. Diese Änderungen gehören dem Betreiber und wurden nicht bereinigt. Die bereits laufende Instanz hörte nach dem Test weiterhin auf `127.0.0.1:8090`.

## Belegter lokaler Ausgangspunkt

| Teil | Befund | Aussagegrenze |
| --- | --- | --- |
| Einstieg/Abhängigkeiten | `main.py` bindet zwei FastAPI-Router und liefert `user_workflow.html/.css/.js` aus; `requirements.txt` enthält u. a. FastAPI, PyTorch, NumPy, ReportLab und OpenPyXL. Default `APP_HOST=127.0.0.1`, `APP_PORT=8090`. | Die README nennt an einer Stelle noch 8000. Eine CUDA-fähige Laufzeit oder Hardwarewirkung ist damit nicht belegt. |
| Funktionen | Routen für Matrix-, Sequenz-, Gruppen- und Geoanalyse, DB-Liste/Ranking/Scan, PDF, EMF und Verstärker; eigene Client-/Lösch-/Audit-Routen. EMF besitzt eigene WebSockets `/api/v1/emf/ws` und `/api/v1/emf/client-sensor`. | Funktionsinventar aus Quellrouten, noch keine vollständige fachliche Äquivalenz- oder Sicherheitsprüfung. Der gemeinsame `/ws`-/`/manifest`-Aurelia-Vertrag ist dadurch nicht nachgewiesen. |
| API-Grenze | CORS-Default auf 8090-Loopback; API-Key-Gate wird nur bei gesetztem, nicht beispielhaftem `API_KEY` aktiv. | Lokale Schutzlage ist keine Mandanten-, Client- und Job-Autorität für Aurelia. Bei späterer Hosteinbindung Authentisierung, Rechte, WebSockets, Exporte und Widerruf separat prüfen. |
| Testkopie | 802 Dateien in `Brainpower/runtime/r144-m0-20260930`, ohne `.venv`, Git-Historie und `data/runtime`; vorhandener Projekt-Python-Interpreter. Erster Vollauf: **88 bestanden, 4 fehlgeschlagen**; alle vier Fehler stammten aus `git check-ignore`, weil die Kopie zunächst unter dem übergeordneten Brainpower-Git lag. Nach `git init` in der Kopie: **9/9** Tests der betroffenen Git-Regeldatei bestanden. | Das sind zwei ergänzende Läufe, **kein** einzelner neuer Vollauf mit 92/92. 30 bekannte httpx-TestClient-DeprecationWarnings im ersten Lauf. Keine echte Hardware oder Browser-/Betreiberprobe in diesem Schritt. |

## Nächste begrenzte Schritte

1. M0 mit dem Betreiber auf die konkrete Radi144-Fassung und den gewünschten fachlichen Kernumfang festlegen. Die alte README-Portangabe korrigieren, ohne Port 8090 oder die laufende Instanz zu ändern.
2. Algorithmuspfade, CUDA/CPU-Fallback, Daten- und Exportwege sowie EMF-WebSocket-Zugriffe gegen vorhandene Tests und synthetische Negativfälle prüfen. Fachliche Aussagen über `10^144` oder Hardwarewirkung nur mit gesondertem Nachweis übernehmen.
3. In isoliertem Runtime-Home den UI-Workflow lokal live prüfen; echte Betreiberbedienung und beobachtete Abweichungen separat erfassen. Bestehende Radi144-Daten und 8090 nicht für synthetische Tests verwenden.
4. Danach den Radi144-spezifischen Entwurf gegen `Modul_Templates/standards/API_CONTRACT.md`, `MODUL_STANDARD.md`, `REIFEGRADE.md`, Aurelias D0–D4-Design und G0/AUDIT-02-Gates stellen. `REIFEGRADE.md` weist für Radi144 derzeit noch keine Stufe als belegt aus; lokale Tests ändern das nicht automatisch.

**Phase M0:** 4 von 5 Aufnahmebausteinen (Quelle, Laufzeit, Routenübersicht, synthetische Testbaseline) sind begonnen bzw. belegt; die fachliche Umfangsbestätigung fehlt. Grober Arbeitsstand **ca. 70 %**, keine Modulreife- oder Integrationsfreigabe. Der F:-Sicherungspunkt wurde unmittelbar **vor** dieser Radi144-M0-Probe erstellt und enthält die Radi144-Quellbytes, nicht diesen nachfolgenden Bericht.

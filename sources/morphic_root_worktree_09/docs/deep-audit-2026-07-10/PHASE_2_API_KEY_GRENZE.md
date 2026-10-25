# Phase 2A – API-Key-Grenze: Tatsächlicher Status

**Stand:** 2026-07-10
**Betriebsprofil:** lokaler Einoperator / Loopback

## Code-Echter Befund

`MORPHIC_API_KEY` ist optional. Ist die Variable nicht gesetzt, überspringt `apps/web/security.py:37-52` die Prüfung. Ist sie gesetzt, verlangen nur ausgewählte schreibende Endpunkte `X-API-Key`:

| Endpunktgruppe | API-Key bei gesetzter Variable | Browser-Workbench sendet Header? | Bewertung |
|---|---:|---:|---|
| `POST /api/scan/preview` | ja | nein | Workbench-Preview würde 401 erhalten |
| `POST /api/scan/jobs` | ja | nein | Workbench-Start würde 401 erhalten |
| `POST /api/harmonization/jobs` und `/stop` | ja | nein | Harmonisierung würde 401 erhalten |
| Reports, Privacy-Clients, Jobstatus/-resultate, Workbench-Draft/Template/Trace | überwiegend nein | n/a | kein vollständiger Zugriffsschutz |
| Health, Status, Sources | nein | n/a | im Loopbackmodus technisch vertretbar, kein Netzschutz |

## Verbindliche Aussage

Der optionale Key ist **keine Browser-Loginfunktion, keine Benutzeridentität, keine Rollen- oder Tenant-Autorisierung**. Er darf im Phase-2A-Standardbetrieb nicht als lokale Schutzmaßnahme beworben werden, weil die Workbench keinen sicheren Schlüsseltransport/-speicher besitzt und bei Aktivierung nicht funktionsfähig wäre.

## Konsequenz für Variante A

1. Lokale Workbench: `MORPHIC_API_KEY` standardmäßig **nicht setzen**; Schutzgrenze bleibt Loopback + Windows-Benutzer-/Dateirechte.
2. Maschinenintegration: nur über einen separaten, dokumentierten Client mit kurzlebiger/rotierbarer Credential-Strategie nach eigenem Gate.
3. Netzwerk-/Mehrbenutzerbetrieb: erst Variante B mit IdP, serverseitig abgeleitetem Principal, TLS und Tenant-/Owner-AuthZ.

## Nächster sicherer Schritt

Keine Pseudo-Authentifizierung in den Browser einbauen. Phase 2A konzentriert sich stattdessen auf eine strikte Loopback-/CORS-/Security-Header-Deploymentgrenze und Datenschutzartefakte.

# Identität, Rollen, Abos

## Rollen

| Rolle | Darf | Darf nicht |
|---|---|---|
| Plattform-Admin | Mandanten, Abos, Worker, Kernel-Freigabe | Fremde Sitzungsinhalte still lesen |
| Mandanten-Admin | Nutzer, Gruppen, lokale Raten, Löschanträge | Abo selbst kaufen (MVP) |
| Therapeut | Klienten, Zeugen, Scans, Harmonisierung, Reports im Scope | Fremde Mandanten |
| Assistenz | Organisation, Termine, Aktenvorbereitung | Harmonisierung ohne Step-up |
| Klient | Freigegebenes, eigene Einwilligungen | Raten, Worker, fremde Akten |
| System | Worker-Identität, attestierte Keys | Interaktive Anmeldung |

Gruppen leben **innerhalb** eines Mandanten. Freigaben explizit, befristet, auditiert.

## Login (Phase 1+)

Passkeys (WebAuthn) primär, TOTP Fallback. Kein Social-Login für Fachnutzer.
Alternative später: Keycloak auf Ubuntu für Klinik-OIDC.

Step-up zwingend: Harmonisierung starten, Zeugen löschen, Mandant exportieren.

## Abos (Admin only)

| Stufe | Kernquota |
|---|---|
| Orientierung | 1 Nutzer, CPU-only, kleines Archiv |
| Praxis | Team, 1 GPU-Job, 2 Timer-Kanäle |
| Gruppe | Mehrere Therapeuten, 2 GPU-Jobs, Gruppen |
| Forschung | Stochastische Ensembles, API-Export, Labor-Kernel |

Quotas schützen 20 GB VRAM. Selbstbedienung erst, wenn Kündigungs- und
Löschfristen sitzen.

# REIFEGRADE — Definition of Ready für die Aurelia-Integration

> Ein Modul ist integrationsbereit ab **Stufe 4**. Die Stufen sind kumulativ.

## Stufe 0 — Quellgesichert
- Original-Code/Artefakte gesichert, dekompiliert/dokumentiert, nichts geht verloren.
- Funktionsanalyse existiert und ist verifiziert (nicht geraten).

## Stufe 1 — Portierungsbasis
- `modules/<name>/QUELLENANALYSE.md` + `PORT_PLAN.md` vorhanden.
- API-/Daten-Contracts aus dem Original extrahiert (Routen, Schemas, Algorithmen).

## Stufe 2 — Engine-Prototyp
- Python-Engine nach `MODUL_STANDARD.md` lauffähig (`uvicorn` startet).
- API_CONTRACT v1 implementiert; `pytest`-Suite grün (deterministische Pfade mit Seed).
- Kernfunktion beweisbar (bei RadiWorks: Analyse + GV + Broadcast-Queue).

## Stufe 3 — Webapp-Prototyp
- HTML-App implementiert die Kernworkflows gegen die Engine.
- Aurelia-Design-Tokens + WCAG 2.2 AA-Grundlagen; deutsche UI.
- Konfigurierbare `apiBase`; läuft solo (file:// oder kleiner Static-Server).

## Stufe 4 — Integrationsreif (Definition of Ready für Aurelia)
- [ ] `/manifest` liefert vollständiges Kernel-ABI-v1-Objekt mit Hash.
- [ ] CopyGuard über alle sichtbaren Texte; keine Diagnose-/Therapie-/Heilungsformulierungen.
- [ ] WebSocket-Livekanal realisiert (`analysis.update`, `broadcast.*`).
- [ ] Mandantenfelder (`tenant_id`, `client_id`) in Schemas vorgesehen; Queries scoping-fähig.
- [ ] Smoke-Test (Engine + webapp) skriptgestützt wiederholbar.
- [ ] Dokumentation: Install, Run, Contract-Abweichungen.

## Stufe 5 — Integriert
- In Aurelia eingebunden (iframe/Preview-Host bzw. spätere Kernel-Registry), `/manifest` in Aurelias Registry registriert, Freigabe als Admin-Akt dokumentiert (`docs/06-kernel-abi.md:38-41`).

## Dokumentierter Stand (RadiWorks-Nachtrag 2026-09-30; übrige Module wie zuvor erfasst)

| Modul | S0 | S1 | S2 | S3 | S4 | S5 |
|---|---|---|---|---|---|---|
| RadiWorks | ✅ | ✅ | ✅ (lokaler Engine-Testnachweis) | ✅ (lokale Browser-Verifikation, Kandidat `a242d247`) | – (nicht zertifiziert) | – |
| Radi144 | – | – | – | – | – | – |
| RadiMorphic | – | – | – | – | – | – |
| RadiBlohm | – | – | – | – | – | – |
| RadiThoms | – | – | – | – | – | – |
| RadiCopen | – | – | – | – | – | – |

Der RadiWorks-Kandidat `a242d247` bestand den isolierten synthetischen Browser-Smoke 19/19; eine gezielte hörende Fallaktionsprobe ist bestätigt. Die im lokalen Prüfplan ausgewiesenen Fortschritte S4.6 ca. 98 % und S4.7 ca. 88 % sind **Arbeitsfortschritte**, keine Reifegrad-Stufen oder Freigaben. Ubuntu-Server-24.04.4-Zieltest, weitere WCAG-Zustände und der autorisierte Aurelia-Hostvertrag stehen aus. Der [RadiWorks-Profilentwurf](RADIOWORKS_LOCAL_PROFILE_V1_1_DRAFT.md) dokumentiert die Abweichung zum gemeinsamen v1-Vertrag; S4 bleibt offen, S5 wurde nicht begonnen.

# Modul_Templates — Koordinationsprojekt der Aurelia-Module

> **Zweck:** Alle 6–7 Module auf „eine Linie" bringen: gemeinsame Struktur, gemeinsamer API-Contract,
> gemeinsamer Prototyp-Reifegrad — damit jedes Modul als lauffähiger Prototyp in das Hauptprojekt
> **Aurelia** (`C:\Users\Hubert111\Documents\ChatGPT\Aurelia\`) integriert werden kann.
>
> **Prinzip:** Hier wird NICHT die Modullogik entwickelt (die liegt in den Modulprojekten), sondern
> die *Schnittstellenschablone*, die *Standardisierung* und die *Koordination* zwischen den Modulen.

**RadiWorks-Abgleich 30.09.2026:** `standards/API_CONTRACT.md` v1 bleibt der gemeinsame Sollvertrag. Der aktuelle lokale RadiWorks-Kandidat `a242d247` weicht an benannten Stellen ab; das [versionierte Profil als Entwurf](standards/RADIOWORKS_LOCAL_PROFILE_V1_1_DRAFT.md) macht diese Differenzen sichtbar, ohne sie für alle Module oder den Aurelia-Host freizugeben. [Register](MODULE_REGISTRY.md), [Reifegrad](standards/REIFEGRADE.md) und [Übergabepaket](UEBERGABE_AURELIA.md) führen nur belegte lokale Nachweise. S4 und die Aurelia-Integration bleiben offen. Die Hermes-/Governor-Designvorlage mit Modulakzenten ist in Brainpower `docs/AURELIA_DESIGN_TEMPLATE.md` geplant; die gemeinsame Token-/Komponentenrevision wartet auf D0/D1.

## Aufbau

```
Modul_Templates/
├── README.md                       ← diese Datei
├── MODULE_REGISTRY.md              ← Matrix aller Module: Pfad, Stack, Reifegrad, Integrationsstatus
├── standards/
│   ├── MODUL_STANDARD.md           ← die verbindliche „Linie": Ordnerschema, Stack, Konventionen
│   ├── API_CONTRACT.md             ← standardisierter REST/WebSocket-Contract je Modul
│   ├── RADIOWORKS_LOCAL_PROFILE_V1_1_DRAFT.md ← dokumentierte lokale Abweichungen, keine Hostfreigabe
│   └── REIFEGRADE.md               ← Definition of Ready für die Aurelia-Integration (Stufen 0–5)
└── modules/
    └── <modul-name>/               ← je Modul ein Koordinationsordner
        ├── QUELLENANALYSE.md       ← Verweis + Zusammenfassung der Quellanalyse
        └── PORT_PLAN.md            ← Portierungsplan (Python-Engine + HTML-App)
```

## Arbeitsregeln

1. **Nichts geht verloren:** Quellprojekte werden nie destruktiv verändert; Analysen werden hier gespiegelt.
2. **Ein Sollvertrag:** Jedes Modul richtet sich nach dem gemeinsamen API-Skelett (siehe `standards/API_CONTRACT.md`); nachgewiesene Abweichungen bleiben versioniert sichtbar, bis sie abgestimmt sind.
3. **Reifegrad vor Integration:** Ein Modul gilt als integrationsbereit erst ab Stufe 4 (siehe `standards/REIFEGRADE.md`).
4. **Aurelia ist Referenz:** Alle Konventionen leiten sich aus dem Hauptprojekt ab und werden hier zentral gepflegt — nie im Modulprojekt divergierend.

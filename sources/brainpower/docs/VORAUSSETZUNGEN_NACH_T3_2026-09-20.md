# Aurelia / Modul-Templates – aktueller Voraussetzungenabgleich nach T3

20.09.2026. Gezielter lesender Abgleich der externen Produktquellen; keine Imports, Produktstarts, Modellübermittlung oder Änderungen dort. T3-Abschluss ist in verification/REST_T3_ABSCHLUSS_2026-09-20.md belegt. Die folgenden Schritte ersetzen nicht die historischen Gesamt-Gates durch eine pauschale Freigabe.

## Ergebnis und Arbeitsreihenfolge

| Reihenfolge | Voraussetzung / Iststand | Konkreter nächster Abschluss | Zuständiger Bereich |
|---|---|---|---|
| Erledigt | T1–T3: begrenzter Vertragskern, Transport- und Ubuntu-Prozessnachweise | Vorhandene Belege weiterverwenden; keine Wiederholung bestandener synthetischer Läufe ohne Anlass | Brainpower-Testlabor |
| V1 | Getrenntes REST-Profil als Richtung angenommen; Aurelia-ABI weiterhin Python/WASM, Templates verlangen REST | Kanonische Ergänzung mit Profilrevision, vollständigem Manifest-/Schema-/Releasevertrag und ausdrücklicher Fehlerübersetzung vorbereiten; keine stillschweigende ABI-Umdeutung | Aurelia als Vertragsautorität; Templates nachgelagert |
| V2 | Anmeldung liefert geprüfte Benutzeridentität; vorgesehene Plattformdelegation braucht zusätzlich Mandant, aktuelle Berechtigung und freigegebenes Ziel | Herkunftskette Sitzung → Mitgliedschaft/Mandant → erlaubte Operation → begrenzter Delegationskontext konkret abgleichen; Preview-/Devpfad nicht als produktive Autorität übernehmen | Aurelia-Identitäts-/Berechtigungspfad |
| V3 | Synthetische mTLS-/Sperrtests bestanden; keine Produktions-CA aus diesen Tests | Reale Dienstidentitäten, Zertifikatsausgabe/-rotation/-sperre, Ablage und Restoreverfahren festlegen und gesondert prüfen | Plattformbetrieb |
| V4 | Reale Manifest-/Fachschema-/Passport-/CopyGuard-Varianten noch offen; Templates S4 nicht zertifiziert | Pro angebotenem Funktionsumfang eigene Annahme-/Negativtests, Linux-Smoke und Betriebsbelege; C-Erweiterungen nur mit eigenem Vertrag | Gewähltes Modul plus Aurelia |
| V5 | Noch kein Erstmodul gewählt; historisch Morphic zuerst, RadiWorks lokal S0–S3 dokumentiert | Aktuelle Reihenfolge ausdrücklich entscheiden; erst dann konkreten Projektadapter und Integrationsauftrag festlegen | Betreiberentscheidung |
| Vor echtem Deployment | Konfigurations-/SMB-/Schlüsselbelege vorhanden; keine komplette G0-/Produktionsfreigabe | Relevante G0-Abweichungen, Recoverywartung, Daten-/Backupumfang und Restore-/Rollbackverfahren für die konkrete Integration schließen oder ausdrücklich begründet behandeln | Plattformbetrieb und Betreiber |

V1/V2 sind die nächste zusammenhängende Arbeit: vorhandene Verträge und Identitätsherkunft konkretisieren. Dafür sind weder ein Serverneustart noch ein weiteres Paketinstallieren oder eine Wahl des Frontend-/CMS-Frameworks erforderlich. Automatische produktive Backuptimer, PostgreSQL-/CUDA-Aktivierung und Hardwarezugriff werden nicht aus bestandenen T3-Tests abgeleitet.

## Neuer gezielter Identitätsbefund

`Aurelia/src/lib/auth/verify.server.ts` vollständig gelesen: `getSessionUser()` nutzt serverseitig `auth.api.getSession` und gibt `{id,email}` zurück. `requireUserId()` gibt eine Benutzer-ID zurück; wenn Auth und Gate-Identity aus sind, sperrt eine konfigurierte Datenbank den Dev-Fallback, ohne Datenbank wird `dev-user` zurückgegeben. Das ist keine Mandanten- oder Operationsfreigabe. Der spätere REST-Adapter darf diese Benutzer-ID nicht allein in einen autorisierten Mandantenkontext umdeuten.

`gate-identity.server.ts` und `gate-session.server.ts` gezielt nach Exporten/Sitzungspfad durchsucht und vollständig gehasht. Gate-Identitätsprüfung und Sitzungsbindung sind vorhanden; ihre vollständige Vertrauenskette und deren Aufrufer wurden hier nicht auditiert. Keine Aussage über aktive ENV-Schalter oder tatsächlich genutzten Loginmodus, keine Secrets gelesen und kein Login ausgeführt.

Die bestehende Identitätsvorgabe nennt Passkeys/TOTP und Rollen pro Mandant. Der zusätzliche Broker-/Gatepfad ist vor realer Delegation mit dieser Vorgabe abzugleichen. Das ist eine offene Integrationsprüfung, kein pauschaler Defektbefund.

## Quellenfrische

Alle acht bisherigen Vergleichsquellen haben unveränderte Bytes gegenüber den dokumentierten Hashes vom 19.09. Die historischen Aussagen zum Servervorinstallationszustand bleiben damit historisch; heutige Nachweise ändern deren Gateentscheidung nicht automatisch.

| Quelle | SHA256 |
|---|---|
| Aurelia/docs/project-control/ground-zero/GATE-STATUS.md | 30a961283d70092076ad52163d8da867c5d5e308f04b5307ef231fda094217c2 |
| Aurelia/docs/06-kernel-abi.md | 9105cf2a4fc13d068b2bfa8b12aecdf81b799a607cd93afac0fe54fdc8466886 |
| Modul_Templates/standards/API_CONTRACT.md | f21ff364e208d1194f5d2f0f33679f7076adbe6b265b2ab14b9ff361e750c8c7 |
| Modul_Templates/standards/REIFEGRADE.md | fcde7896030716dba5777369919f2c7bfbe95e26708764ca20bb645cd9e7ea87 |
| Modul_Templates/UEBERGABE_AURELIA.md | df3041c005f72e2cd25cdec91c3a9fdac1efa586ef2b575ccd933b4fc174935b |
| Aurelia/docs/07-identity.md | f6668318b2de4a2212a45ea29f6075390fb07029347e4a7b563a9b42fc0fe2f5 |
| Aurelia/docs/18-clipboard.md | c78653cd5b4b743a900d58f440ed45c7dea29e0570b5e8b87976be3f2fe03c5c |
| Radiworks/radiworks_port/engine/src/radiworks/manifest.py | 2107016ecfb77cada017e428a22ff12bda785b2df8fbe92eb49a1efa2adfa00a |
| Aurelia/src/lib/auth/verify.server.ts | f52402a7220b56dcad0c81a8cb3be4ad2531f6200e0d2aef7a5744befa5079c8 |
| Aurelia/src/lib/auth/gate-identity.server.ts | 322a491b47389b998a7f1792f43abae8332b7c70e9594a205e557fe17b9fcbed |
| Aurelia/src/lib/auth/gate-session.server.ts | bfbdf247d8ed16f45ec7bcb11aed62033284696f0ff5917e33cc45b9925a1a2b |

Pfade: Aurelia unter `C:/Users/Hubert111/Documents/ChatGPT/Aurelia`; Modul_Templates und Radiworks unter `C:/Users/Hubert111/Documents`. Hashgleichheit ist Quellenfrische für diese Dateien, keine Laufzeitabnahme. Es wurden keine funktionalen Änderungen vorgenommen; keine erneute Testsuite erforderlich. Historische Matrix PROJEKTMATRIX_2026-09-20.md bleibt als Vor-T1-Ausgangsstand erhalten.

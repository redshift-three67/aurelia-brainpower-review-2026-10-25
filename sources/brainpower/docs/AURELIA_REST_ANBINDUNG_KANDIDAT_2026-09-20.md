# REST-Anbindung: konkreter Vertragskandidat V1/V2

Status: zur Übernahme vorbereitet, noch kein kanonischer Aurelia-Vertrag und keine externe Implementierung. Grundlage ist die angenommene Richtung eines separaten REST-Profils und der abgeschlossene synthetische T1–T3-Umfang. Die folgenden Regeln betreffen zunächst eine direkte synchrone CPU-Analyse mit synthetischen Daten.

## 1. Verbindliche Grenze des vorgeschlagenen Profils

Profilrevision bleibt bis zur Abnahme `aurelia-rest/1.0-draft.1`. Python/WASM und REST werden ausdrücklich getrennt ausgewählt; es gibt keinen automatischen Fallback. Kernel-/Manifest-/Schema-/Releasebindung, Budgets und CopyGuard bleiben erhalten. Eine Modulaufnahme oder ein gültiges Zertifikat erteilt keine Benutzerberechtigung.

Die in T2 verwendete Hülle `{context,payload}` gehört an einen neuen, ausdrücklich freigegebenen internen Adaptereingang. Sie wird NICHT ungeprüft an den bestehenden Modulendpunkt `/analysis` gesendet: dessen fachliches Schema bleibt unverändert. Der kontrollierte Moduladapter prüft Kontext und Payload getrennt und übergibt nur das passende fachliche Payload an die Engine. URL, Methode und Schema dieses neuen Eingangs müssen im kanonischen Profil explizit gebunden werden; ein freies Manifestziel oder ein Clientheader darf sie nicht bestimmen.

## 2. Herkunft jedes sicherheitsrelevanten Werts

| Wert | Zulässige Herkunft / vorgeschlagene Prüfung | Unzulässige Ableitung |
|---|---|---|
| actor_id | Serverseitig geprüfte Aurelia-Sitzung; zusätzlich freigegebener Authmodus | Browser-ID, dev-user-Fallback, ungeprüfter Gateheader |
| tenant_id | Ausgewählter Mandant nur als Auswahlwunsch; aktuelle Mitgliedschaft für actor_id und exakt diesen Mandanten serverseitig prüfen | Erster Mandant der Liste, Gate teamId, impliziter globaler Mandant |
| Datenklasse | Aktueller Mandantendatensatz; Erstprofil nur ausdrücklich zugelassene synthetische Umgebung | Freies Payloadfeld oder behauptete Testumgebung |
| Operation/Rechte | Explizite aktuelle Rollen-/Grantregel für actor_id, tenant_id, Modul und Operation | Anmeldung allein, tenant_admin als unbegrenzte Modulvollmacht |
| client_id / Objektbezug | Wenn Fachschema solche Felder enthält: Zugehörigkeit zum autorisierten Mandanten vor Zugriff prüfen | Nullable Feld als Beweis vorhandener Trennung |
| audience/release_id/profile_revision | Aktuell freigegebener interner Ziel-/Releasebeleg | Browser-URL, beliebige Manifest-URL oder alter Cache ohne Frischeprüfung |
| authorization_revision | Vertrauenswürdige Autorität nach aktueller Prüfung; Revision bindet den konkreten Entscheid | Clientbehauptung oder konstant erfundene Revisionsnummer |
| request_id / Gültigkeit | Kontrollierter Aurelia-Adapter; neue ID, UTC, höchstens30s, eindeutige Ablaufprüfung | Wiederverwendung als automatische Idempotenzgarantie |

Der Governor verwaltet Planung, Zustimmung und Testbelege. Er wird dadurch weder Loginanbieter noch Laufzeit-Berechtigungsdienst oder CA.

## 3. Reihenfolge des späteren Aufrufs

1. Gleiche-Origin-/Sitzungsprüfung und zulässigen Authmodus feststellen. Nicht produktiv bestätigte Preview-/Devkontexte erhalten keinen Modulzugang.
2. Gewünschten Mandanten gegen aktuelle Mitgliedschaft prüfen. Kein Aufruf von `ensurePrimaryTenant` oder `addSecondTenant` als Nebeneffekt einer Analyse.
3. Datenklasse, Rollen-/Grantregel und gegebenenfalls Objektzugehörigkeit prüfen. Nicht verfügbare Autorität verweigert den Start.
4. Freigegebenes Modulziel, Manifest-/Schema-/Releasebindung und effektive Limits prüfen. Erst danach minimalen Delegationskontext erzeugen.
5. Direkter zugelassener mTLS-Dienstaufruf. Moduladapter prüft Transportidentität, Kontext, aktuelle Berechtigung und Fachschema vor Reservierung/Ausführung. Keine Weitergabe von Browsercookies, Bearertokens oder Rollenprofilen an die Engine.
6. Vor Ergebnisfreigabe erneut autorisieren. Entzug/Ablauf/Drift verhindert die Ausgabe; ein Clienttimeout gibt den Prozessslot nicht vor belegtem Ende frei. Keine automatische Wiederholung.

Die konkrete Autoritätsschnittstelle muss eindeutige Antworten für erlaubt, verweigert und nicht prüfbar liefern. Sie benötigt aktuelle Mitgliedschaft, explizite Grantregel, Revisionsbindung und Gültigkeitsgrenze. Das bestehende `listMemberships` ist eine Grundlage für Mitgliedschaften, kein Ersatz für diese gesamte Entscheidung. Ein sofortiger Entzug zwischen letzter Prüfung und Ausgabe wird durch diesen Entwurf nicht als vollständig gelöst behauptet.

## 4. Konkrete Quellbefunde

- `auth/middleware.ts`: Same-Site-Prüfung, danach `requireUserId`; erzeugt context.userId.
- `praxis/memberships.ts`: `listMemberships` liest memberships/tenants über context.userId und liefert tenant_id, Datenklasse und Rolle. Die beiden weiteren Funktionen legen synthetische Mandanten/Mitgliedschaften an; sie werden für die Anbindung nicht ausgeführt.
- `auth/gate-identity.server.ts`: Gate-JWT-Prüfung für EdDSA, issuer/audience und sub/iat/exp; Identität enthält teamId. Keine Mandanten-/Operationsprüfung aus teamId ableiten.
- `auth/gate-session.server.ts`: Hook für /get-session, Gateprüfung und Abgleich des verknüpften Kontos, gegebenenfalls Sitzungserzeugung. Authorization-Header führt zum Überspringen dieses Hooks; daraus folgt keine Aussage über die nachgelagerte Bearerprüfung. Das Verhalten bei Gatefehler plus vorhandener Sitzung muss vor produktiver Freigabe gesondert geprüft werden.
- Gate-JWKS-Cache: Nach abgelaufener Cachezeit und fehlgeschlagener Aktualisierung kann der vorhandene Cacheeintrag weiter verwendet werden. Für das REST-Ziel einer begrenzten Richtlinien-/Schlüsselfrische ist dazu ein expliziter Betriebsentscheid und Negativtest nötig. Kein Ausnutzbarkeits- oder Live-Konfigurationsnachweis aus dieser statischen Beobachtung.
- RadiWorks `scope.py`: enforced derzeit ausdrücklich abgewiesen, freie Aurelia-Scopeheader im local-Modus verboten. Diesen Schutz nicht umgehen. Eine echte Moduldelegation braucht einen gesondert implementierten und geprüften Pfad.

## 5. Nächstes enges Prüf-/Implementierungspaket

| Kennung | Akzeptanzfall | Erwartetes Ergebnis |
|---|---|---|
| ID01 | Unangemeldet, Dev-Fallback oder nicht freigegebener Previewmodus | Null Modulaufrufe |
| ID02 | Mitglied von A wählt fremden Mandanten B | Verweigert; null B-Daten und null Modulaufrufe |
| ID03 | Mitglied von A/B wechselt Auswahl | Exakt ausgewählten aktuell erlaubten Mandanten binden; keinen ersten Mandanten übernehmen |
| ID04 | Bekannte Mitgliedschaft, unbekannte Rolle oder fehlender Operationsgrant | Verweigert, kein implizites Adminrecht |
| ID05 | Mitgliedschaft/Grant während Auftrag entzogen oder Autorität nicht erreichbar | Keine neue Ausführung/Ergebnisfreigabe; laufenden Ausgang korrekt ungeklärt/abgebrochen behandeln |
| ID06 | Gate teamId, gefälschte Scopeheader, abgelaufene Schlüsselrichtlinie | Kein Ersatz für aktuelle Aurelia-Berechtigung |
| ID07 | Schema-/Release-/Zieländerung oder Kontext-/Payloadwiderspruch | Vor Ausführung gesperrt |
| ID08 | Positiver synthetischer Fall | Ein Aufruf, unverändertes Fachpayload, gebundener geprüfter Kontext und eigener Ergebnisbeleg |

Diese acht Fälle sind neu zu belegende Anbindungsfälle; die bisherigen Labtests zertifizieren sie nicht. Zuerst konkrete Mitgliedschafts-/Grant-/Authmodus-Schnittstelle und kanonischen Adaptereingang festlegen, danach gezielt implementieren und testen. Änderungen an Aurelia/Modul_Templates und später am ausgewählten Modul brauchen ihren jeweiligen Auftrag/Gate; aktuell wurden nur lokale Planungsdateien geschrieben. Kein weiterer allgemeiner Konzeptaufbau oder Paketinstallation nötig.

## 6. Übernahmeumfang und noch offene Entscheidungen

Die vorgeschlagene kanonische Übernahme besteht aus einer eigenständigen Aurelia-Profilbeschreibung, einer expliziten Referenz im Kernel-ABI und einer dazu passenden Template-Referenz. S4/S5 bleiben separate Reifegrade. Vor deren Änderung werden die Regeln des jeweiligen Zielrepositories gelesen und konkrete Diffs vorgelegt. Es gibt noch keinen angewendeten Patch in diesen Repositories.

Vor Implementierung festzulegen: freigegebener Aurelia-Authmodus, Rollen-/Grantmatrix für analysis, vertrauenswürdige Autoritätsquelle samt Revision/Entzug, exakter interner Adaptereingang und reale CA-Betriebsparameter. Keine dieser fachlichen Entscheidungen wird aus dem sichtbaren Benutzerlogin oder T3-Teststatus erfunden. Erstmodulwahl, produktive Daten, PostgreSQL-/CUDA-/Hardwarebetrieb und S4-/Deploymentfreigaben folgen separat.

## Quellenbindung und Prüfgrenze

Aurelia-Pfade unter C:/Users/Hubert111/Documents/ChatGPT/Aurelia. Gezielte statische Prüfung, keine Produktimporte, keine ENV/Secrets, keine HTTP-/DB-Aufrufe und keine Live-Auth-Abnahme.

| Quelle | SHA256 |
|---|---|
| src/lib/auth/middleware.ts | 6feeb612fb7f2c752f7ada845fe54b0ad4bf954ba2321561e432d3bb47bd10f1 |
| src/lib/praxis/memberships.ts | fcd60f0fa7e4dc2bd2ebc7e47ae9be304432c756541e8090370825da973876e9 |
| src/lib/auth/gate-identity.server.ts | 322a491b47389b998a7f1792f43abae8332b7c70e9594a205e557fe17b9fcbed |
| src/lib/auth/gate-session.server.ts | bfbdf247d8ed16f45ec7bcb11aed62033284696f0ff5917e33cc45b9925a1a2b |

Weitere Vertrags-/Manifesthashes und Herkunft: VORAUSSETZUNGEN_NACH_T3_2026-09-20.md. Dokumentänderung, keine funktionale Änderung; vorhandene 222 Labtests nicht erneut ausgeführt und nicht als Anbindungsnachweis bezeichnet.

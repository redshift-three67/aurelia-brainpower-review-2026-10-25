# Aufgabenabhängige Codex-Chatroute — Stand23.10.2026

Vom Betreiber freigegebene aktuelle Chatvorgabe für Aurelia, alle Module, Governors und Modul_Templates:

| Aufgabe | Auswahl |
|---|---|
| Geklärte Zusammenführung, normale Testplanung und Code-/Datenabgleich | GPT-6.1 Sol/medium |
| Schwierige Mathematik/Binärfragen, Fehlerketten, Recovery, Nebenläufigkeit, Sicherheit und zentrale Daten-/Job-/Mandanten-/Rechteverträge | GPT-6.1 Sol/high |
| Begrenzte Inventar-/Schema-/Tabellenextraktion | Luna/low oder medium zunächst vergleichen; Quellen/Hashes unabhängig prüfen |
| Anspruchsvolle begrenzte Konsistenzprüfung mit begründetem Zusatznutzen | Luna/max |
| Unabhängige kritische Schlussprüfung | Astra/medium |
| Kritischer ungelöster Widerspruch nach Belegprüfung | Astra/high als ausdrücklich gewählte und berichtete Ausnahme |

Die V5-Limit-/Bereinigungsdiagnose bleibt high-geeignet. Neue begrenzte Teilaufträge können mit der passenden freigegebenen Rolle starten. Die erste Luna/medium-Probe enthielt eine Namensraumverwechslung und einen verkürzten Hash; nach Quellenprüfung korrigiert. Keine allgemeine Qualitätsgleichheit oder gemessene Ersparnis daraus ableiten. Modelltext ersetzt keine maschinelle Quellen-/Hashprüfung.

Diese Richtlinie schaltet den laufenden Hauptchat nicht um. Dafür ist eine verfügbare Runtime-Steuerung oder die Desktopauswahl des Betreibers erforderlich; nur belegte Wechsel als erfolgt melden. Keine globale Profildatei, Hermes-Route, automatische Reviewfunktion oder Serverkonfiguration wird geändert. Freigaben, Algorithmen und Stopbedingungen bleiben bestehen. Repräsentative Vergleiche betrachten gültige Ergebnisse, Fehler, Laufzeit und tatsächlich verfügbare Verbrauchswerte; keine festen Einspar- oder Astra-Anteilzusagen. [Offizielle Reasoning-Empfehlungen](https://developers.openai.com/api/docs/guides/deployment-checklist).

**Historischer Installationsstand:** Der unveränderte Text unten dokumentiert frühere feste Profile und damalige Prüfungen. Seine Sol/high-/Luna/max-Standardanweisungen sind durch die obige aktuelle Route ersetzt. Vorhandene Profildateien wurden hier nicht umgeschrieben.

---

# Dauerhafte Codex-Chat-Variante B — Stand 26.09.2026

**Aktualisierung 03.10.2026:** Der Betreiber hat für den Codex-Chat GPT-6.1 Sol/`high` als Orchestrator gewählt. Das separate `chat-sol-lead.config.toml` wurde nach Backup und TOML-Prüfung darauf umgestellt; GPT-6 Luna/`max` und GPT-6 Astra/`medium` behalten ihre Rollen. Die globale `config.toml` mit CC-Switch-Provider wurde nicht geändert. Im laufenden Desktop-Chat muss der Betreiber GPT-6.1 Sol und `high` ausdrücklich auswählen; die Profildatei schaltet den aktuellen Turn nicht selbst um. Die übrigen Angaben zu Sol 6 und den damaligen Kostenproben sind historische Nachweise, keine Messung für GPT-6.1 Sol.

**Aktualisierung 30.09.2026:** Die aktuell gelesene globale `%USERPROFILE%\.codex\config.toml` enthält keine Modell-/Unteragenten-Defaults und keinen Route-B-Marker; das separate `chat-sol-lead.config.toml` sowie `chat_luna.toml` und `chat_astra.toml` existieren. Die Aussagen unten zu damals global installierten Defaults sind historische Installationsbelege. [Aktueller Abgleich und portierbare Anleitung](CODEX_CHAT_ROUTE_B_TRANSFER_2026-09-30.md).

**Aktuelle Chatvorgabe:** GPT-6.1 Sol/high führt, Luna 6/max arbeitet begrenzte Teilaufträge ab, Astra 6/medium prüft unabhängig kritische Entscheidungen oder verbleibende wesentliche Widersprüche. Die Hermes-Anwendung behält ihre separat wählbare Route B mit Sol 6/high. Die Serverkonfiguration bleibt unverändert.

## Bedienung dieser Sitzung

In der Modellauswahl des aktuellen Chats **GPT-6.1 Sol / high** wählen. Die Routingentscheidung ist hier durch den Betreiberauftrag und zusätzlich in der Projektanweisung festgehalten. Die Dateiänderung allein beweist nicht, dass eine bestehende Desktop-Aufgabe bereits dieses Hauptmodell nutzt. Am 03.10.2026 bestätigen die aktuellen Chatprotokolle diese Kombination. Keine neue Chat-Aufgabe ist für die Fortsetzung erforderlich.

Gespeicherte Standards für neue lokale Aufgaben und das benannte Profil verwenden Sol/high. Normale eigenständige Teilaufgaben gehen an Luna/max. Astra/medium ist ein separat gebundener unabhängiger Prüfer, kein automatischer Ersatz für den Hauptchat. Fehlende Belege bleiben unbekannt. Modellprüfungen ersetzen weder Betreiberfreigaben noch Projektschutzregeln.

## Übertragung auf einen weiteren PC

- [Vollständige Installation, Abnahme und Rücknahme](../artifacts/chat-route-b24/README.md)
- [Transportpaket ohne Konten oder Projekte, Stand 26.09.2026](../artifacts/Codex-Chat-Variante-B-2026-09-26.zip)
- [Exakte Routinganweisung](../artifacts/chat-route-b24/ROUTING.txt)

Das Paket benötigt Python 3.11+ und eine separat eingerichtete Codex-Instanz mit Zugang zu den drei Modellen. Die Installation erhält vorhandene Provider und Berechtigungen. Kein fremdes Authentifizierungsverzeichnis kopieren. Die Zielinstanz ist erst nach dortiger Prüfung abgenommen; hier wurde ihre Installation in einem temporären Verzeichnis geprüft, nicht der unbekannte PC selbst.

## Installierte Dateien und Sicherung

Bei der ursprünglichen Installation wurden vier Dateien geändert. Die Aktualisierung vom 26.09.2026 änderte nur `config.toml` und `chat-sol-lead.config.toml`; die Kindrollen blieben unverändert:

- `config.toml`: Hauptmodell Sol/high, zusätzliche Routinganweisung, neue Aufgaben ebenfalls Sol/high, Agentenvorgaben Luna/max und gleichzeitige Kindaufgaben maximal zwei.
- `chat-sol-lead.config.toml`: explizit startbares B-Profil einschließlich Astra-Regel.
- `agents/chat_luna.toml`: begrenzter Worker ohne rekursive Delegation.
- `agents/chat_astra.toml`: unabhängiger Prüfer mit read-only Sandbox und ohne rekursive Delegation.

Vorherige Inhalte liegen jeweils daneben mit Suffix `.pre-route-b-20260924-212431-802830.bak`. Globale Provider-/Zugangs-/MCP-/Berechtigungseinstellungen bleiben erhalten. Alte A- und agent-duo-Profile bleiben als ausdrücklich wählbare Alternativen vorhanden; ihre explizite Auswahl kann die neue Standardroute übersteuern. Bei der damaligen Chat-Installation wurden Hermes-Dateien nicht verändert; die spätere eigenständige Hermes-Route-B-Umstellung ist im aktuellen Routenbericht dokumentiert. Die Chat-Entscheidung wurde zusätzlich in `AGENTS.md` und `WIEDERAUFNAHME.md` dokumentiert.

## Prüfung und Nachweise

Die beiden unten genannten Live-Delegationsprüfungen vom 24.09.2026 liefen mit **Sol/xhigh** und sind historische Nachweise. Für die neue high-Einstellung bestanden Installer-Tests, TOML-Prüfung und idempotente Vorschau (`changed_files: []`). Ein echter Chat-Delegationslauf mit Sol/high und ein fachlicher high/xhigh-Vergleich fehlen noch; die aktive Einstellung dieser bereits laufenden Sitzung folgt nicht beweisbar aus der gespeicherten Datei. Die Aktualisierung sicherte die zwei geänderten Dateien mit Suffix `.pre-route-b-20260926-191122-714034.bak`.

- Vier Installerprüfungen bestanden: Erhalt fremder Einstellungen und bestehender Anweisungen, Vorschau ohne Schreiben, Sicherung und Wiederholbarkeit sowie Abbruch bei fremdem Standardprofil/ungültigem TOML. Zwei anfängliche Testläufe scheiterten ausschließlich an Sandbox-Dateirechten; derselbe Testlauf außerhalb der Sandbox bestand.
- Erneute Installationsvorschau nach Anwendung: `changed_files: []`.
- Codex lud `CHAT_ROUTING_B_V2_BEGIN` mit beiden Rollen sowohl aus dem Standard als auch aus dem expliziten B-Profil; geprüft ohne Modellanfrage.
- Live-Standard ohne Profiloverride: Hauptagent Sol/xhigh, genau ein Luna/max-Kind mit frischem Kontext, beide beendet; Ergebnisse 113 und 55 korrekt. 47,532 Sekunden einschließlich Start/Koordination.
- Live-B-Profil: Hauptagent Sol/xhigh, genau ein Astra/medium-Kind mit frischem Kontext, beide beendet. Widersprüchliche Restore-Belege bleiben ungeklärt, fehlende Freigabe bleibt fehlend, Löschung nicht erlaubt. 55,640 Sekunden einschließlich Start/Koordination. Der Prüfauftrag beschrieb das Risiko und den Konflikt, ohne das gewünschte Kindmodell vorzugeben.
- Keine unerlaubten Werkzeuge, Zeitüberschreitungen oder Modellsubstitutionen in diesen beiden Prüfungen. Vier temporäre Testaufgaben anschließend archiviert; Belege bleiben erhalten.

Bereinigte Belege: `artifacts/chat-route-b24/prompt-check.json`, `live-worker.json`, `live-critical.json` und `package-verification.json`. Die Testmetadaten belegen gebundene Modellnamen/Efforts und abgeschlossene Kinder; sie sind keine unabhängige Attestierung interner Modellgewichte. Der neue Astra-Auslösepfad wurde einmal geprüft; seltene Fehler, Langzeitstabilität und reale Einsatzquote sind damit nicht allgemein nachgewiesen.

## Kosten richtig einordnen

Der frühere kleine A/B-Vergleich ergab für B rund **67,9% niedrigere Standard-API-Referenzkosten** als für Astra allein. Zusätzliche Astra-Prüfungen sind darin nicht enthalten. Unter der Annahme, dass bei 10% der Aufgaben ein zusätzlicher Astra-Prüfauftrag so viel kostet wie ein damaliger vollständiger Astra-Auftrag, verbleiben rechnerisch rund **57,9% Ersparnis**. Kürzere Prüfkontexte können günstiger sein. Zehn Prozent Aufgabenanteil bestimmen weder den Kostenanteil noch die Tokenquote.

Deshalb keine feste Eingriffsquote, keine Zusage von zwei Dritteln Ersparnis und keine Behauptung optimaler Akkuranz. Der Originalvergleich umfasst nur drei synthetische Aufgaben mit je zwei Wiederholungen; die hier ergänzten zwei Fälle sind Funktionsproben. Tatsächliche Codex-Abrechnung und langjährige Einsatzqualität wurden nicht gemessen. Details und Formel stehen in der Installationsanleitung; historischer Vergleich: [A/B-Bericht](verification/CHAT_ROUTING_AB_2026-09-24.md).

## Quellen

- [Offizielle Codex-Konfiguration](https://learn.chatgpt.com/docs/config-file/config-reference): Entwickleranweisungen und Modellvorgaben; explizite Auswahl kann neue Aufgabenvorgaben übersteuern.
- [Offizielle native Unteragenten](https://learn.chatgpt.com/docs/agent-configuration/subagents): getrennte Rollen mit explizitem Modell und Reasoning.

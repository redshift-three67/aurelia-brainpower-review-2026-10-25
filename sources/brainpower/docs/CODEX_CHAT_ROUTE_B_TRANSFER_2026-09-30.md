# Codex-Chat-Route B: Sol/high, Luna/max, Astra/medium

**Aktualisierung 03.10.2026:** Auf diesem PC ist im separaten Chat-Profil nun `gpt-6.1-sol`/`high` statt `gpt-6-sol`/`high` eingetragen. Luna/`max` und Astra/`medium` bleiben gleich. Für den aktuellen Desktop-Chat GPT-6.1 Sol und `high` manuell wählen; die Datei allein schaltet ihn nicht um. Das Installationspaket vom 26.09. und die unten stehenden historischen Vergleiche beschreiben weiterhin Sol 6 und müssen vor einer Übertragung auf einen anderen PC eigens aktualisiert und dort geprüft werden. Die Hermes-Anwendungsroute und der CC-Switch-Provider blieben unverändert.

Stand: 30.09.2026. **Gilt nur für Codex-Chat, nicht für die Hermes-Anwendungsroute.** Die Auswahl in einer laufenden Desktop-Aufgabe muss dort separat geprüft werden. Dies ist eine portierbare Betriebsbeschreibung, keine Zusage automatischer oder deterministischer Modellaufrufe.

## Rollen und Entscheidung

| Rolle | Modell / Effort | Wann und mit welchem Ergebnis |
| --- | --- | --- |
| Hauptchat | `gpt-6-sol` / `high` | Versteht Auftrag und Grenzen, prüft Quellen, entscheidet über begrenzte Delegation, führt Ergebnisse zusammen und verantwortet die Antwort. Erledigt einfache Aufgaben selbst. |
| Begrenzter Helfer | `gpt-6-luna` / `max` | Für eine konkret abtrennbare, nützliche Teilaufgabe mit frischem, möglichst kurzem Kontext. Der Hauptchat prüft den Befund; Luna erteilt keine Produktfreigabe und delegiert nicht weiter. |
| Unabhängige Gegenprüfung | `gpt-6-astra` / `medium` | Vor folgenreichen Entscheidungen mit wesentlichem Datenverlust-, Zugriffs-/Sicherheits- oder irreversiblen Produktionsrisiko; ebenso bei nach eigener Evidenzprüfung verbleibenden materiellen Widersprüchen. Astra erhält konkurrierende Belege und prüft unabhängig, entscheidet aber nicht anstelle des Betreibers. |

Fehlende Fakten werden zuerst beschafft oder ausdrücklich als unbekannt markiert. Das bloße Wort „Sicherheit“ in einer Aufgabe löst keine Astra-Prüfung aus. Eine angenommene Astra-Quote von 10 % ist weder eine harte Grenze noch eine gemessene Einsatzhäufigkeit. Normalerweise höchstens zwei Kinder je Auftrag, davon höchstens ein Astra. Keine rekursive Delegation, kein stiller Modellwechsel und keine neue Berechtigung für Dateien, Server, Versand oder Freigaben.

## Was auf diesem PC aktuell belegt ist

`%USERPROFILE%\.codex\chat-sol-lead.config.toml` deklariert Sol/high, Luna/max als Standard für Unteragenten und höchstens zwei gleichzeitig offene Kinder. `agents\chat_luna.toml` bindet Luna/max; `agents\chat_astra.toml` bindet Astra/medium und setzt dessen Sandbox auf `read-only`. Die Routinganweisung steht in [ROUTING.txt](../artifacts/chat-route-b24/ROUTING.txt) und sinngemäß in der Projektanweisung `AGENTS.md`.

**Aktueller Konfigurationsbefund:** Die am 30.09. gelesene `%USERPROFILE%\.codex\config.toml` enthält Provider-/MCP-Einstellungen, aber keinen globalen `model`-, `model_reasoning_effort`- oder `[agents]`-Default und keinen Route-B-Marker. Das separate Profil und die Projektanweisung existieren weiterhin. Der ältere [Statusbericht](CODEX_CHAT_VARIANTE_B.md) beschreibt eine frühere Installation globaler Defaults und ist für diesen Punkt historisch. Weder Profil-Datei noch Chat-Nachricht beweisen die effektive Modellwahl einer bereits laufenden Desktop-Aufgabe.

## Auf einem zweiten Windows-PC einrichten

1. Codex auf dem Ziel-PC installieren und dort selbst anmelden. Verfügbarkeit von `gpt-6-sol`, `gpt-6-luna` und `gpt-6-astra` sowie Efforts `high`, `max`, `medium` im dortigen Client prüfen. **Keine** Authentifizierungsdateien, Konten, Projekte oder fremde Providerkonfiguration kopieren.
2. Das vorhandene [projektfreie Installationspaket](../artifacts/Codex-Chat-Variante-B-2026-09-26.zip) mit [Anleitung](../artifacts/chat-route-b24/README.md) verwenden. Vor der Anwendung eine dort vorhandene Codex-Konfiguration sichern; `py -3 install.py --check`, dann `py -3 install.py --apply`, dann erneut `--check`. Der Installer meldet Änderungen und erzeugt Backup-Dateien. Er darf vorhandene abweichende Profilvorgaben nicht still überschreiben.
3. Codex neu starten und für den Chat **Sol/high** auswählen. Bei expliziter CLI-Profilwahl `codex -p chat-sol-lead` verwenden, sofern das installierte Profil in der dortigen Version verfügbar ist. Prüfen, ob die Routinganweisung geladen wird; ein geladener Text ist noch kein ausgeführter Modellaufruf.
4. Eine harmlose synthetische Luna-Probe und eine getrennte synthetische Astra-Widerspruchsprobe gemäß [Paket-Anleitung](../artifacts/chat-route-b24/README.md) ausführen. Die tatsächlichen Kindmodell-/Effort-Metadaten prüfen; Modellselbstauskünfte genügen nicht. Bei fehlender Modellverfügbarkeit oder fehlendem Kindnachweis keine erfolgreiche Delegation behaupten. Die Rücknahme steht in derselben Anleitung.

Aktuelle [OpenAI Docs zu Unteragenten](https://learn.chatgpt.com/docs/agent-configuration/subagents) bestätigen: Eigene Agenten können Modell und `model_reasoning_effort` festlegen; ohne solche Bindung werden Werte vom expliziten Spawn, den `[agents]`-Defaults oder dem Elternagenten abgeleitet. `[agents].max_concurrent_threads_per_session` begrenzt gleichzeitig laufende Kinder, nicht die Anzahl aller späteren Aufrufe. Die [Konfigurationsreferenz](https://learn.chatgpt.com/docs/config-file/config-reference) beschreibt die gültigen Schlüssel. Diese Dokumentation kann sich ändern; den Ziel-PC nach Installation mit seiner aktuellen Clientversion prüfen.

## Akkuranz, Token- und Kosteneffizienz

Die kleine frühere A/B-Probe umfasste **drei synthetische Aufgaben mit je zwei Wiederholungen** je Variante; B und Astra allein beantworteten je **6/6 fachlich korrekt**. Damit sind Rollenfunktion und einige Fehlergrenzen illustriert, aber kein allgemeiner Qualitätsvorsprung, keine optimale Akkuranz und keine Langzeitstabilität nachgewiesen. Die zwei späteren Delegationsproben liefen noch mit Sol/**xhigh**; für Sol/**high** sind Profilinstallation und TOML-Prüfung dokumentiert, ein gleichwertiger fachlicher Vergleich fehlt.

Der historische B-Vergleich mit Sol/xhigh und Luna/max ergab **0,227886 USD** gegenüber **0,710670 USD** für Astra/medium allein als rechnerische **Standard-API-Referenz** mit den damals gemeldeten Cachelesungen: ungefähr **67,9 % niedriger**. Zusätzliche Astra-Prüfungen waren darin nicht enthalten. Unter der unbewiesenen Annahme, dass 10 % zusätzliche Prüfungen jeweils so viel wie ein voller damaliger Astra-Auftrag kosten, wären es ungefähr **57,9 %**; tatsächliche Codex-Abrechnung, Chat-Abonnement, Kontextlänge und neue high-Nutzung wurden nicht gemessen. Eine höhere Reasoning-Stufe kann mehr Zeit und Tokens benötigen, verbessert schwierige Aufgaben aber fallabhängig; die [OpenAI-Modellübersicht](https://developers.openai.com/api/docs/models) ordnet Luna als effizient, Sol als Balance und Astra als stärkstes Modell ein. Ein modellübergreifend stabiler Prompt-Cache oder eine garantierte Ersparnis ist nicht belegt; kein erfundener `prompt_cache_mode` wird gesetzt.

**Praktische Regel:** Akkuranz hat Vorrang. Sol prüft Luna-Ergebnisse anhand der Originalbelege, Astra bearbeitet den klar benannten kritischen Restfall, und ungeklärte Evidenz bleibt ungeklärt. Freigaben und Projektschutzregeln bleiben außerhalb dieser Modellroute bestehen.

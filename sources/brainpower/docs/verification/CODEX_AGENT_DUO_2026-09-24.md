# Codex-Konfiguration: Luna und Sol

Betreiberauftrag vom 24.09.2026: Luna als Standard-Worker, Sol/xhigh als Orchestrator im Profil agent-duo; Hermes erst danach gesondert besprechen.

Installiert in der Benutzerkonfiguration `C:/Users/Hubert111/.codex/config.toml`: model=gpt-6-luna, bisheriges model_reasoning_effort=medium erhalten. agents.default_subagent_model=gpt-6-luna und agents.default_subagent_reasoning_effort=medium. Worker-Effort im neuesten Auftrag nicht angegeben; keine pauschale max-Aktivierung.

Separates Profil `C:/Users/Hubert111/.codex/agent-duo.config.toml`: model=gpt-6-sol, model_reasoning_effort=xhigh; dieselben Luna/Medium-Unteragentenvorgaben. CLI-Aufruf: `codex -p agent-duo`. Die installierte CLI 0.149.1 verwendet separate Profildateien. Keine erfundenen Schlüssel orchestrator, worker oder prompt_cache_mode übernommen.

Sicherung: `C:/Users/Hubert111/.codex/config.toml.pre-agent-duo-20260924-195444.bak`. TOML vor/nach Änderung strukturell verglichen; Provider, Authentifizierung, Berechtigungen und sämtliche anderen Werte erhalten. Codex `debug prompt-input` hat das tatsächlich installierte Profil erfolgreich geladen, ohne Inferenz. Die strikte Prüfoption ist bei diesem Diagnosebefehl nicht unterstützt; daher keine strikte Schemaabnahme behaupten. Erste Prüfung im Sandboxkontext scheiterte an Codex-eigenem Verzeichniszugriff, genehmigte Wiederholung erfolgreich.

Grenzen: keine bestätigte Umschaltung der laufenden Desktop-Aufgabe; dort Sol/xhigh im Modellmenü auswählen. Globale Dateiwerte ersetzen bestehende aufgabenspezifische Auswahl nicht nachweislich. Das Profil definiert Modelle, erzwingt aber weder automatische Delegation noch garantierte modellübergreifende Cachetreffer. Keine Änderung an Hermes oder dessen Routing. Vorherige synthetische Routerproben für Sol/xhigh und Luna/max bleiben reine Transportnachweise, kein Duo-Ende-zu-Ende-Test.

Quellen: https://learn.chatgpt.com/docs/config-file/config-reference und https://developers.openai.com/api/docs/guides/prompt-caching .

## Folgeänderung: Luna Max

Betreiber meldet die Chat-Umstellung und verlangt anschließend ausdrücklich Max für Luna. `config.toml` verwendet nun Luna/max als globale Vorgabe und Luna/max als Unteragentenvorgabe. Das Profil `agent-duo.config.toml` behält Sol/xhigh als Hauptmodell und verwendet Luna/max für Unteragenten. Vorherige Dateien unter `.pre-luna-max-20260924-200241.bak` gesichert. Beide TOML-Dateien strukturell verglichen und geparst; das installierte Codex-Profil erneut erfolgreich ohne Inferenz geladen. Die anfänglichen Medium-Angaben oben dokumentieren nur die Erstkonfiguration. Für die laufende Chat-Auswahl liegt die Betreibermeldung vor; ihre tatsächliche Stufe wurde technisch nicht ausgelesen. Hermes bleibt unverändert.

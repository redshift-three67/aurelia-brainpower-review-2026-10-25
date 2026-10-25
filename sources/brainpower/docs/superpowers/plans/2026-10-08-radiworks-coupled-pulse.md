# RadiWorks gekoppelte Pulsprofile – bestätigtes Design und Implementierungsplan

> Für agentische Bearbeitung: superpowers:subagent-driven-development; unabhängiger Review. Betreiberfreigabe aus Chat2026-10-08 gilt bereits, keine erneute Freigabeschleife. Kein Git-Commit im fremden Profil-Repository; isolierte manifestierte Kopie.

**Ziel:** Freigegebene Rosa-Rauschen-Profile mit gekoppelten Pulsraten/Abschnittsdauern, unveränderte Originalalgorithmen und historische Profile.
**Architektur:** Reiner Frameplan und Hüllkurve im Browserworker; CAS-geschütztes versioniertes Medienprofil bleibt Companion zum Broadcastziel. Keine Analyse-/GV-/Entropieformeln ändern.
**Technik:** Python/FastAPI bestehender Enginevertrag; VanillaJS/Worker/WebAudio, Float64-Planung und Float32-PCM.

## Exakter Vertrag

IDs pink-pulse-v1/pink-phi-v1/pink-fibonacci-v1. Basissekunden30, ganzzahlig konfigurierbar. ModulationDepthPercent50, ganze0..100. Repeat explizit. Einfache Pulse:1Hz, eine Stufe. Phi: phi=(1+sqrt(5))/2, k0..4, Rate=phi^kHz, Dauer=Basissekunden*phi^k. Fibonacci: Faktoren1,2,3,5,8,13, Rate=0.5*FaktorHz, Dauer=Basissekunden*Faktor. Maximal600s je tatsächlichem Abschnitt: Basis max600/87/46s für gleichmäßig/Phi/Fibonacci. Überschreitung ablehnen, nicht still kappen. Im UI vollständige Stufenfolge/Gesamtdauer anzeigen; 30s ergibt Phi rund489.79s und Fibonacci960s. Pure Planprofile version1.

Framezahl jeder Stufe=Math.round(Dauer*actualSampleRate). Framegrenzen kumulieren, Phasenfortschritt aus quantisierter Dauer; an Stufen- und Wiederholungsgrenzen kontinuierlich. Hüllkurve=(1-depth)+depth*(0.5-0.5*cos(2*pi*phase)), depth=Percent/100. Kein Frequenzsprung im hörbaren Rauschträger; nur weiche Amplitudenmodulation. Rauschkern/Gainregel/Seedfolge unverändert, Hüllkurve0..1 erhält Peakgrenze. Späte Aktivierung verwendet die Phase/Position zum Broadcast-Elapsed; keine Nachholwiedergabe. Einmalprofil endet mit Folge, Repeat mit Broadcast. Maximal86400s Broadcast; kein unbegrenzter Puffer.

Persistenz: Bestehende schemaVersion1-Profile unverändert lesen/schreiben und validieren. Neue drei IDs nur schemaVersion2 mit zusätzlichem modulationDepthPercent; unveränderliche ID-v1 bindet Formel/Stufenzahl. Profil-Digest umfasst alle Parameter. Companion bleibt Schema1, erlaubt beide streng geprüften Profilschemata; alte Belege/Digests nicht neu schreiben. PUT-Feld modulation_depth_percent optional für alte IDs, für neue zwingend; Werte/Typen/Grenzen fail-closed. Nichtpulsende IDs mit Modulationsfeld ablehnen. Fall-/Scope-/CAS-Prüfungen erhalten.

## Aufgaben mit Eigentümerschaft

- [x] P1 Luna: nur engine/src/radiworks/core/presentation_profile.py, api/routes.py und neue engine/tests/test_presentation_pulse_profiles.py. Erst Schema/CAS/Legacy/Digest/Broadcastsnapshot-Tests RED, dann kleinste Erweiterung. Testkommando Python-venv -m pytest -q engine/tests/test_presentation_pulse_profiles.py engine/tests/test_presentation_profiles.py. Keine personal/analysis/entropy/broadcast Kernänderung.
- [x] P2 Root: webapp/js/pink-pulse-profile.js + .test.mjs. Tests RED für bekannte fünf/sechs Stufen, sichere Framegrenzen, Rate/Dauerfaktoren, Hüllkurve0..1, kontinuierliche Grenzphase, Repeat/Late und abgelehnte Basisgrenzen. Export planPinkPulse(profile,sampleRate), pulseGainAtFrame(plan,frame), isPulseProfile(id), pulseBaseLimit(id). Keine neue Runtime-Abhängigkeit.
- [x] P3 Root: pink-worker.js/Hüllkurve und broadcast-audio-player.js/startPink; Tests erst RED für Worker-Init/Elapsed/Broadcast-Ende/Repeat/ausgeschöpften Plan. Worker erhält optionalen pulseProfile-Planinput+startFrame; init bisheriger Pinkweg unverändert kompatibel. Eigener Audiopulsverbrauch verändert keine analytische RNG; begrenzte Blockgröße und Stop bleiben erhalten.
- [x] P4 Root: PresentationEditor/case-presentation/index/views/broadcast. Drei Auswahlprofile, dynamische Basisdauergrenze, Depth nur bei Pulsprofilen, lesbare Stufenvorschau, Änderungen erst nach bewusstem Profilspeichern; alte Jobs unverändert. Tests für Legacy-Payload ohne Zusatzfeld und V2-Payload, ungültige aktuelle UI-Eingaben nicht speichern.
- [x] P5 Astra: Spezifikation zuerst, dann Qualität/Drift/Peak-/Zeit-/Legacy-Grenzen unabhängig prüfen. Keine Writes, kein Review als Freigabe behandeln.
- [x] P6 Root: neue Numeriktests +79 alteUItests, relevante162Backendtests+Personal9 separat, Worker-PCM-Referenz und synthetischer Chrome-Lauf auf8113 oder freiem Entwicklungsport außerhalb8103–8109. Aktuelle8112 read-only prüfen; keine echte Kamera/Audioausgabe ohne Nutzerprobe. Lesbare1440/390Ansichten, Stagewechsel/reduced-motion/Stop/Profilbindung.
- [x] P7 Root: hashmanifest, Provenienz, genaue Grenzen/Tests/Reviewbericht, neuer lokaler Wiederherstellungspunkt; Benutzerprobe vorbereiten. Dauerinstanzen/R6/Start5 erst nach gemeinsamer Abnahme. Vollprojekt-F:-Sicherung folgt nach Start5; Datenbankstruktur später.

Technischer Abschluss: docs/verification/RADIWORKS_PULSPROFILE_2026-10-08.md. 8112 nach Sicherung/datenwahrendem Neustart bereitgestellt; gemeinsame Nutzer-/Hörabnahme vor R6/Start5 offen.

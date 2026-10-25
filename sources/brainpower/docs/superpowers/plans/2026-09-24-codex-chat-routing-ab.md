# Codex Chat Routing A/B Implementation Plan

**Goal:** Zwei vom Betreiber freigegebene Codex-Chat-Varianten konfigurieren und mit identischen synthetischen Aufgaben vergleichen. Hermes bleibt vollständig ausserhalb des Versuchs.

**Architecture:** Separate Benutzerprofile `chat-luna-lead` und `chat-sol-lead`; benannte Unteragenten mit festem Modell/Effort. Profil A: Luna/max, gezielte Sol/xhigh-Pruefung, anschliessend Astra/medium nur bei verbleibendem evidenzbezogenen Widerspruch. Profil B: Sol/xhigh, Luna/max fuer abgegrenzte Teilaufgaben. Beide Hauptmodelle pruefen Ergebnisse, eskalieren fehlende Fakten nicht als vermeintlich geloeste Fakten, verwenden keine rekursiven Delegationen und erhalten alle bestehenden Berechtigungen. Globale Voreinstellungen werden nicht umgestellt.

**Tech Stack:** Codex CLI 0.149.1, native Chat-Unteragenten, TOML, Python-Standardbibliothek als lokaler Testtreiber. Keine direkten API-Ketten als Ersatz fuer Unteragententests.

## Schritt 1: Konfiguration und Funktionsnachweis

- [x] Offizielle Konfigurations-/Unteragentendokumentation und installierte Version pruefen.
- [x] Echte Luna/max-Unteragentenanforderung in dieser Aufgabe: JSON-Summe 50 korrekt. API-Anforderung akzeptiert; kein Modellselbstauskunftsbeweis.
- [x] Zwei Profile und drei benannte Unteragenten unter Benutzer-Codex vorbereiten, TOML und geladene Instruktionen pruefen. Quellen in `artifacts/chat-routing-ab24/config/` erhalten.
- [x] Native Anforderung beider Helfer und moeglicher Astra-Eskalation pruefen. Gespeichertes Profil ist keine bestaetigte Profilaktivierung im bestehenden Desktop-Chat.

## Schritt 2: Vorab festgelegter Vergleich

Je Variante zwei Wiederholungen von drei identischen synthetischen Aufgaben, Reihenfolge A/B dann B/A. Routinefall: Rechnung und striktes JSON; keine Delegation. Analysefall: unabhaengige Gegenpruefung einer kleinen Zustandstabelle, explizite begrenzte Delegationsfreigabe. Unsicherheitsfall: widerspruechliche Quellen ohne eindeutige Aufloesung; Ungewissheit sichtbar lassen. Erwartete Antworten und harte Fehler vor dem Lauf speichern; keine Anpassung der Erwartungen nach Antworten.

Bewertung: Korrektheit, korrektes JSON/Instruktionstreue, echte angeforderte und abgeschlossene Unteragenten, keine unzulaessigen Tools/Dateiaenderungen, Gesamtlatenz, Fehler/Timeouts, Prompt-/Ausgabe-/Cache-Tokens soweit vollstaendig auf Haupt- und Kindmodelle zurechenbar. Fehlende Kindabrechnung bedeutet **keine belastbare Gesamtkostenaussage**. Offizielle API-Preise koennen nur als Vergleichsschaetzung dienen, nicht als Abrechnung des Codex-Abonnements. Kein Sieger allein aus Gesamt-Tokenzahlen verschiedener Modelle; Qualitaet zuerst. Kleine Stichprobe ist keine statistische Stabilitaetsgarantie.

- [x] Testtreiber mit Zeitgrenze und bereinigter Beweissicherung vorbereiten.
- [x] Erst Delegations-Smoke-Test; bei Infrastrukturfehlern Vergleich stoppen und Ursache dokumentieren.
- [x] A/B-Vergleich erst bei erfolgreicher echter Delegation.

## Schritt 3: Astra-Referenz und Bericht

- [x] Nur bei erfolgreicher Konfiguration/Delegation denselben Aufgabensatz mit Astra/medium allein ausfuehren; keine Unteragenten.
- [x] Gemessene Ergebnisse von fehlender Abrechnung, Desktop-Profilaktivierung und Grenzen trennen. Keine Hermes-Aenderung, keine Gesamtfreigabe.

Freigabe: Der Betreiber hat beide Varianten, schrittweise Konfiguration und anschliessenden Vergleich ausdruecklich bestaetigt. Kein erneuter Planfreigabeschritt erforderlich. Keine Git-Commits im uebergeordneten persoenlichen Repository.

Abgeschlossen: 18 Wertungsläufe, 18 fachlich korrekte Antworten, 18 bestandene Laufzeit-/Routingprüfungen. Die eine nicht vorgeschriebene Statusbezeichnung bei B wurde transparent zusätzlich semantisch bewertet. Bericht: `docs/verification/CHAT_ROUTING_AB_2026-09-24.md`. 29 ausschließlich synthetische Testaufgaben samt Kindern archiviert; Belege erhalten.

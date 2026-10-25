# Lokale Kontextaufschlüsselung — 16.09.2026

Unverändertes Medium; keine Modellanfragen oder produktiven Routingänderungen. Aktuellen aurelia-integration-Kontext über ScopeService aus einer temporären SQLite-Sicherung rekonstruiert; Projektquellen lokal gelesen. Das produktive Journal wurde ausschließlich über mode=ro geöffnet. Die Kontextbildung erfolgte mit require_egress=False; sie beschreibt den aktuellen Lesestand, nicht die exakten historischen Prompts. Die eigentliche Plananweisung und der spätere Modellplan sind in den nachfolgenden Kontextgrößen nicht enthalten.

## Größen

| Bestandteil | Zeichen der kompakten JSON-Darstellung vor Matrixreferenzen |
|---|---:|
| Projekte einschließlich Quellen-/Gedächtnisauszügen | 44.925 |
| Zentrale Governance-Quellen | 14.665 |
| Governance-Matrix | 14.617 |
| Aufnahmebelege | 12.199 |
| Aufnahmestatus | 2.662 |
| Betreiberentscheidungen | 2.288 |
| Registrierungsmetadaten | 917 |

Review-Regel plus Evidenz ohne bisherige Verdichtung: 95.933 Zeichen. Mit vorhandener Formatverdichtung und identischen Matrixreferenzen: 91.269 Zeichen. Bereits eingespart: 4.664 Zeichen bzw. 4,86 %. Die Einzelbestandteile oben sind Messgrößen vor der Referenzbildung, keine additiven Anteile des endgültigen Prompts. Zeichen sind keine Tokens; weder Token- noch Kostenersparnis hieraus behaupten.

## Exakte Wiederholungen

Untersucht wurden identische vollständige Stringwerte ab 160 Zeichen. Nach Zählung ihrer vollständigen JSON-Darstellung in der tatsächlich kompakten Evidenz verbleiben fünf Gruppen:

| Kategorie | Wiederholte Zeichen oberhalb einer einzelnen Kopie |
|---|---:|
| Freigabe-/Abnahmebegründungen in Betreiberentscheidungen und Matrix | 1.667 |
| Warnungen in Projektbefunden und fehlenden Aufnahmenachweisen | 578 |
| Summe | 2.245 |

Das entspricht höchstens 2,46 % des gemessenen aktuellen Regel-/Evidenztexts, noch ohne Aufwand für neue Referenzen, Auflösungsregeln oder Prüfungen. Es ist keine belegte Nettoeinsparung. Die Fundstellen sind fachlich mehrfach zugeordnet: Betreiberentscheidungen begründen konkrete Freigaben; die Matrix zeigt deren Anwendung. Warnungen sind sowohl Quellenbefund als auch Aufnahmehindernis. Ungeprüftes Entfernen kann Nachvollziehbarkeit oder Modellinterpretation beeinträchtigen.

Grenzen: keine Volltextanalyse semantisch ähnlicher Passagen, keine Erkennung beliebiger Teilstringüberlappungen, keine Aussage über kürzere Wiederholungen. Unterschiedliche Quelle und Belegrolle sind nicht allein wegen ähnlichen Wortlauts redundant. Der Bericht zeigt keine gemessene Einsparung durch neue Chats oder Übergabezusammenfassungen. Rohdaten enthalten Pfade, Größen und SHA-256 statt Quellentexte: artifacts/context_audit_2026-09-16.json.

## Priorisierung

1. Bestehende verlustfreie Verdichtung und Medium beibehalten. Kein weiterer Referenzmechanismus allein für den kleinen hier beobachteten Rest empfohlen.
2. Für spätere klar abgegrenzte Projektaufgaben den vorhandenen passenden Scope verwenden; notwendige gemeinsame Voraussetzungen erhalten. Die aktuelle Fünf-Projekte-Gruppenplanung darf nicht allein zur Einsparung in isolierte Einzelprüfungen zerlegt werden.
3. Vollständige Logs verfügbar halten, relevante Ausgaben gezielt lesen; vorhandene Nachweise nur bei passendem Quellenstand wiederverwenden. Kein Abbau erforderlicher Tests oder unabhängiger Reviews.
4. Kompakte Übergaben erst an echten Arbeitspaketgrenzen und nach Vollständigkeitsprüfung nutzen. Deren Nettoeffekt ist weiterhin ungemessen; kein automatischer Kontextverlust.

Fazit: Kein neu nachgewiesener großer, risikofreier Einsparhebel. Weitere Effizienz-Infrastruktur vorerst zurückstellen und die offenen Hermes-Funktionen fortsetzen. Unveränderte Produktionsfunktionen; deshalb keine Wiederholung der bereits bestandenen 34 relevanten Tests. Messarithmetik und Berichtsdaten separat geprüft.

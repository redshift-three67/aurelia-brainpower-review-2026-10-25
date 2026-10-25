# REST – konsolidierte Teilabdeckung nach T2c

Aktualisierung T3: Normalfall, OOM-Speicherlimit, vollständiger Prozessgruppenabbruch, Controllerverlust/Recovery, tatsächliche CPU-Drosselung und 47 Linux-TLS-Prüfungen auf Ubuntu belegt. Belegabgleich abgeschlossen: REST_T3_ABSCHLUSS_2026-09-20.md. Produktvarianten bleiben getrennt; nachstehende T2a/T3a-Zahlen sind historisch.

Fortschreibung T3a: inzwischen 90 lokale Tests bestanden (16 zusätzliche Journaltests). Separater Controllerprozess, persistente offene Belege, Fencing, Schreibschutz und SQLITE_FULL geprüft; siehe [T3a](REST_T3A_2026-09-20.md). B08 hat damit einen lokalen Persistenz-Teilnachweis. Echter Ubuntu-Worker-/Controllerausfall und Prozessrekonstruktion bleiben offen; B07/B09 unverändert ungetestet.

74 erfolgreiche lokale Tests sind **keine 74 vollständigen Vertragsfälle**. Die 25 Familien der Matrix vom 19.09. bleiben unten einzeln sichtbar. „Teilnachweis“ bedeutet nur synthetisches Lab; kein Produkt-GO. Variantenbelege stehen in `tests/test_contract_lab.py`, `test_contract_transport.py`, `test_contract_deadlines.py`, `test_contract_policy.py` und den Berichten REST_T1/T2A/T2B/T2C. Vollständige Laufdatensätze gemäß Produktmatrix einschließlich echter Manifest-/Schema-/Releasebindung stehen noch aus.

| Familie | Aktueller Nachweis | Noch offen |
|---|---|---|
| A01 | Lokale TLS-Analyse, ein Aufruf, Wertprüfung, unsigned Minimalpassport | Vollständiges Produktschema, Input-/Kernelbindung, Wirkungsbeobachtung |
| A02 | Synthetische Pflichtfelder, Typen, Version-/Operationsbindung | Vollständiges ABI-/Passport-/Manifestprofil |
| A03 | REST-entry im T1-Validator nur Metadatum | Ausführungssentinel und reale Python-/WASM-Regression |
| A04 | Festes Loopbackziel, Redirect abgewiesen, Sentinel ohne Zugriff | Produktzielauflösung, Schema-Fetch- und Zieländerungsvarianten |
| A05 | Synthetische Vertragsabweichungen erkannt | Reale Quell-/Abhängigkeits-/Konfigurationshashes und Driftbelege |
| A06 | TLS 1.3, Identität/CA, fehlende/fremde/abgelaufene/zukünftige Zertifikate geprüft | Produktions-CA und reales Zielprofil |
| A07 | Lokale Rotation/Sperre; Sperre auf bestehender Verbindung | Betriebsverfahren, verteilte Sperre und konkurrierende Ausgabe |
| A08 | Synthetische Grants/Mandanten/Entzug | Reale Sitzung, Datenobjekte, unabhängige Zustandsbelege |
| A09 | Strikter synthetischer Kontext und Bindungsprüfung | Echte delegierte Autorität, Header-/Direktzugriffsvarianten |
| A10 | Testuhr, Kontextablauf, Rechteentzug; zusätzlich Policyalterung | Produktdelegation und vertrauenswürdiger Zeit-/Authbetrieb |
| A11 | Granttrennung als Teilnachweis | Mandantenobjekte, Drafts und Cache vollständig ungetestet |
| A12 | Ausgewählte Fehlerantworten/Konsole ohne Marker | Erfolgsaudit und alle Produkt-/Proxylogschichten |
| B01 | 1-MiB-Ränder, Typen/Framing, Encodingabwehr | Allgemeines Streaming nicht unterstützt; Produktschema/Scopeentscheidung |
| B02 | 4-MiB-Ränder, chunked/fehlende Länge, Framing/Ergebnisprüfung | Produktpassport/Draftübernahme und Speicherbeobachtung |
| B03 | Echte verzögerte TLS-/Header-/Bodytests mit monotoner Frist | Zielplattform-/Produktpfad und Lastbedingungen |
| B04 | Zweiter Aufruf bei gehaltenem Slot gesperrt | Mandantenübergreifende Instanzprobe und dauerhaftes Journal |
| B05 | Clienttimeout hält Slot bis Callbackende | Harter Prozessabbruch und belegter unbekannter Ausgang |
| B06 | Abbruch ohne automatischen Retry; Aufrufzähler | Persistentes Journal, wiederholte manuelle Request-ID |
| B07 | Ubuntu: cgroup-Limits, positive CPU-Drosselzähler, OOM bei 128MiB/Swap0 und vollständiger Abbruch unkooperativer Prozessgruppe belegt | Modulbezogene Produktionslimits und reale Produktintegration |
| B08 | Lokale Crash-/Persistenz-/Fencingtests; Ubuntu Controllerexit, unknown bei weiterlaufendem Worker, Runtime-Ende, Recovery ohne Replay und released_unknown/active0 vollständig belegt | Übertragung auf reale Produktprozesse und deren Journalverträge |
| B09 | Synthetische Ubuntu-Läufe mit Paket-/Unitbindung, eigenen Rücknahmen und Fremddienstvergleich einschließlich Controllerverlust; T3e abgeglichen | Reale Produktinstanz und deren Sandbox-/Readiness-/Rücknahmevertrag |
| C01 | Nicht ausgeführt | Separater D18-/Step-up-/CopyGuard-Vertrag |
| C02 | Nicht ausgeführt | Separater Idempotenz-/Transaktionsvertrag |
| C03 | Nicht ausgeführt | Separater WS-/Replayvertrag |
| C04 | Nicht ausgeführt | Separater Job-/Persistenzvertrag |

Nächste Reihenfolge: Aurelia-/Modul-Templates-Voraussetzungen abgleichen → offene A/B-Produktvarianten → separate Abnahmeentscheidungen. C-Erweiterungen und Erstmodulwahl bleiben getrennt. Keine Prozentzahl aus dem Quotienten bestandener Labtests ableiten.

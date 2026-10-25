# P3 – Radi144 API-Parameterreferenz

Der Betreiber bestätigt am14.10.2026 die Empfehlung: Originalzustand erhalten, bekannte Vertragslücke dokumentieren, P3 fortsetzen. Wunschparameter, wirksam weitergereichte Parameter und beobachtete Antwortwerte werden getrennt erfasst. Dies ist keine Freigabe einer Produktkorrektur.

## Begrenzter Entwurf

Ein neues Standardbibliotheks-Prüfwerkzeug charakterisiert genau den originalen API-Analyseeinstieg `analyze_matrix_resonance` und sieben direkte Übergabe-/Antworthelfer aus der hashgebundenen Datei `app/api/resonance.py`. Die Routingdekoration wird ausschließlich beim AST-Laden ausgelassen; Funktionskörper bleiben unverändert. Schemas und Engine werden nur gelesen/gehasht, nicht importiert oder instanziiert. Der bekannte Originalbefund wird als erwarteter Iststand geprüft, nicht als neue Störung und nicht als Fehlerfreiheit gewertet.

Verwendete Originalfunktionen: `analyze_matrix_resonance`, `_build_client_data`, `_requires_precomputed_signature`, `_mirror_api_session`, `_split_focus_sequence`, `_build_response`, `_apply_request_amplifier`, `_restore_request_amplifier`. Ein Spy ersetzt die gesamte Rechenengine. In-Memory-Doubles ersetzen Klienten-/Sessionservices, Pydantic-Response, vorberechnete Signatur, Logger und Zeit-/ID-Erzeugung. Diese Grenzen werden im Ergebnis ausdrücklich ausgewiesen. Kein HTTP-/FastAPI-/Pydantic-/Torch-/GPU-/Dateisystem-/Autorisierungsnachweis.

Die native Coroutine wird ohne Eventloop einmal bis zum Abschluss geführt. Unerwartete Suspendierung ist ein Werkzeugfehler. Ein Auditguard sperrt während Originalaufrufen Datei-I/O, Imports, Codegenerierung, Netzwerk, Prozesse, Registry und ctypes. Der Guard ist kein Betriebssystem-Sandboxversprechen. Das Kind schreibt keine Ergebnisdatei; der äußere Controller übernimmt stdout/stderr und Belege in den eigenen Prüfpunkt.

## Acht feste Fallgruppen

1. Vollständige tatsächlich weitergereichte Parameter, Sessionkonfiguration, Antwort/IDs/Hardware und Amplifier-Rücknahme bei erfolgreicher direkter Anfrage.
2. Nur CUDA-/Quantum-Wunschflags und Iterationen ändern: Engine-Kwargs bleiben gleich; Requestflags ändern die gespeicherte Konfiguration, Iterationen fehlen dort.
3. `calculation_mode` getrennt von Quantumflag: precision/quantum werden übergeben; keine echte Zufallsquelle oder Berechnung.
4. Signaturvorbereitung wird nur gemäß originalem Entscheidungsgate aufgerufen; genaues Sentinelobjekt wird zur Spy-Engine durchgereicht. Keine Signaturformel oder Bild-/Geo-/Katalogdatei ausführen.
5. Fehlende Eingaben: originaler400-Pfad und Amplifier-Rücknahme, keine Berechnung/Session.
6. Kontrollierter Enginefehler: originaler500-Pfad, keine Session, Amplifier-Rücknahme.
7. Kontrollierter Sessionfehler nach Berechnung:500, keine Antwortheader, Amplifier-Rücknahme.
8. Kontrollierter Antwortfehler nach Sessionerstellung:500 bei bereits gespeicherter synthetischer Session und gesetzten Headern; kein atomarer Gesamterfolg behauptet.

## Nachweis und Zuständigkeit

Luna/max besitzt nur neues Werkzeug und dessen Tests im eigenen neuen Prüfpunkt; keine Original-/Produkt-/Statusänderungen. Root besitzt Controller, Entwurf/Plan, Ausführung und Abschluss. Astra/medium prüft die eingefrorenen Bytes SPEC→QUALITY vor Originalausführung und den Ergebnisvergleich danach. Ein bewusst fehlschlagender Werkzeugtest kommt vor Implementierung; Rot-/Grünbytes und Exitcodes erhalten. Zwei frische Kindläufe vergleichen vollständige stabile Fallobjekte und Quellen-/AST-/Werkzeugbindungen. Zeit, Laufkennung und Ressourcen separat halten.

Vorherkopien der relevanten Statusdokumente vorhanden. Kein Gitcommit, Indexeingriff oder Produktworktree nötig: ausschließlich additive lokale Test-/Dokumentationsartefakte; bestehende WIP und Produktquellen bleiben unverändert. Abschluss mit Manifest, Archiv und Rücklesekontrolle. P3 insgesamt bleibt offen; P4 vor P5 unverändert.

# T2 – erster echter Transportnachweis

Genehmigt: Betreiberauftrag „mit T2 weiter“. Umsetzung zunächst als abgeschlossener T2a-Schnitt: TLS-1.3/mTLS, explizite Dienstzulassung, synthetische Analyse/Delegation, Sperre und Rotation. T2-Gesamtabnahme bleibt bis zu den weiteren Größen-/Frist-/Abbruchvarianten offen.

Dateien: `contract_lab/transport.py` (nur lokale Testverbindung, kein Produktionsadapter), `tests/contract_tls_fixture.py` (temporäre Test-CA/Zertifikate), `tests/test_contract_transport.py` (echte lokale HTTP/TLS-Tests), datierter Bericht unter docs/verification.

Entscheidungen: Python ssl/http.client; festes IPv4-Loopbackziel, keine Proxy-/URL-/Redirectfunktion; TLS exakt 1.3 auf beiden Seiten. Server fordert Clientzertifikat, zusätzlich aktuelle DER-Fingerprint-Allowlist pro Anfrage. Test-CA über vorhandenes Git-OpenSSL, keine Installation/System-Truststoreänderung. Schlüssel ausschließlich im automatisch entfernten TemporaryDirectory; keine Zertifikate in Repository oder Berichten. Test-HTTP-Anfrage enthält genau context und payload mit ganzzahligem value. Ganze Zahlen begrenzt auf 0..100, Ergebnis value*2; ausdrücklich unsigned, synthetic Passport.

RED/GREEN: erst Tests für positive Verbindung, fehlendes/fremdes/nichtzugelassenes Zertifikat, falsches Serverziel, TLS1.2-Ablehnung, Rotation/Sperre, abgelaufenen Kontext, fremden Mandant und ungültigen Payload schreiben. Dann minimalen Transport implementieren. Eigener serverseitiger Analysezähler ist Negativbeleg. Requestlänge fest begrenzt; nicht unterstützte Transfer-/Content-Encoding abweisen. Keine automatische Wiederholung; frische Verbindung pro Testclientaufruf. Sperrprüfung auf wiederverwendeter Testverbindung separat testen.

Nicht behaupten: dauerhafter CA-Betrieb, Zertifikatsablauf-/CRL-Abnahme, Widerruf laufender Jobs, allgemeine JSON-Schema-Unterstützung, komplette Streaming-/Slowloris-/Gesamtfristprüfung, gehärteter Produktions-HTTP-Server, echter Auth-Dienst oder Ubuntu-Prozessbesitz. Diese bleiben T2b/T3 und eigenen Produktgates zugeordnet.

Prüfung: `python -B -m unittest discover -s tests -p test_contract_transport.py -v`, anschließend zusammen mit T1 über `-p test_contract*.py`. Jeder Testdienst auf dynamischem Loopbackport, sichere shutdown/join-Reihenfolge, kein Zugriff auf Governor-Port 8787. Medium; kein Low-Wechsel.

# RadiWorks – begrenzte Token-Framing-Korrektur

> Ausführung lokal mit getrenntem Worker und unabhängigem Review; keine erneute Materialfreigabe aus diesem Plan ableiten.

**Ziel:** Den aktuell reproduzierten Token-Parserfehler in einem neuen, getrennten Kandidaten korrigieren. Historischen Fehlversuch und dessen Marker vollständig erhalten.

**Architektur:** Der feste anonyme HTTPS-Endpunkt liefert aktuell HTTP200 mit Chunked-Framing. Ein eigener begrenzter Body-Leser akzeptiert nur eindeutiges unterstütztes Framing und vollständig abgeschlossene Antworten. TLS, öffentliche IPv4-Adressen, Token-Schema und Blob-Regeln bleiben erhalten. Keine Produktänderung.

**Technik:** Python-Standardbibliothek, synthetische echte HTTPResponse-Fixtures; kein lokaler Produktlauf, keine neue Abhängigkeit.

**Stand21.10.2026:** Body-Leser, Integration und EOL-Korrektur abgeschlossen; Quellen-/Beleghashes fuer125 Kandidaten- und9 EOL-Tests erneut bestaetigt, kein heutiger Testwiederholungslauf.53 V4-Dateien sowie alte52/19 und23 Diagnosebelege unveraendert. Vorhandener unabhaengiger SPEC-/QUALITY-Review ohne materiellen Befund und gespeicherte native Vorpruefung bestaetigt. Lokaler Abschlussblocker durch erfolgreiches Zuruecklesen aufgeloest; keine neue Serveraktion. RESULT/INDEX_ALL/MATERIAL_APPROVAL_READY vorbereitet. Letztes Gate bleibt neue konkrete Betreiberfreigabe; kein Materialstart.

- [x] Genau eine freigegebene Metadatenabfrage; Parser lehnt Chunked vor Body-Read ab. Vorher-/Nachher-Erhaltungsprüfung erfolgreich; keine Materialprozesse oder Änderungen. Bericht: `runtime/rw-token-diagnostic-20261020/native-token-01/report.json`.
- [x] Unabhängige Astra-Einordnung: aktueller Fehler reproduziert; historische Ursache bleibt unbewiesen. Keine Ausführungsfreigabe aus dem Review.
- [x] Worker-Dateien `runtime/rw-token-fix-20261020/token_body.py` und `test_token_body.py`: zunächst nachweislich fehlschlagende Tests, danach begrenzter Body-Leser. Grenzen: 16.384 dekodierte Bytes, 65.536 Wire-Bytes, 256 Chunks, 1.024 Bytes pro Framingzeile, 8.192 Trailerbytes, 10 Sekunden kooperative Body-Lesezeit einschließlich verbleibendem Socket-Timeout. Keine harte DNS-/Header-/OS-Gesamtdeadline behaupten.
- [x] Parent erstellt getrennte Token-Integration und Regressionstests. Doppelte/mehrdeutige Header, TE+CL, nicht unterstützte Kodierung, unvollständiges Framing, Übergröße und Zeitüberschreitung bleiben Fehler. Blob-Code bytegleich erhalten.
- [x] Frischer vollständiger relevanter Testlauf, Quellen-/Beleghashes, unabhängiger SPEC-/QUALITY-Review; Befunde vor Freigabe schließen.
- [x] Konkretes V4-Materialpaket mit eigenem Verzeichnis/Units, erhaltenen alten Markern, Grenzen und Hashbindungen vorbereitet; finale Belege lokal zurueckgelesen.
- [ ] Neue ausdrueckliche Betreiberfreigabe fuer genau einen V4-Materiallauf einholen. Vorher keine Ausfuehrung; Entpacken, Import, Container, Build, Produkt- und Budgetaenderungen ausgeschlossen.

Der erfolgreiche Token-Kandidat allein belegt weder einen erfolgreichen Materiallauf noch die Annahme der Build-Laufzeit. Bestehende Schutzgrenzen und spätere R2-/P3-/P5-Gates bleiben bestehen.

Die Bytewerte sind Annahme-/Verwerfungsgrenzen des Body-Lesers; zum Erkennen einer Überschreitung kann begrenzter Vorgriff nötig sein. Der Framingzähler umfasst ab `response.fp` verarbeitete Body-/Framingbytes, keine vorher gepufferten Bytes, HTTP-Header oder TCP-/TLS-Overhead. Nicht unterstützte Chunk-Extensions werden bewusst abgelehnt. Protokoll-/Bibliotheksreferenzen: [RFC9112, Abschnitt7.1](https://www.rfc-editor.org/rfc/rfc9112.html#section-7.1), [Python3.12 http.client](https://docs.python.org/3.12/library/http.client.html).

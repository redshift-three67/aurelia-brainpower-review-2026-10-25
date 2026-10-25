# RadiWorks B1: gespeicherter Rehash und TAR-Inventur

**Goal:** Ein rein lokal getesteter, begrenzter Datenpruefer fuer bestehende gzip-Layer; keine Extraktion, kein Serverlauf und keine Container-/Buildfreigabe.

**Architecture:** Getrenntes Verzeichnis `runtime/rw-b1-archive-20261023`. Eine inkrementelle physische TAR-Inventur verarbeitet kleine Klartextchunks, waehrend der bewahrte gzip-Pruefer komprimierten SHA, diff_id und Laengen erneut berechnet. Ein Nur-Lese-Dateiadapter bindet den offenen Descriptor vor/nach dem Lesen an die erwartete Identitaet. Eine separate Bilanz nennt Daten-/Eintragszahlen und explizite Unbekannte statt eine Entpackfreigabe abzuleiten.

**Tech Stack:** Python-Standardbibliothek, unittest, synthetische TAR/gzip-Fixtures, Prozess-/Netzsperre, SHA-Bindungen. Nutzer hat diesen lokalen Vorbereitungsschritt unter Wahrung der bestehenden Gates freigegeben. Designfragen ohne Betreiberentscheidung werden konservativ geloest; keine erneute pauschale Designfreigabe.

## Abgegrenzte Wahl

Ein unbeschraenkter tarfile-Iterator kann Erweiterungsdaten intern puffern. Ein eigener vollstaendiger Extraktor waere fuer B1 zu breit. Verwendet wird deshalb ein strikt begrenzter Streaming-Inventarparser; Standardbibliothek nur fuer Headerdekodierung, keine Extraktions-API. Nicht unterstuetzte Semantik fuehrt zu expliziter Ablehnung oder verhindert jede belastbare Extraktionsbilanz.

## Vertragsgrenzen

- `TarInventory(check, max_members=100000, max_stream_bytes=4294967296)`; `feed(bytes)` nur Chunks1..65536, `finish()` liefert frisches JSON-kompatibles Ergebnis, keine Dateischreiboperation. Leerchunks erlauben. Echte Integer, keine bools; Deadlinepruefung vor Arbeit und waehrend der Verarbeitung.
- Strikte512-Byte-Header, Checksumme, bekannte ustar/GNU-Magie, deklarierte Laengen/Padding, zwei Nullendbloecke und ausschliesslich Nullpadding danach. Abgebrochene Header/Payload/Endmarker und ungueltige Typen werden abgewiesen. Maximal65536Bytes Erweiterungsdaten,4096Bytes Pfad,1024PAX-Schluessel pro Erweiterung, kein unbegrenztes `read`/`flush`.
- Regular, Verzeichnis, Links und Sondertypen getrennt zaehlen. Effektive PAX-path/linkpath/size sowie GNU-longname/link mit begrenzten Daten; globale PAX-Semantik nur wenn eindeutig unterstuetzt. Sparse/negative Groessen/unbekannte Semantik werden abgewiesen. Keine Ausgabe freier Dateinamen oder Dateiinhalte.
- Pfade muessen relative POSIX-Pfade ohne NUL, Backslash oder Traversal sein; `./` wird normalisiert. Gleiche normalisierte Pfade innerhalb eines Layers werden abgewiesen. Linkziele werden nur als Daten inventarisiert; absolute/relative Ziele bedeuten keine sichere Extraktionsfreigabe.
- Ergebnis: `tar_stream_bytes`, `headers`, `members`, `types`, `regular_payload_bytes`, `regular_rounded_4096_bytes`, `path_components_total`, `whiteouts`, `accounting_complete`, `extraction_authorized=False`. Rundungswert ist nur regulaerer Datenblockanteil, kein physischer Peak oder Inode-Freigabebeweis. Links, Spezialtypen und nicht rein triviale Erweiterungen verhindern vollstaendige Bilanz. Alle zaehlenden Summen begrenzt; Bericht <=8192Bytes.
- `inspect_stream(...)` prueft bestehende Inhalte erneut; Klartextchunks gehen ausschliesslich an TAR.feed. Erwartete komprimierte Laenge/SHA, diff_id und exakte bekannte TAR-Streamlaenge sind vor Lesen typisiert gebunden. Jede Abweichung verwirft den Bericht.
- Dateiadapter: nur regulaere, eindeutige Datei; O_NOFOLLOW/O_NONBLOCK soweit vorhanden, kanonischer Pfad, exakte erwartete device/inode/size/mtime_ns, Vor-/Nach-fstat. Keine automatische Wiederholung, keine Reparatur oder Aenderung der Quelldatei. Keine Behauptung gegen privilegierte gleichzeitige Dateimanipulation.

## Aufgaben und Besitz

- [x] Worker besitzt ausschliesslich `tar_inventory.py`, `test_tar_inventory.py` und eigene RED/GREEN-Belege. Synthetische Standard-/PAX/GNU-/Link-/Traversal-/Groessen-/Checksum-/Abbruch-/Padding-/Deadlinefaelle zuerst RED, dann Implementierung.
- [x] Root besitzt `archive_rehash.py`, `test_archive_rehash.py`, neue lokale Kopie `material_bounds.py` und dessen unveraenderte Bestandspruefungen. Neuer optionaler `on_tar_chunk` wird vor jedem Datenverbrauch validiert und bounded vorgegeben; standardmaessiger Pfad bleibt erhalten.
- [x] Root implementiert bewachten Gesamtverifier, unveraenderte Ursprungsbindungen, JSON-/Bytegrenzen und Bilanztests. Keine native Paketbildung aus einem unreviewten Parser.
- [x] Echte lokale RED/GREEN-Runs, vollstaendige relevante Tests, unabhaengiger Astra/medium-Review, Fehlerkorrekturen mit neuen Belegen; erst danach lokalen Checkpoint und konkreten Stand fuer naechsten Job festhalten.
- [ ] Native Job-/Cgroup-/Transportintegration bleibt ein separater nachfolgender Vertrag; erst nach dessen Tests/Review konkrete Ausfuehrungsfreigabe. Kein Import, Entpacken, Toolchainaufruf oder Containerstart in B1.

## Quellen und Aussagegrenzen

[OCI-Layerspezifikation](https://github.com/opencontainers/image-spec/blob/main/layer.md) beschreibt unter anderem Pfadduplikate, Links und Whiteouts; diese werden nicht als einfache regulaere Nutzdateien behandelt. Parserheader werden gegen die installierte Python3.12-Standardbibliothek und synthetische tarfile-Fixtures gegengeprueft. Die aktuellen7Serverblobs werden in diesem lokalen Block weder gelesen noch erneut heruntergeladen; echte Unterstuetzung dieser konkreten Archive bleibt bis zur separat zugelassenen Probe unbekannt.

## Verifizierter lokaler Abschluss

55 Tests bestanden,0Fehler/Failures/Skips;209 eingefrorene Eintraege vor/nach unveraendert. Acht Pythondateien, unabhängiger Astra/medium-Review ohne offene Blocker. Alle RED- und nicht akzeptierten Zwischenbelege bleiben erhalten. Noch kein natives B1-Paket, keine Serverblob-Leseprobe oder Extraktion.

Deadline ist kooperativ und unterbricht keinen blockierten OS-Read. Audit-Hooks sind keine Betriebssystem-Sandbox. storage_summary verarbeitet vertrauenswuerdige lokale Bericht-Dicts und authentisiert kein externes JSON. Der Pfadkomponenten-Zustand ist zusaetzlich auf500000 begrenzt; Nichtverzeichnis-Praefixkonflikte werden beidseitig abgewiesen. Alte NUL-Typ-Verzeichnisse werden gemaess TarInfo.type klassifiziert, regulaere Endkomponenten / oder /. abgewiesen. Die4-KiB-Rundung hat feldspezifische Einzel-/Aggregatgrenzen und bleibt nur ein Nutzdaten-Subtotal.

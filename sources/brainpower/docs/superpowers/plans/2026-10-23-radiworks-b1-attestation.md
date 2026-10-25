# B1: fehlende Eingangs-/Laufzeitbindungen zuerst belegen

**Goal:** Ein konkretes lokal getestetes/reviewtes Paket fuer eine rein lesende Metadaten-Vorpruefung vorbereiten. Keine native Ausfuehrung ohne neue Freigabe.

**Evidence:** Der V6-Transportbeleg bindet alle sieben Inhaltsdigests und Laengen, filtert aber die Dateideskriptor-Identitaeten heraus. Linux-Python-/tarfile-Identitaet fehlt ebenfalls. B1 darf diese Werte weder erraten noch die aktuelle Windows-Standardbibliothek als Linux-Beweis verwenden.

**Design:** Die neue Probe verwendet den exakt gehashten V6-Statusbootstrap nur fuer dessen bereits gepruefte importierte Helfer und Initialisierung. Danach prueft sie unter demselben Runtime-Lock frische V6-Erhaltungs-/Stopbedingungen, die vorhandenen Launch-/Worker-/Completed-/Postcheck-Belege und die Blob-Metadaten. Sie liest keine Blob-Inhalte. Eine kleine synthetische TAR-Headerprobe und SHA-Werte der tatsaechlichen Standardbibliothek markieren die eng begrenzte Laufzeitbeobachtung. Keine Behauptung einer vollstaendigen Python-/Parserabnahme.

## Aufgaben

- [x] Reiner Antwortvertrag mit strikten Typen, genauer7-Layer-Menge, fest gebundenen Digests/Laengen, vier numerischen Identitaetsfeldern, festen False-Schutzflags, kanonischen Beleg-SHAs und begrenzten Laufzeitmetadaten; unbekannte/fehlende Felder zurueckweisen. RED/GREEN zuerst.
- [x] Pure Probe-Bausteine fuer Headerverhalten und Metadatenpruefung, serverseitige Belegkonsistenz vor/nach Snapshot, keine Aenderung von Units/Belegen oder Blob-Inhalten. Tests mit synthetischen Belegen/IO.
- [x] Reproduzierbarer Generator mit gehashtem V6-Header, probe-/validatorbytes und eigenem neuen Paket-SHA; kein geerbter __main__-Status/Finalisierungsaufruf. Echten erzeugten Import-/Antwortpfad synthetisch pruefen.
- [x] Begrenzter Einmal-Runner: Review-/Paket-/Sourcebindung, vorhandener geschuetzter Ops-Client, IPv4, beobachtendes180s-Warten/Drain (120s nominelle Summe der Schutzkommandolimits), strikter Antwortvertrag und persistierter unbekannter Ausgang bei Timeout/Fehler. Keine Wiederholung oder Material-/Lifecyclefreigabe.
- [x] Kompatible Tests, Negativ-/Drift-/Timeout-/Persistenzfaelle, alte Belege und neue Paketgroesse pruefen; unabhängiger Astra/medium-Review. Checkpoint und genaue native Freigabefrage erst nach geschlossenem Review.

## Sicherheitsgrenzen und Ergebnis

Kein SSH-Aufruf in dieser lokalen Vorbereitung. Auf dem Server sind fuer eine spaetere Probe fest gebundene Metadaten-/Stdlib-Lesezugriffe, kleine synthetische Speicherfixtures und die vorhandenen Schutzkommandos vorgesehen. Die unveraenderten Erhaltungsgates lesen zudem die gebundenen Produktquellbytes, preview_entry.py und worker.py ausschliesslich fuer Schutzhashes; diese Quellen werden nicht ausgefuehrt. Keine Blob-Deskriptoren zum Inhaltslesen oeffnen, keine Registry/Clients/Schluessel lesen, keine Start-/Stop-/Reset-/Import-/Extraktions-/Container-/Buildbefehle. Der vorhandene Betriebsstop wird nur geprueft.

Ein positives Ergebnis ist eine punktuelle Metadaten-/Verhaltensbeobachtung, kein unabhaengiger Inhaltsrehash, keine nachtraegliche Frischbestaetigung alter Postcheckbytes und keine B1-Ausfuehrungsfreigabe. spaetere B1-Pakete muessen die gewonnenen Identitaeten/SHA-Werte erneut eng binden und bei Drift abbrechen. Beobachtungsbudget ist keine harte Gesamtwallclock; verlorene SSH-Antwort bedeutet unbekannt und kein automatischer Retry.

**Lokaler Abschluss 23.10.2026:** Paket7724435687602971756f5dd0d0d6e96766756f31a90c545399f885d18cfff800,70820Bytes;46Tests0Fehler/Failures/Skips,246eingefroreneEintraege gleich. Unabhaengiger Astra/medium-Review0offeneBlocker. Beide P1 durch RED/GREEN geschlossen: falscher Completed-Pfad und erneutes Lesen nach Hashpruefung. Gespeichertes Paket mit frischer Erzeugung und echtem gebundenem Loader offline verglichen;0Prozess-/Netzaufrufe. Native Probe noch nicht freigegeben/gestartet. Genauer Umfang: runtime/rw-b1-attestation-20261023/NATIVE_REQUEST.json.

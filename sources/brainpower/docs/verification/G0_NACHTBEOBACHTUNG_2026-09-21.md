# G0: nächtliche Betriebsbeobachtung

Nach Wiederaufnahme am21.09. lesend per SSH geprüft: ca.15h Uptime, keine failed Units, PostgreSQL16/main weiter down, Backup-Timer disabled. Keine Konfigurationsänderung, kein neuer Lastlauf.

Alle vom Journal gelieferten JSON-Healthberichte des aktuellen Boots ausgewertet:162Berichte von20.09.17:39:00UTC bis21.09.08:36:01UTC (knapp15h). Kein Bericht healthy=false, keine errors oder failed_units. Größte Zeitspanne zwischen zwei Berichten367,558s. Letzter Bericht beideRAIDdegraded0, NVMe passed ohnecritical_warning/media_errors, NTPsynchron.

Lokale Belege: artifacts/health-overnight21-summary.json und health-overnight21-reports.json. JSON wurde lokal geparst/neu serialisiert; kein byteidentischer Journalexport. Zeitstempel der Berichte können dabei lokal mit +02:00 dargestellt sein; Zusammenfassung explizit UTC.

Dieser Nachweis erweitert die vorherige kurze Beobachtungsstrecke. Er beweist keinen ununterbrochen fehlerfreien Zustand zwischen Messpunkten, keinen repräsentativen Produktlasttest und keine vollständige G0-Abnahme. Soak-Kriterien und unabhängige Recovery bleiben getrennt.

Gezielte Ablagenprüfung: fünf erwartete Projektverzeichnisse unter /srv/build sichtbar, Zugriffsschutz0700. /srv/aurelia-Unterbäume für SSH-Benutzer nicht lesbar. Daher keine Aussage, sie seien leer; Root-Metadatenprüfung als nächster Schritt. DB-Inhaltsprüfung nicht durch Start des Hauptclusters erzwingen.

Neue Computer-Use-Funktion initialisiert und Fensterliste geprüft: kein eindeutig identifizierbares KVM-Fenster sichtbar. Keine Tastatureingabe oder Appänderung vorgenommen. Frühere pauschale Aussage über fehlende Computer-Use-Werkzeuge gilt für diese Sitzung nicht mehr; direkte KVM-Bedienbarkeit bleibt bis zur Prüfung des geöffneten Fensters unbestätigt.

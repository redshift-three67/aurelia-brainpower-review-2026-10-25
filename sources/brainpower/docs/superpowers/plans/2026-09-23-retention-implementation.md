# Aufbewahrung 7/4/6 – Implementierungsplan

**Ziel:** vorhandene abgeglichene Vorschau in eine begrenzte, überprüfbare Bereinigung überführen. Aktuelle Betreiberentscheidungen zu zurückgestelltem Rescue und zweiter Kopie bleiben wirksam. Medium.

**Umfang:** ein eigener Retention-Helfer mit preview/apply und optionalem prune, keine Änderung am bestehenden Backupablauf. Gleiche exklusive Sperre wie Backup. Erst nach aktuellem erfolgreichem Lauf, vollständiger Repositoryprüfung, frischem Snapshotabgleich und Schutz des neuesten verifizierten Standes. Host/Tag und Repository-ID fest. Fremde Profile unverändert. Apply entfernt ausschließlich explizit gerade geprüfte IDs, niemals eine ungeprüfte pauschale Policy. Nachprüfung der Snapshotmenge; Prune getrennt und begrenzt, danach Repositorycheck. Kein Timer ohne gesonderte Betriebsabnahme.

- [x] Tests zuerst für vollständig disjunkte/abdeckende Keep-/Remove-Mengen, richtige Profile, frischen Erfolgsstand, Schutz des jüngsten Snapshots und Driftabbruch. Acht bestanden.
- [x] Implementierung `artifacts/server-retention23.py` samt synthetischem Linux-Roundtrip in eigenem lokalem Testrepository; erfolgreiche Wiederherstellung nach Entfernung künstlicher Zwischenstände und Test-prune nachgewiesen.
- [ ] Hashgebundener Rootstarter für reale Vorschau/Installation; zunächst keine echte Löschung. Anschließend konkrete IDs/Verhalten reviewbar anbieten und tatsächlichen Apply-Schritt ausführen lassen. Bisherige allgemeine Zurückstellungen sind keine Löschfreigabe.
- [ ] Aktuelle Evidenz und Grenzen in kurzen Status übernehmen. Keine vollständigen Langzeit-/RTO-Behauptungen.

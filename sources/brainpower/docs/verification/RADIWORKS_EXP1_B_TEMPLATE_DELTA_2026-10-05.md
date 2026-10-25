# RadiWorks EXP1-B — vorgemerkter Modul_Templates-Abgleich

Entwurf zum geprüften Kandidaten `runtime/rw-exp1b-20261005`; keine Änderung der kanonischen Standards, kein neuer Hostvertrag oder S4.8-Go.

- Persönlicher Kontext: optional `placeKind` mit exakt `residence|birth`; fehlend bedeutet Legacy/unbekannt. Genau ein `place`-Wert; keine birthPlace/residencePlace-Zweitfelder.
- UI: exklusiver Ortstyp, Wechsel leert Eingabe, ausdrückliches Speichern; unbekannte Altangaben behalten unbekannte Bedeutung. Auswahl/Hilfe beschriftet, Tastaturfokus und320px geprüft. Bild zunächst immutable Kontext.
- Lokaler Patch: Typwechsel muss `place` gleichzeitig explizit liefern oder leeren;409 sonst. Vollständiger Ersatz mit unvollständigem Typwechsel422. Kontextrevision steigt bei wirksamer Änderung; bestehende Aufträge behalten Snapshot.
- Snapshot-Schema1 akzeptiert zusätzlich den optionalen Typ. Alte Bytes/Prüfsummen bleiben gültig. Neuer Reader prüft Datumsplausibilität gegen gespeicherten UTC-Aufnahmetag+1 Zeitzonentoleranz statt Systemdatum; Eingaben weiterhin aktuelle Zukunftsprüfung. Digest keine Authentifizierung.
- EXP1-B: reine skalare Vorbereitung mit Formelversion, Quellenhash, Kontextdigest/-revision/Fall-ID, Komponenten/Gewichten und expliziten Nutzungsparametern. Keine neue API/Queue/Jobausführung oder Rankingabnahme. Original bleibt Standard; Fokus benötigt später belegten Katalogmatch. Wohnort/untypisierte Orte/Bild keine numerische Komponente.
- Vor Integration: tenant/client/job/context/session binding für EXP1-C und unabhängige Vergleichspersistenz testen, Ressourcen und CPU-Abhängigkeiten pinnen. Keine semantische KI-Suche oder neue Formel ohne Besprechung.
- Rollback: Alte Programmstände kennen neue typisierte Snapshots nicht. Nicht blind ältere Binärdateien auf künftig typisierte Live-Daten setzen; kontrollierte Daten-/Programmversion und separate Sicherung erforderlich. Derzeit keine Live-Datenmigration.

Gemeinsame Referenzen: bestehendes Aurelia-Design/Modul_Template-Designstandard bleiben maßgeblich, Rollen-/Berechtigungs-/Mandantengrenzen unverändert. Radi144-Verfahren sind Heuristiken; reproduzierbare Zahlen belegen keine medizinische Wirkung.

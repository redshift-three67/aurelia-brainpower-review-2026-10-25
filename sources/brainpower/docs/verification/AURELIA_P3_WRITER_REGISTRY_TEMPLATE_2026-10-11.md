# P3 – Writer, Registry und lesender Template-Abgleich

Stand: 11.10.2026. Statischer Teilnachweis; keine vollständige Modul- oder Laufzeitabnahme. Die freigegebene Reihenfolge bleibt P3-Referenzen → P4 siebenmodulige Matrix mit Aurelia/Templates → P5 Datenstrukturentscheidung. Normative Verträge und Umsetzung folgen getrennt in P6–P8.

| Teil | Tatsächlich erfasst | Weiter offen |
|---|---|---|
| RadiMorphic Writer | Zehn Quelldateien: Webstart → Top-N-Kindprozesse → Profilwriter → Reportregistrierung; Fehler- und Persistenzgrenzen | Writer-/Job-End-to-End, Konsolidierungs-/PDF-Interna, Fehler-/Abbruch-/Wiederholungsproben |
| Registry / Restore | Vier direkte Quelldateien der Publish-Kette; echte Windows-Handles und unveränderter POSIX-Ablehnungsguard statisch verfolgt | Vollständiger geprüfter Loader, positiver öffentlicher Backup-/Restorelauf; tatsächliche Linux-Ablehnungs-/Cleanup-Probe |
| Modul_Templates | Drei Dateien: MODULE_REGISTRY, MODUL_STANDARD, API_CONTRACT; Ist/Soll getrennt | Gesamter Host-/Bridge-/Schema-/Designabgleich und normative Synchronisierung nach der Datenstrukturentscheidung |
| Quellenbindung | Leitung hat 17 gebundene Einträge frisch nachgerechnet: 14 Morphic-Dateien plus drei Template-Dateien; HEAD/tracked-only Metadaten verglichen | Keine kontinuierliche Beobachtung, HEAD-Bytegleichheit, vollständige Repository- oder Runtimeprüfung |

## Für die Datenstruktur relevante Befunde

**Aufträge und Berichte:** Im untersuchten Top-N-Pfad existieren Web-Job-ID, Job-Owner, Roh-Session und abgeleitete Ordner-/Katalogsession. Letztere lautet beispielsweise `<Roh-ID>_TOP3_SESSION`, allgemein `_TOP{N}_SESSION`. Der Kindwriter registriert die Roh-ID; der Elternprozess liefert nach Validierung die abgeleitete Katalog-ID. Diese Zuordnung darf nicht durch ein gemeinsames unbestimmtes „session_id“-Feld ersetzt werden. Die Vollzuordnung bis zum Report-Reader bleibt offen.

**Mandanten:** Der Webstart übergibt `report_roots[0]` explizit. Ob dieser Root schon tenantgebunden ist, wurde nicht verfolgt. Der Job-Owner ist im Jobservice vorhanden; seine explizite Übernahme in den untersuchten Reportregistrierungsaufruf ist nicht belegt. Das ist eine offene Vertragskante, kein nachgewiesener Tenant-Bypass.

**Artefakte und Versionen:** Das geprüfte Manifest-Artefaktobjekt enthält ID, Session, Klient, Typ, Pfad, Label und Zeitpunkt; es bindet dort keinen Bytehash oder unveränderliche Inhaltsrevision. Artefaktliste, Sessionverknüpfung und Audit werden nacheinander gespeichert; ein späterer Fehler kann Teilbestände hinterlassen, obwohl der Wrapper `None` liefert. Auch JSON/HTML/TXT-Einzeldateischreiben belegt keine gemeinsame Mehrformattransaktion. Vor dem JSON-Schreiben erfolgen `round_scores_for_export` und `report_json_dumps`; genaue Rundungssemantik wurde nicht geprüft. Für P4 sind Auftrag, Versuch, Standort, Artefakt, Inhaltsrevision und Archivstand getrennt zu erfassen.

**Ubuntu-Ziel:** `_require_posix_source_inode_bound_publish` im gebundenen `source_registry.py:1250–1256` kehrt unter Windows zurück und wirft auf Nicht-Windows-Plattformen unbedingt. Erfolgreiches unverändertes Publishing über diesen Pfad ist damit unter POSIX nicht vorgesehen. Vorher können Handles und temporäre Snapshots entstehen; die spätere Prüfung muss Cleanup, temporäre Dateien und Zielunverändertheit getrennt beobachten. Kein ausgeführter Ubuntu-Test und keine Aussage zur Funktionsfähigkeit des gesamten RadiMorphic-Moduls.

**Templates:** Die historische Sechserkarte enthält RadiFarben nicht. Alte Blohm-/Thoms-Bezeichnungen sind keine belegten heutigen Modul-IDs. Der API-Sollvertrag enthält AetherOne-spezifische Funktionen; diese werden nicht automatisch Anforderungen aller Module. Versionierte modulspezifische Fähigkeitsprofile sind ein P4-Klärungsvorschlag, noch kein beschlossener Standard. Nullable Kontextfelder ersetzen laut vorhandenem Vertrag keine Autorisierung/Mandantentrennung. Die drei gebundenen Template-Dateien blieben bytegleich; der tracked-only Status einschließlich bestehender WIP blieb gleich. Andere WIP-Dateien wurden nicht gehasht.

## Nachweise und nächste Schritte

- [Writervertrag und zehn Quellenbindungen](../../checkpoints/Aurelia-P3-Morphic-Writer-Contracts-20261011/WRITER_CONTRACT.md).
- [Registry-/Templatevertrag und vier vorbereitete NOT_RUN-Prüfpakete](../../checkpoints/Aurelia-P3-Registry-Template-Contracts-20261011/REFERENCE_CONTRACT.md).
- [Frühere synthetische Backup-Referenzprüfung](AURELIA_P3_BACKUP_REFERENZEN_2026-10-11.md) und [Bericht-Handleprüfung](AURELIA_P3_BERICHT_REFERENZEN_2026-10-11.md) bleiben eigene begrenzte Laufnachweise; in diesem Block nicht erneut ausgeführt.

Als Nächstes den echten Schema-v8-Windows-Publish-/Restoreweg über einen zuvor gebundenen Loader und ausschließlich synthetischen Scratch prüfen. POSIX-Ablehnung/Cleanup und v7-Migration bleiben getrennte Pakete. Keine Dummy-Registry und keine Umgehung des bestehenden Guards. RF-E1 und weitere P0/P1/P2/P3-Nachweise bleiben offen; eine vollständige siebenmodulige Vergleichsmatrix ist noch nicht abgenommen. Drei Lovable-Module verteilen sich auf zwei Anwendungen: Copen/Bohm im Explorer, Thom separat; kein neuer GitHub-/Cloud-Aktualitätsnachweis in diesem Block.

Lokaler Vorher-/Nachher-Dokumentenprüfpunkt: `checkpoints/Aurelia-P3-Writer-Registry-Status-20261011-174307Z`. Enthält Quellenbindungen, Leitungsverifikation, Berichte, Reviewnotiz, vorherige Dokumente und rückgelesenes Manifest; alte Wiederaufnahme als vollständiger Bytesuffix erhalten. Dies ist keine F:-Vollsicherung oder vollständige Produkt-/Runtime-Wiederherstellung.

Tatsächliche Helfer: GPT-6 Luna/max für den begrenzten Writervertrag; GPT-6 Astra/medium für unabhängige Registry-/Template-/Writerprüfung. Leitung: Quellen-Nachrechnung, Konsolidierung und Prüfpunkt. Review ersetzt keine Betreiberfreigabe. Keine Produkt-/Live-/Cloud-/Office-/WSL-/Routing-/normative Templateänderung durch diesen Block; Originalalgorithmen erhalten.

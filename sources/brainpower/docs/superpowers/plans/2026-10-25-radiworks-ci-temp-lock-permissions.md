# RadiWorks CP1 – temporäre Lockdateirechte korrigieren

**Ziel:** Den im ersten nativen CI-Lauf erkannten Leserechtsfehler mit einer eng begrenzten lokalen Korrektur vorbereiten. Keine Wiederholung oder Veröffentlichung aus der Vorbereitung ableiten.

**Beleg:** Run40171409190, Controlcommit62f01d89253c71477bb6e5cd1b686ab59d5355e8. Checkout und204Quelldateien bestanden; festes Python-Basisimage geladen. Danach `Permission denied: /requirements.lock`. Build, Wheelprüfung und RadiWorks-Tests nicht erreicht. Native UID-/Mode-/Capabilitywerte fehlen; die Ursachenverkettung aus `umask077`, `cp` und `--cap-drop=ALL` ist eine starke statische Rekonstruktion.

**Isolierter Kandidat:** `runtime/rw-cloud-ci-permission-fix-prep-20261025`. Nur nach dem Kopieren `chmod 0444 "$work/requirements-linux-c3a.lock"` ergänzen. Originaldateien, Daten, Container-Capabilities, read-only-Mounts, Ressourcen, Timeout und Testauswahl unverändert lassen.

- [ ] Vorhandene geprüfte Baseline getrennt kopieren; alten Beleg-/Payloadstand erhalten.
- [ ] Regression zuerst: echten Shell-Copyblock mit synthetischen Dateien unter Git Bash prüfen; Zieldatei für alle Rollen lesbar und nicht schreib-/ausführbar, Inhalt und Quellmodus unverändert, Pfade mit Leerzeichen.
- [ ] Erwartetes Rot dokumentieren, dann genau eine chmod-Zeile ergänzen.
- [ ] Relevante lokale Gesamtprüfung und Syntaxprüfung; keine Linux-App/WSL/Docker-Runtime auf Windows starten.
- [ ] Unabhängiger Astra/medium-Review des konkreten Deltas und der Nativebelege.
- [ ] Neue Paketidentität/Umfang speichern. Erst nach neuer expliziter Einmalfreigabe genau ein weiterer CI-Lauf, vorab Kontingent/Kosten und tatsächliche Veröffentlichungsidentität prüfen.

Git-Bash-Tests beweisen keinen nativen Linux-DAC-/Container-Fixerfolg. Der neue echte CI-Lauf bleibt erforderlich. Der erste Einmalumfang ist verbraucht. Kein Cloud-/Pilotserver-Materiallauf, keine neue Securityprüfung oder Produktfreigabe. Kosten des vorgeschlagenen neuen Standardjobs unverändert:30Minuten nominal0,18USD reine Runnerzeit ohne ausreichendes Inklusivkontingent; tatsächliches Kontingent erneut prüfen.

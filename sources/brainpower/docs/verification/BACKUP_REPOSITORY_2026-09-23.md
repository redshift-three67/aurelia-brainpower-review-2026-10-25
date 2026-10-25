# Betriebsrepository vorbereitet, Automatik aus

23.09.2026: genehmigtes Paket einmalig ausgeführt. Ergebnis `repository_prepared_not_activated`. Kein produktiver Sicherungslauf und keine G0-Freigabe.

## Nachweise

- Paket `artifacts/server-backup-prepare23.py`, SHA256 `f0298a4091095425dce2cfa5e44891b4e1da29da5690f26a42030217d0f2155a`, lokal/servergleich.
- Unprivilegierter Linux-Selftest bestanden: synthetische Daten, vollständige Repositoryprüfung und Restore mit Inhalts-/Modusvergleich; `/tmp/aurelia-prepare23-selftest-m96irho_`.
- Rootstart über Chrome-KVM mit einzelnen Tastendrücken und kodiertem Python-Text; Übertragungs-SHA256 vor Ausführung verglichen. Starterhash `b618029f6c968f8635e3a3aab3176d2f659941fca108929256cec86785990a12`. Paket exklusiv rootgeschützt unter `/var/lib/aurelia-maintenance-packages/prepare-20260923/prepare.py` versiegelt.
- Bericht `/var/tmp/aurelia-backup-prepare23-result.json`, lokal `artifacts/backup-prepare23-report.json`, SHA256 `bccd43e757a0783481cdfed9b170e520c65169010003c1677fae0400821682c9`, lokal/servergleich.
- Berichtszeit `2026-09-23T13:48:46.789865+00:00`.

| Prüfung | Ergebnis |
|---|---|
| Bisheriger Schlüssel öffnet erwarteten alten Snapshot | Bestätigt |
| Neues getrenntes SMB-Repository | `aurelia-operations-v1` |
| Repository-ID | `8dd73248e24a470cb30e72fe7a0d15e8caf0278d654e08a03ff7a41d92b10c98` |
| Synthetischer Snapshot | `8590a841954d1ae4e4cbf438ccc0851fd2547bbc696eb13a1d739347f08ca0b7` |
| Vollständige Prüfung und synthetischer Restore | Bestanden |
| Eigener Mount entfernt / Originalzustand unverändert | Bestätigt |
| PostgreSQL 16/main | Frisch geprüft: inactive, MainPID=0 |
| `aurelia-backup-files.timer` | Frisch geprüft: disabled/inactive |

Kandidat: `/var/lib/aurelia-backup-deployment/prepare-20260923/candidate.json`. Bestehende `/etc`-Backup-Konfiguration nicht ersetzt/aktiviert. Zuvor falsch abgefragter Name `aurelia-backup.timer` meldete not-found; maßgeblich ist der korrekt geprüfte Name oben.

## Wartungszugang

Betreiber genehmigte neuen ED25519-Schlüssel für `klaus999`, Fingerabdruck `SHA256:oxxxYmTvHFfvUpI7rgniFdoX94j1t9SCd9c8N8ggefY`. Private Datei ausschließlich unter `C:/Users/Hubert111/.ssh/aurelia-maintenance-20260923-1326/id_ed25519`; Ordner-ACL nur für dieses Windows-Konto. Keine private Datei im Projekt/Snapshot.

Neuer Eintrag mit `restrict,expiry-time="20260924134551Z"`; neue Authentifizierungen enden am 24.09.2026 15:45:51 CEST. Ablauf beendet keine bestehende Sitzung. Alte Einträge/Rechte unverändert; vorher exklusives Backup `/root/aurelia-authorized-keys-before-20260923`. Keine Root-Anmeldung oder zusätzlichen sudo-Rechte eingerichtet. SSH-Login als UID1000 mit strikter KVM-verifizierter Serveridentität bestanden.

Chrome-KVM funktioniert für kontrollierte einzelne Tastendrücke. `ax.typeText` bleibt wegen bestätigter Zeichenwiederholungen ungeeignet. Sonderzeichen explizit mit Umschalttaste; kodierten Text vor Ausführung per SHA256 vergleichen. Keine pauschale Zusage fehlerfreier KVM-Texteingabe.

## Restarbeit

1. Gemeinsamen Ablauf für Dateien und konsistente DB-Sicherung vorbereiten/prüfen.
2. Vor Aktivierung RPO, Aufbewahrung und Fehlerbenachrichtigung mit Betreiber klären. RTO maximal12h ist Ziel, kein nachgewiesener Gesamtrestore.
3. Echten Betriebsbackup-Lauf, Wiederherstellung und Fehlererkennung abnehmen; unabhängige Schlüsselkopie erneut prüfen.
4. Unabhängigen Rescue-/ISO-Weg, Provider-/Hardwarepunkte, nötige Belastungsnachweise und G0-Abgleich abschließen.

Keine automatische Löschung, kein Prune, keine Aktivierung und keine Modulfreigabe aus diesem Teilnachweis.

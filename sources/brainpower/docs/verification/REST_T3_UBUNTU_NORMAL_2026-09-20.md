# T3 – erster Ubuntu-Normallauf bestätigt

Betreiberfreigabe und einmalige KVM-Rootausführung erfolgt. Berichtzeit: **2026-09-20T10:17:25.232662+00:00**. Der bereinigte Root-Nachweis wurde anschließend per SSH gelesen, lokal kopiert und auf konsistente Identität, Manifestbindung, Status, Journalabschluss und Rücknahme geprüft. Kein erneuter Start.

| Gegenstand | Beobachtetes Ergebnis |
|---|---|
| Lauf-ID | 0dccd173321a46d58b737b93b27fed7a |
| Runner | v2, SHA256 6a4d59d48fb8aeb63ab499fafaadaddb72de2010836500a45320490c98d41669 |
| Manifest | 5379aa7b6d45a25a93ba5a6b1a507e8281c3c99b0f4b555c562b7fffcd7b42f1 |
| Ergebnis | process_completed; Hilfsaufruf Rückgabecode 0 |
| Prozess | ended, unit_result=success, ExecMainCode=1 (normaler Exit), ExecMainStatus=0 |
| Endebeleg | unit_and_removed_cgroup; identische Lauf-/Invocation-/Boot-/cgroup-Bindung in Bericht und Beobachtung |
| Journal | succeeded, active=0 |
| Rücknahme | unit_retired=true, package_removed=true, staging_absent=true |
| Fremddienste | SSH, wg-admin und GDM vor/nach sowie nach Rücknahme jeweils active |
| Unabhängige SSH-Prüfung | Unit LoadState=not-found, ActiveState=inactive, MainPID=0; Test-cgroup abwesend |
| Ressourcenlimits | limits=null: nach Prozessende nicht mehr auslesbar; keine Durchsetzungsabnahme daraus ableiten |

Lokaler Export: [t3normal20-report.json](../../artifacts/t3normal20-report.json).
Export-SHA256: `fd9bd913a25eea50e4ace0be140d777b85281cf77a9e2294e389906c70d35543`.
Der Root-Exporter meldet für den ursprünglichen Bericht SHA256 `9ce7174b1fc0d5c5f848af64c43784f611f5d38f5334a116ddb937ecaeae8510`; Originalbericht blieb rootgeschützt. Export und Original haben verschiedene Inhalte und daher unterschiedliche Hashes.

## Umfang und verbleibende Arbeit

Der enge synthetische Normalprozess auf Ubuntu einschließlich Journalabschluss und Rücknahme ist bestätigt. Dies ist ein Teilnachweis für B09, keine vollständige B07–B09-, REST-, Produkt- oder Backupabnahme. Der Bericht überprüft den erfolgreichen Prozessausgang; ein vollständiger fachlicher Passport-/Input-/Kernelvergleich war nicht Gegenstand dieses Laufs.

Als nächste Vorbereitung: Ressourcenwerte während eines noch laufenden begrenzten Testprozesses unabhängig beobachten, anschließend kontrollierten Kindprozess-/Abbruchtest konkretisieren. CPU-Drosselung, Speicherlimit/OOM, Controllerverlust, Recovery und Linux-TLS-Wiederholung bleiben offen. Die bisherige Freigabe galt ausschließlich diesem Normalfall; kein Stress-/Abbruchlauf aus ihr ableiten.

Installation unter /opt/aurelia-t3, Root-Testjournal/Berichte unter /var/tmp/aurelia-t3-control und Upload-/Helferdateien bleiben als Nachweise erhalten. Keine pauschale Bereinigung oder neue Sicherung durchgeführt. Kein Serverneustart, keine Firewall-/SSH-/Produktkonfiguration geändert.

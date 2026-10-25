# B1 saved-content worker: gebundener Kern und anschliessendes Linux-Paket

> Fuer agentische Ausfuehrung: executing-plans / subagent-driven-development; TDD und unabhaengige kritische Reviews, native Gates separat.

**Goal:** Sieben vorhandene V6-Blobs unabhaengig rehashen und strikt begrenzt als TAR inventarisieren; keine Extraktion, neuen Downloads oder Produktalgorithmusaenderungen.
**Architecture:** Isolierter additiver Kandidat runtime/rw-b1-job-20261023. Reale Metadatenattestation dient ausschliesslich als gebundene Eingabe. Reiner Planvalidator und kooperativer Jobkern zuerst; Systemd-Lifecycle, eigener einmaliger Claim, Fehler-/Persistenz-/Transport-/Fresh-Finalisierung separat integrieren. Keine Zwischenstufe erteilt Serverausfuehrungsrechte.
**Tech Stack:** Python3.12/Stdlib und gehashte unveraenderte Archivhelfer; bestehender geschuetzter IPv4-Opszugang erst nach neuem Gesamtpaketreview/Freigabe.

## Schritte

- [x] Einmalige Metadatenprobe und unabhaengiger Beobachtungsreview: sieben Identitaeten, CPython3.12.3/zlib1.3/ausgewaehlte TAR-Codefingerprints; keine Blobinhalte.
- [x] job_plan.py / test_job_plan.py: extern gehashte Belegbytes mit exaktem Antwortvertrag und False-Autoritaetsflags binden; feste Pfade, sieben Layer, Laufzeit und Ressourcen nicht frei konfigurierbar. RED/GREEN, Aenderungen/Schema/Subklassen ablehnen, keine IO im Planbau.
- [x] job_core.py / test_job_core.py: gebundene Runtime und echte Kernel-/Service-/Prozesskontextbeobachtung vor erstem Blobopen und nach letzter Inhaltspruefung; Deadline und Contextgates, exakte sieben Dateipfade und Pins, alle Ergebnisse atomar im Rueckgabewert; unvollstaendige/fehlerhafte Befunde niemals als Erfolg. Echte gzip/TAR-Synthetik plus Drift-/Timeout-/fehlendeGate-Tests.
- [x] Lokale Kernintegration und begrenzter unabhaengiger Review; alte Kandidaten und nativen Belege hashgleich erhalten. Dies ist noch kein startbares Linux-Paket.
- [ ] Anschliessend: neue rwb1archivev1.service/.slice mit1CPU, memory.high1610612736/max2147483648,swap0,pids256 und endlichem RuntimeMax. Aktuelle Kernelwerte/PID/Cgroup vor Blobinhalten; bestaetigte Produkt-/Preview-/Budget-/Mount-/IPv6-/V6-Stopbedingungen; kein Netz oder neue Downloads. Vor-/Nachfstat jedes Blobs.
- [ ] Erzeugten Bootstrap/Worker/Einmaltransport auf Quell-,Job-,Runtime-,Paket-,Limit- und Ergebnisbindung testen; eigene Metadaten begrenzen, Persistenzfehler/Timeout/unbekannten Ausgang behandeln, kein Autoretry. Aktuellen Kernelbeleg nicht durch Sollwerte ersetzen.
- [ ] Frischen Abschluss erst nach eigenem Stopp + neuer Schutzpruefung + File-/Parent-fsync-Rueckkehr akzeptieren; gespeicherte Kandidaten allein nie akzeptieren. Finalreview, dann konkrete gesonderte native Freigabe.

## Grenzen

Metadaten und Runtime sind nur punktuell beobachtet. Archivdeadline kooperativ, keine harte Unterbrechung blockierten OS-IOs. TAR-Inventur ist konservativ und begrenzt; reale Archive noch unbekannt. Nutzdatenrundung ist kein physischer Peak oder Inodebedarf. Rueckgabewerte verleihen keine Extraktions-,Container-,Build-,Produkt- oder Migrationsfreigabe. Der neue Kern darf Lifecycle/Persistenz noch nicht vortaeuschen.

**Kernabschluss23.10.2026:**38Tests0Fehler/Failures/Skips,289eingefroreneEintraegegleich,unabhaengigerAstra/medium-Review0Blocker. Plan-SHAae5f98570e4cfddf53c25402c483a0235539f7e04ff2fb5362e6a57c9b320017. Deadlinepruefungen nach finalenProbes/Serialisierung per3RED/GREEN-Regressionsfaellen abgesichert. Noch kein erzeugtes/startbares Linux-Gesamtpaket. Weiter mit erster offener Checkbox; keine erneute Metadatenprobe oder Materialaufnahme automatisch starten.

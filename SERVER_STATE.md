# Server: beobachtetes Ist und Nachweisgrenzen

**25.10.2026, mehrere zeitgestempelte lesende Einzelaufnahmen.** Kein gemeinsamer atomarer Serverzustand und kein vollständiges Maschinenbackup.

## Aktueller Test-VPS

Der Betreiber hat den aktuellen Test-VPS als frische Quelle festgelegt. Die lesende Bestandsaufnahme und die fest begrenzte Konfigurationsaufnahme waren erfolgreich. Erfasst sind unter anderem Betriebssystem-/Paket-/Dienst-/Dateisystemmetadaten, Budgetkonfiguration und ausgewählte System-/Benutzerdienstkonfiguration. Geheimnisse und rohe Konfiguration verbleiben ausschließlich in der geschützten Sicherung.

Die beobachteten Speicherwerte entsprechen rund 23,47 GiB vom Betriebssystem gemeldetem RAM; das ist keine alleinige Kapazitätszusage für die Anwendung. Die konfigurierten Budgetgrenzen sind:

| Projektbereich | CPU-Obergrenze | RAM weich / hart | Swap-Obergrenze |
|---|---:|---:|---:|
| Aurelia-Pilot | 5 CPUs | 8 / 10 GiB | 1 GiB |
| Separater Website-Testbereich | 1 CPU | 2 / 4 GiB | 256 MiB |

Die Bereiche sind getrennte Projektbudgets auf demselben VPS. Inhalte des Websiteprojekts gehören nicht in diesen Review. Gleichzeitige Ressourcennutzung ist keine gegenseitige funktionale Integration.

Docker-Benutzerdienst und Preview-Dienst wurden als aktiv beobachtet. Dienstaktivität beweist keine Anwendungserreichbarkeit, Containerabnahme oder erfolgreiche RadiWorks-Integration. Ein kumulativer `CPUUsageNSec`-Wert ist keine CPU-Prozentmessung. IPv6 war für `all` und `default` deaktiviert; der vereinbarte Zugang verwendet IPv4.

Eine weitere begrenzte Laufzeitaufnahme lieferte sechs erfolgreiche Docker-Metadatenabfragen: Docker-Client und -Server 29.9.1, vier Container (drei laufend, einer beendet), drei Images, vier Volumes und vier Netzwerke. Rohe Namen, Labels und Befehlsargumente verbleiben geschützt. Zwei ergänzende Gitabfragen am angenommenen Pilot-Sammelverzeichnis scheiterten mit „not a git repository“. Das belegt eine falsche Annahme über die Gitablage, keinen Fehler der Anwendung; die Gesamtprobe wird deshalb nicht als vollständig erfolgreich ausgewiesen.

Noch nicht geschlossen sind die Bindung der tatsächlichen Laufzeit an die gesicherten Produktquellen, alle persistenten Anwendungsdaten, der vollständige Provider-/Maschinenrestore und ein getesteter gesamter Wiederanlauf. Die gespeicherten Konfigurationen, Metadaten und Paketlisten ersetzen diese Nachweise nicht.

## Hauptserver

Der Betreiber hat ausdrücklich **historischen dokumentierten Stand plus Zielanforderungen** gewählt. Die neue Sicherung enthält keine behauptete aktuelle Erreichbarkeits-, Hardware- oder Wiederherstellungsattestation des Hauptservers. Der frühere Boot-/LUKS-Fehler wird durch die Test-VPS-Aufnahme nicht als behoben bewertet.

Die Hauptserver-Zielplanung nennt Ryzen 5 9600X, sechs Kerne / zwölf Threads, RTX 4000 SFF Ada mit 20 GB GPU-Speicher sowie beispielhaft 128 GB RAM und zwei 1-TB-NVMe-Laufwerke. Diese Zielwerte sind keine frische Hardwaremessung und kein nachgewiesenes 25-Nutzer-Leistungsversprechen.

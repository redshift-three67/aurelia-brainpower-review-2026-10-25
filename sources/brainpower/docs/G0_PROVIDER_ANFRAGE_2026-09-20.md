# Anfrageentwurf: Recovery- und Betriebsnachweise

Entwurf für den Betreiber; nicht versendet. Keine Zugangsdaten beifügen.

Betreff: Recoveryzugang und Betriebsnachweise für unseren Ubuntu-Server

Guten Tag,

für die abschließende Betriebs- und Recoveryplanung unseres dedizierten Servers benötigen wir bitte folgende Informationen:

1. Gibt es ein unabhängig von den installierten NVMe-Laufwerken startbares Rescue-System oder eine Virtual-Media-/ISO-Einbindung über die KVM? Bitte nennen Sie Zugangsschritte, unterstützte Medien, Einschränkungen und die Möglichkeit, anschließend wieder regulär von NVMe zu starten. Gemeint ist keine Neuinstallation oder Löschung.
2. Ist die BMC-/IPMI-Verwaltung vom öffentlichen Internet und dem Betriebssystemnetz getrennt? Welche Zugangsbeschränkungen schützen KVM und virtuelle Medien?
3. Wie sind USV und längere Stromausfälle abgesichert? Ist ein geordneter Betriebssystem-Shutdown vorgesehen bzw. integrierbar, wie wird er ausgelöst und welches Wiederanlaufverhalten gilt? Bitte vorhandene Betriebs-/Testnachweise nennen.
4. Unterstützen Mainboard, CPU und eingesetzter RAM aktives ECC? Bitte bestätigen Sie die konkrete Ausstattung und den tatsächlichen ECC-Betrieb; die derzeitige DMI-Ausgabe meldet keine Fehlerkorrektur.

Bitte zunächst nur Informationen bereitstellen und keine Einstellungen, Datenträger, Neustarts oder Neuinstallationen auslösen.

Vielen Dank.

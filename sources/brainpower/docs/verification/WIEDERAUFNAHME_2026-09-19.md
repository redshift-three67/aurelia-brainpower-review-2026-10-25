# Lesender Wiederaufnahmecheck und Integrationsvoraussetzungen

Serverbeobachtung: 19.09.2026, 18:42:16 UTC, über bestehenden SSH-Zugang/WireGuard.

| Kontrolle | Ergebnis |
|---|---|
| Bootziel | graphical.target |
| GDM | active/running; display-manager verweist auf /usr/lib/systemd/system/gdm.service |
| VPN / Hostfirewall | wg-quick@wg-admin und aurelia-firewall active |
| RAID | md0 und md1 jeweils [2/2] [UU] |
| Fehlgeschlagene Units | keine |
| CIFS-Mounts | keine; bisheriger temporärer Mount ist nach Neustart nicht persistent |
| Backup-Timer | disabled; erklärt Exitcode 1 des abschließenden systemctl-is-enabled-Aufrufs |

Kein erneuter Neustart ausgelöst, keine vollständige Sicherheits-/Hardwareabnahme. Konfigurationssicherung vom 18.09. erfolgreich, aber vor grafischer Bootkorrektur. Aktuelle Grafikverknüpfung und Bootziel vor späteren Änderungen nachsichern. Kein Wiederholen des alten Sicherungsskripts ohne vorangehende Mountprüfung: es verlangt den RO-Hauptmount.

## Schlüsselverwahrung

Betreiber wählt verschlüsselten externen Datenträger. Vollständiger Zielordner und Entsperrung angefragt; noch kein Schlüssel übertragen. SSH hat bisher keine nichtinteraktiven Rootrechte. Schlüssel niemals in Chat, Projektdateien oder Toolausgaben ausgeben. Die vorbereitete externe Kopie muss separat gegen das Original verifiziert werden; bisher kein Schutz bei vollständigem Verlust des Servers belegt.

## Gezielter Quellenabgleich (keine Produktänderung)

- Aurelia Ground-Zero-Status vom 25.08. beschreibt weiterhin den Zustand vor Installation. Bestehende Infrastrukturbelege müssen in eine aktuelle Gatebewertung eingehen; kein Neuinstallationsauftrag und keine automatische Gatefreigabe.
- Aurelias Kernel-ABI beschreibt Python-/WASM-entry. Modul_Templates API_CONTRACT §5 schreibt für neue Integrationen die versionierte REST-Operation vor, entry bleibt deprecated-compatibility. Vor Adapterimplementierung ist eine autoritative Vertragsentscheidung nötig.
- Fehlende Schemas im gekürzten Manifestbeispiel sind KEIN Nachweis fehlender Schemas im Modul: API_CONTRACT verlangt input/output-Schemas und copy-Liste aus dem Live-Manifest. Ein späterer Live-Contracttest muss diese tatsächlichen Felder prüfen.
- API_CONTRACT §6 und Übergabe bestätigen lokalen Prototyp ohne Authentifizierung und ohne belegte tenant-scoped Queries. Nullable Mandantenfelder allein erfüllen keine Produktions-Mandantentrennung.
- REIFEGRADE: RadiWorks S0–S3 lokal dokumentiert, S4/S5 nicht zertifiziert. Übergabe bleibt Evidenzangebot, kein Registry-/Produktions-GO. Erstmodul noch nicht ausgewählt.

Quellen-SHA256 (19.09.2026):

| Quelle | SHA256 |
|---|---|
| Aurelia/docs/project-control/ground-zero/GATE-STATUS.md | 30a961283d70092076ad52163d8da867c5d5e308f04b5307ef231fda094217c2 |
| Aurelia/docs/06-kernel-abi.md | 9105cf2a4fc13d068b2bfa8b12aecdf81b799a607cd93afac0fe54fdc8466886 |
| Modul_Templates/standards/API_CONTRACT.md | f21ff364e208d1194f5d2f0f33679f7076adbe6b265b2ab14b9ff361e750c8c7 |
| Modul_Templates/standards/REIFEGRADE.md | fcde7896030716dba5777369919f2c7bfbe95e26708764ca20bb645cd9e7ea87 |
| Modul_Templates/UEBERGABE_AURELIA.md | df3041c005f72e2cd25cdec91c3a9fdac1efa586ef2b575ccd933b4fc174935b |

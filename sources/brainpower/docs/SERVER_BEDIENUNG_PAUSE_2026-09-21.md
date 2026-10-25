# Einfachere Serverbedienung – Untersuchung vor Pause

Betreiber wünscht erheblich weniger manuelle KVM-Eingaben und danach Pause. Keine Servertests, Dienste oder Rechte im Rahmen dieser Untersuchung ändern.

## Erkenntnisse

SSH über WireGuard ist für Vorbereitung und Auswertung nutzbar. sudo-n steht nicht zur Verfügung; Root-Anmeldung in einer anderen KVM-Sitzung gibt dem SSH-Prozess keine Root-Rechte. Die beiden bisherigen Computer-Use-Versuche scheiterten vor Eingaben: Firefox wegen nicht unterstützter URL-Policy-Erkennung, Chrome wegen nicht hinreichend zuverlässig ermittelter URL. Keine Serverfehlfunktion daraus ableiten. Keine Umgehung dieser Werkzeuggrenze.

Die aktuelle Werkzeug-/Skillprüfung zeigt weiter Computer Use über sky/node_repl, aber keinen nachgewiesenen behobenen URL-Zugriff. Ein erneuter kontrollierter Beobachtungsversuch wird vor dem Pausenabschluss versucht; direkte Bedienbarkeit ist bis zu dessen Erfolg unbestätigt. Keine Zusage einer funktionierenden KVM-Automation.

## Empfehlung zur Wiederaufnahme

| Weg | Aufwand für Betreiber | Bewertung |
|---|---|---|
| Geprüftes, geschlossenes Wartungspaket | Ein kurzer Root-Aufruf pro sachlich zusammengehörigem Paket | Empfohlen; vorhandenen Ablauf bündeln, Berichte anschließend perSSH automatisch auswerten |
| Direkte KVM-Automation | Entsperrung/Anmeldung durch Betreiber; übrige Eingaben bei unterstütztem Werkzeug | Nützlich, aber aktuelle URL-Erkennung verhindert verlässliche Zusage; KVM für Boot/Recovery weiter erforderlich |
| Dauerhafter privilegierter Auftragsdienst | Nach Einrichtung potenziell keine einzelnen Root-Aufrufe | Zusätzliche privilegierte Schnittstelle und Prüfaufwand; derzeit nicht implementieren |

Wartungspaket: fest definierte Schritte, rootgeschützter geprüfter Ausführungsstand, erwartete Quellhashes, gebundene Lauf-ID, begrenzte Laufzeit/Ressourcen, Stop bei Fehler oder Zustandsabweichung, getrennte Ergebnisberichte und eigene Aufräumprüfung. Keine allgemeine Befehlsschnittstelle, kein Nachladen beliebiger Aufträge in laufende Root-Sitzung, keine pauschale sudo-/Root-SSH-Freigabe. Neuboot/Entsperrung und externe Entscheidungen bleiben gesondert. Erfolg, Fehlschlag und Cleanup werden unabhängig ausgewertet; keine Wiederholung bereits erledigter Schritte.

Dies ist eine Empfehlung, keine implementierte neue Steuerung. Bisherige kurze Helfer bleiben verfügbar. Nächste Wiederaufnahme zuerst Bedienablauf bündeln, danach ausstehende logische DB-/Recovery-Nachweise. Kein konkretes neues Testpaket während der Pause gestartet.

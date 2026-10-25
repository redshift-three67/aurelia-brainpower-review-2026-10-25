# RadiWorks 8103: Fallladen nach blockiertem Dienst

Stand: 03.10.2026, lokale Betriebsstörung. Keine Änderung am RadiWorks-Quellcode und keine Aurelia-Freigabe.

## Befund

Der Prozess auf `127.0.0.1:8103` nahm TCP-Verbindungen an, beantwortete aber `/ping`, `/manifest` und `/cases` nicht innerhalb von vier Sekunden. Die asynchronen Diagnose-Endpunkte `/docs` und `/openapi.json` antworteten mit HTTP 200. Der Python-Prozess hatte 43 Threads und praktisch keine zusätzliche CPU-Last; die verschlüsselte Entropiejournaldatei wuchs weiter. Das ist ein starkes Indiz für blockierte synchrone API-Arbeiter. Ohne Thread-Stack oder aktuelle Zugriffsprotokolle ist die konkrete auslösende Route **nicht nachgewiesen**. Die Journalaktivität belegt keine Ursache der Blockade.

Die vier Dateien im Fallordner bestanden aus drei Fällen und einer Verwaltungsdatei. Alle drei Falldokumente waren als JSON lesbar. Vor dem Stop wurden die relevanten Laufzeitordner unter `checkpoints/radiworks-8103-hung-20261003/before-stop` mit 64 Dateien gesichert. Nach dem Stop wurden dieselben Bereiche unter `.../after-stop` erneut kopiert. Das Manifest `.../after-stop-manifest.json` enthält 64 Dateien; jede Kopie stimmte beim SHA-256-Abgleich mit ihrer gestoppten Quelle überein, und die drei Falldokumente waren weiterhin als JSON lesbar. Die Sicherungen liegen lokal im Brainpower-Arbeitsbereich, nicht auf einem unabhängigen Datenträger.

## Wiederherstellung und Nachprüfung

Der identifizierte, blockierte 8103-Prozess wurde nach der Vorabkopie beendet. Der Port wurde frei. Anschließend startete `tools/start_radiworks_preview_8103.ps1` mit demselben Laufzeitordner, Katalog und externen Fernet-Recovery-Schlüssel von E: neu. Der Schlüsselwert wurde nicht ausgegeben oder in diesen Bericht geschrieben.

Nach dem Neustart: `/ping` lieferte `pong`, der Manifesthash war `sha256:fa169781a07b21c4dd569fad1ae6225611095f8bdb3aae41f22a0d986b2309eb`, `/cases` meldete drei Fälle, Auto war AUS, die virtuelle Queue leer und Stochastic-Recovery verfügbar. Für **alle drei** gelisteten Fälle lieferte `POST /cases/ref/{ref}/activate` HTTP 200; `/cases/current/ref` stimmte jeweils mit dem angeforderten Fallverweis überein. Sitzungs- und Statistikendpunkte antworteten ebenfalls. Nach der Prüfung blieb der erste gelistete Fall als aktuell ausgewählt; der Betreiber kann im Browser einen anderen wählen. 8104 und 8105 blieben erreichbar.

Der API-Ladepfad ist damit wieder funktionsfähig. Die Browserbedienung nach `Strg+F5` ist zusätzlich beim Betreiber angefragt. Ein weiterer Langzeittest und die genaue Ursache der alten Thread-Blockade sind offen. Bei Wiederholung zuerst Thread-/Anfragestatus und laufende Aufträge sichern; aus der erfolgreichen Neustartprobe folgt keine dauerhafte Fehlerbehebung.

Eine anschließend neu geöffnete Browserseite zeigte die Fallliste und `Live`. Während dieser Sichtprüfung war Auto AN und die virtuelle Queue wieder aktiv. Auto wurde in der Diagnose nicht manuell eingeschaltet; die Ursache der Zustandsänderung ist nicht belegt. Der laufende Zustand wurde nicht beendet, und es wurde kein zusätzlicher Fallwechsel per Browser vorgenommen. Die oben genannten Werte „Auto AUS/Queue leer“ sind der unmittelbare Zustand nach dem Neustart, nicht eine Aussage über den späteren laufenden Zustand.

| Abschnitt | Stand |
| --- | ---: |
| Wiederherstellung des lokalen 8103-Fallladepfads | 100 % für die drei vorhandenen Fälle per API |
| Browser-Bedienbestätigung | ausstehend |
| Ursachenanalyse / dauerhafte Vorbeugung | offen; konkrete blockierende Route nicht bewiesen |
| Aurelia-Integration | 0 %; getrennte Host- und Freigabegates |

# RadiWorks S4.3: öffentlicher CopyGuard-Ausgabevertrag

Freigegebene Entscheidung: Die internen Analyse-, Draft-, Fall- und Passportdaten bleiben unverändert. Verbotene sichtbare Texte werden erst an der öffentlichen JSON-/WebSocket-Grenze ersetzt. Der Platzhalter lautet `[CopyGuard: Text zurückgehalten]`; ein Block bleibt als `copyguard_verdict=block` erkennbar. Diese lokale Lexikon-Stufe ersetzt Aurelias spätere zweite CopyGuard-Stufe nicht.

## Datenfluss

1. Die Engine berechnet und persistiert unveränderte Originalraten für Parität, Wiederanlauf und Audit. Draft-Promote und direkte Queue-Wege prüfen weiterhin die Originalsignatur und blockieren sie.
2. Eine reine, rekursive Projektion ersetzt jeden vom lokalen CopyGuard gesperrten öffentlichen String. Sie mutiert ihr Eingabeobjekt nicht und behandelt auch dynamische JSON-Schlüssel, insbesondere `copyguard_findings`. Sichere Werte bleiben bytegleich. HTTP-JSON-Antworten einschließlich Fall-/Sessionansichten und Fehlern verwenden diese Projektion; WebSocket-Ereignisse werden vor Speicherung und Replay projiziert. HTML/JS-Assets bleiben davon unberührt.
3. Der Browser erhält ausschließlich die öffentliche Projektion. Buttons für einen zurückgehaltenen Ratenwert dürfen keinen scheinbar gültigen Direkt-Broadcast/Clarke-Auftrag starten. Die normale Analyse und sichere Originalraten behalten ihre Bedienung.
4. Weil ein projiziertes Falldokument nicht als Rohdatensatz zurückgespeichert werden darf, speichern die beiden vorhandenen UI-Editoren nur Name/Beschreibung und gegebenenfalls die letzte Absicht über einen gezielten Server-Endpunkt. Der Server übernimmt die übrigen Felder aus seinem unveränderten aktiven Falldokument. Der alte vollständige `POST /cases`-Pfad weist Projektionen mit Platzhalter zurück, statt Originalanalysen still zu überschreiben. Unveränderte sichere Altaufrufe bleiben erlaubt.

## Fehler, Grenzen und Abnahme

- Kein verbotener Text in Analyseantwort, aktuellem Ergebnis, Draftansicht, Fall-/Sessionansicht, Statistik, Live-Ereignis oder Replay im künstlichen Negativfall. Der interne Draft und der gespeicherte Fall enthalten weiterhin den Rohwert; Promote/Queue bleiben gesperrt.
- Der Metadatenpfad erfordert einen aktiven Fall; nicht angegebene Felder bleiben unverändert. Ein unverändert zurückgereichter Platzhalter bewahrt den internen Originalwert; neue verbotene Metadaten werden abgelehnt. Fehlende/ungültige Daten führen zu einem expliziten Fehler.
- Gezielte Rot-/Grün-Tests für Projektion, HTTP, WebSocket und Fallrückschreiben; anschließend vollständige Engine-Suite, JS-Syntax und der isolierte 390-px-Browser-Smoke. Die übrigen Textflächen und der Aurelia-Host bleiben eigene S4-Gates.

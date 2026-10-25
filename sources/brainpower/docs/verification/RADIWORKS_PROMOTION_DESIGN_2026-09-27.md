# RadiWorks: belastbare Draft-Freigabe im lokalen Prototyp

Stand 27.09.2026. Vom Betreiber als nächster RadiWorks-Fix bestätigt. Betrifft nur die virtuelle Broadcast-Queue des lokalen Prototyps. Physische Emission, Aurelia-Autorisierung und eine Garantie genau-einmaliger Seiteneffekte sind nicht Teil dieser Änderung.

## Befund und Ziel

Ein synthetisch erzwungener `BroadcastError` nach `draft → ready` führt derzeit zu HTTP 422, `draft.status=promoted` und leerer Queue. Die Draft-Datei wird vor `enqueue` geschrieben. Bei mehreren Raten kann ein späterer Fehler bereits laufende Broadcasts hinterlassen. Nach Prozessende ist die Queue absichtlich flüchtig.

Jeder Promote- oder Legacy-Mix-Versuch erhält eine zufällige, eindeutige `promotion_id` und einen persistierten Versuchszustand. Vor der Queue-Übernahme bleibt der Draft `ready`. Nur nach erfolgreicher Übernahme des gesamten vorbereiteten Batches wird er `promoted`. Fehlgeschlagene/unterbrochene Versuche bleiben lesbar, erzeugen niemals einen automatischen Wiederholungsversuch und können nur nach bewusster Prüfung neu begonnen werden. CopyGuard, aktueller Scope und bestehende Statusübergänge bleiben Pflicht.

## Lokaler Vertrag

1. Die Engine erstellt aus einem `ready`-Draft eine unveränderliche Vorschau aller Queue-Einträge. Sie prüft CopyGuard, Eingabegrenzen, Rate-Anzahl und leere Ergebnisse vor jeder Status- oder Queue-Änderung.
2. Unter einer pro Engine gehaltenen Promote-Sperre schreibt sie einen Versuch `pending` atomar in den Draft und merkt `promotion_id` sowie den Digest der vorbereiteten Einträge. Derselbe Draft kann währenddessen keinen zweiten Versuch beginnen.
3. Die Queue übernimmt die vorbereiteten Elemente als einen Batch unter ihrer eigenen Sperre. Validierung, Elementerzeugung und Startfehler dürfen keine Teilmenge hinterlassen. Der Batch liefert die `broadcastId`s zurück.
4. Noch unter der Queue-Sperre speichert die Engine `status=promoted`, `promotion.state=submitted` und die IDs atomar. Scheitert dieser letzte Schritt, entfernt sie genau diesen noch nicht sichtbaren Batch. Der Versuch wird `failed`; schlägt auch diese Speicherung fehl, bleibt sein `pending`-Marker zur kontrollierten Wiederanlaufprüfung erhalten. Sie behauptet keinen erfolgreichen Promote und stoppt keine fremden Queue-Elemente.
5. Beim nächsten Prozessstart werden offene `pending`- oder `submitted`-Versuche als `interrupted` sichtbar gemacht. Die Queue wird nicht neu befüllt. Auch bereits ausgesendete Signale werden nicht automatisch wiederholt. Nur ein nachweislich vollständig beendeter Batch darf als `completed` erscheinen; ein späterer Neustart ändert diesen Abschluss nicht.
6. Die bestehende direkte Operator-Funktion `POST /broadcast` bleibt ein gesonderter, mit CopyGuard geschützter Weg. Sie wird nicht als Draft-Promotion ausgegeben. Der Legacy-Mix benutzt denselben Versuchsdienst und behält seinen ausdrücklichen Settings-Schalter.

## Fehler- und Testfälle

- Fehler vor Versuchsanlage: HTTP 409/422, Draft unverändert, Queue unverändert.
- Erzwungener Fehler beim ersten oder späteren Batch-Element: keine Teilübernahme, Draft nicht `promoted`, Versuch fehlgeschlagen oder `uncertain`.
- Fehler beim finalen Draft-Schreiben: Batch gezielt stoppen; Zustand sichtbar `uncertain`, kein Erfolgssignal.
- Neustart mit offenem Versuch: `interrupted`, keine automatische Queue-Aktivität und keine Wiederholung.
- Wiederholung eines bereits erfolgreichen Promote-Requests: HTTP 409, keine erneute Aussendung. Ein gescheiterter Versuch darf durch eine neue bewusste Benutzeraktion mit neuer `promotion_id` wiederholt werden; unterbrochene Versuche bleiben bis zur fachlichen Klärung gesperrt.
- Regulärer Promote und Legacy-Mix: vollständiger Batch, zuordenbare IDs, bestehende CopyGuard-/Scope-/Browser-Tests weiter grün.

Die Dateispeicherung und die flüchtige Queue können keine gemeinsame ACID-Transaktion bilden. Bei Absturz während eines Broadcasts ist die Wirkung unbekannt; der persistierte Zustand muss das als `interrupted` offen ausweisen. Diese bewusste Begrenzung verhindert falsche Erfolgsbehauptungen und automatische Doppelsendungen.

# Plattform- und Lastanforderungen

Die folgenden Punkte sind Anforderungen beziehungsweise Planungsprofile. Ihre Dokumentation ist kein Implementierungs- oder Abnahmenachweis.

Mandant/Praxis, Benutzer, Therapeut, Klient/Fall und Abonnementinhaber sind getrennte Identitäten. Jeder Zugriff muss Mitgliedschaft, Objekt-/Klientenrechte und die Berechtigung für das jeweilige Modul beziehungsweise die Modulkombination prüfen. Ein Abonnement allein ersetzt keine Objektberechtigung.

Jobs benötigen unveränderliche Bindungen an Mandant, handelnden Benutzer, Klient, Modul, Verfahren, Katalog und Kontextrevision sowie die akzeptierte Tarif-/Quotenrevision. Abbruch, Wiederanlauf, Ergebniszuordnung, Audit und Rechteprüfung müssen dieselben Bindungen erhalten. Neue Embeddings oder ersetzende Analyseverfahren sind keine freigegebene Routineanpassung.

Erforderlich sind hierarchische CPU-/RAM-/Speicher-/Jobbudgets, faire Warteschlangen, definierte Lebenszyklen, Speicherquoten und negative Tests gegen Mandantenwechsel, API-/WebSocket-/Assetzugriffe und veraltete Berechtigungen. Die endgültigen Daten-, Job-, Rechte- und Modulverträge müssen vor Integration abgestimmt werden.

## Laststrategie

Der Test-VPS nimmt Module und gemeinsame Bereiche schrittweise auf. Er kann begrenzte Modul- und Parallelitätsproben liefern. Eine vollständige Hauptserver-Lastsimulation ist dadurch nicht belegt.

Das Profil „25 Nutzer verwenden RadiWorks gleichzeitig“ gehört zusammen mit Burst-, gemischten Modul- und Gesamtlastprofilen in die spätere Prüfung des tatsächlich verifizierten Hauptservers. Zu messen sind unter anderem Laufzeit, Warteschlangen, CPU/RAM je aktivem Job, dauerhafte Datenzunahme, Spitzenbedarf, Abbruch/Recovery und die Wirkung gemeinsamer Quoten. Messwerte eines einzelnen VPS-Laufs dürfen nicht linear als Produktionsgarantie hochgerechnet werden.

Primärquelle: Brainpower `docs/AURELIA_MANDANTEN_KAPAZITAET_2026-10-16.md`. Zentrale Datenbankentscheidung und finale Abonnement-/Abrechnungskonditionen bleiben getrennte offene Entscheidungen.

# Klientenbezogene Favoriten, Trends und Benachrichtigungen in Aurelia

Stand: 09.10.2026. Betreibervorgabe für die spätere zentrale Datenstruktur. **Anforderung und empfohlene Grenzen; noch keine implementierte Auswertung, Migration oder aktivierte Benachrichtigung.** Die laufende [Referenzprüfung der Module](AURELIA_REFERENZPRUEFUNG_COPEN_BOHM_THOM_2026-10-09.md) hat Vorrang.

Aurelia soll einem berechtigten Nutzer die Favoriten und zeitlichen Entwicklungen eines Klienten über mehrere Module hinweg zeigen können. Das erfordert gemeinsame Klientenreferenzen und nachvollziehbare Herkunft. Die Berechnungsverfahren der Module bleiben erhalten. Ein häufig vorkommender Eintrag ist zunächst ein Vorschlag; daraus wird weder automatisch ein persönlicher Favorit noch eine fachliche Bewertung.

## Welche Daten getrennt bleiben müssen

| Gegenstand | Für die zentrale Planung vorzusehen | Bedeutung für die Darstellung |
|---|---|---|
| Klientenbezug | Mandant, stabile Klienten-ID, Modulzuordnung, Fall/Sitzung und Zugriffsberechtigung; Ersteller getrennt vom fachlichen Besitzer | Gleiche Namen genügen nicht für eine automatische Personenvereinigung. Modulübergreifende Sicht nur innerhalb erlaubter Beziehungen. |
| Persönlicher Favorit | Ausdrückliche Auswahl, auswählender Nutzer, Sichtbarkeit, Eintrag/Katalogrevision, Zeitpunkt und Änderungen | Nutzerfavoriten getrennt von algorithmisch gefundenen Wiederholungen zeigen. |
| Wiederkehrender Kandidat | Versionierte Vergleichsregel, Zeitfenster, beteiligte Beobachtungen, Trefferzahl und Herkunft | Begründung anzeigen und Übernahme bestätigen lassen. Ähnliche Texte verschiedener Module nicht ohne bestätigte Zuordnung gleichsetzen. |
| Beobachtung | Native Kennzahl, Einheit/Skala, Verfahren/Revision, Zufallsquelle soweit relevant, Kontext-/Auftragsstand, Beobachtungs- und Empfangszeit, fehlende Werte | Original-GV, persönliche Matrixscores und Thom-Dimensionen bleiben unterschiedliche Größen. Zufallsvariationen sind keine nachgewiesenen Klientenreaktionen. |
| Trend und Archiv | Verwendeter Datenstand, Regelversion, Zeitfenster, Vergleichsgruppe, Lücken und gespeicherter Ergebnisstand | Unterschiede zunächst nebeneinander zeigen. Keine beliebige Mittelung, keine allgemeine Deutung von steigenden Werten als Verbesserung. |
| Ereignis und Triggerentscheidung | Auslösende Beobachtungen, Regelrevision, Annahme/Ablehnung, Rechteprüfung und eindeutige Entscheidung | Wiederholte Zustellung oder ein Reconnect darf keine doppelte Aktion auslösen. |
| Benachrichtigung | Empfänger, Kanal und aktivierte Präferenz; Versandabsicht, Zustellversuche, Fehler und Deduplizierungskennung | Auswertung, Versandabsicht und tatsächliche Zustellung sind getrennte Zustände. |

Für gemeinsame Favoriten sind bestätigte fachliche Zuordnungen zwischen Katalogeinträgen erforderlich. Eine Zuordnung hält fest, ob Einträge gleichbedeutend, verwandt oder lediglich textähnlich sind. Die native Modulreferenz bleibt erhalten; neue Zuordnungen verändern frühere Ergebnisse nicht. Numerische Trends dürfen nur bei dokumentierter Vergleichbarkeit zusammengeführt werden. Bis dahin ist eine gemeinsame Übersicht mit getrennten Modulspuren sinnvoll.

## Regeln und optionale Benachrichtigungen

Trigger werden später ausdrücklich konfiguriert und standardmäßig deaktiviert angelegt. Eine Regel benötigt eine klar benannte Kennzahl, ihr Vergleichsverfahren und die zulässige Richtung/Schwelle. Mindestzahl und Alter der Beobachtungen, Datenlücken, Wiederholungsabstand sowie gegebenenfalls Hysterese gehören zur Regelversion. Fehlende Werte erzeugen keinen künstlichen Nullwert oder Trend. Eine nachträgliche Korrektur muss als neuer Daten-/Auswertungsstand nachvollziehbar bleiben.

Mailversand ist ein Beispiel für einen optionalen Kanal. Empfänger, Freigabe und Sichtbarkeit sind gesondert festzulegen. Eine Nachricht sollte standardmäßig keine sensiblen Klientendetails enthalten, sondern auf eine geschützte Ansicht verweisen. Vor tatsächlicher Zustellung Rechte und Aktivierung erneut prüfen; widerrufene oder unzulässige Versandabsichten dürfen nicht weiter ausgeführt werden. Ein Modulabo ersetzt keine Berechtigung für einen bestimmten Klienten.

Aufbewahrung, Löschung, Export und Wiederherstellung müssen Rohbeobachtungen, Favoriten, Zuordnungen, Trendstände, Triggerentscheidungen und Versandprotokolle gemeinsam berücksichtigen. Ein Archiv ist kein Backup; gelöschte Inhalte dürfen durch Wiederherstellung nicht unkontrolliert wieder sichtbar werden.

## Reihenfolge

1. Bestehende Modulpfade für Beobachtungen, Favoriten/Wiederholungen, Archive und Ereignisse charakterisieren. Tatsächliche Produzenten von lediglich vorgesehenen Feldern unterscheiden.
2. Diese Anforderungen in die gemeinsame Modulmatrix aufnehmen, einschließlich des [administrativen Assetbereichs](AURELIA_ADMIN_ASSETS_VORMERKUNG_2026-10-09.md).
3. Vergleichsregeln und fachliche Zuordnungen mit dem Betreiber festlegen; erst danach Datenstruktur und Adapterverantwortung entscheiden.
4. Später eine berechtigungsgeschützte Übersicht vorbereiten und prüfen. Trigger zunächst ohne Versand anhand synthetischer Ereignisse testen, danach getrennt freigeben.

Heute wurden keine Mail, neue Analyseformel, semantische KI-Suche, automatische Favoritenübernahme oder ausführbare Trigger eingerichtet. Die [gemeinsamen Datenbereiche](AURELIA_DATENDOMAENEN_ECHTZEIT_2026-10-09.md) werden um diese Vorgabe ergänzt; bestehende Produktquellen bleiben unverändert.

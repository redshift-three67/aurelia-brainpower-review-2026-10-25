# AURELIA Zwei-Spuren-Qualitätsstrategie

```yaml
effective_from: 2026-08-26
scope: engineering-process-and-review-routing
operator_approved_for_local_documentation: true
version_control_state: uncommitted-by-operator-boundary
push_authorized: false
server_mutation: false
history_rewrite: false
```

Diese Direktive steuert Modell-, Reasoning-, Review- und Evidenzaufwand nach
dem Schadenspotenzial einer Aufgabe. Sie senkt weder Produkt-, Sicherheits-
noch Abnahmeanforderungen. Produktregeln in `AGENTS.project.md`, aktive
Ground-Zero-Gates und ausdrücklich freigegebene Spezifikationen behalten
Vorrang.

Die Direktive ersetzt für noch nicht abgeschlossene Arbeiten die pauschale
Anforderung, jede Änderung unabhängig vom Risiko durch einen Implementierer,
einen vollständigen Spezifikationsreviewer und einen vollständigen
Qualitätsreviewer bearbeiten zu lassen. Historische Reviewentscheidungen und
Evidenz bleiben unverändert.

## 1. Unveränderliche Qualitätsbasis

Unabhängig von der Spur gelten immer:

1. Die Aufgabe besitzt einen klaren Scope, eine erlaubte Mutationsgrenze und
   nachprüfbare Erfolgskriterien.
2. Kein PASS wird ohne frische, zur Behauptung passende Evidenz erklärt.
3. Ein fehlender, unlesbarer oder widersprüchlicher Nachweis ist kein PASS.
4. Secrets, Art.-9-Daten und lokale Analyse-`source/`-Ordner gelangen weder in
   Prompts noch in Reviewerpakete oder Git.
5. Externe Reviewer entscheiden nicht über Push, Destruktion, Serverzugriff
   oder ein Projektgate.
6. Publikations-, Server- und History-Grenzen werden durch die Wahl einer Spur
   niemals erweitert.
7. Bei unklarer Risikoklasse gilt fail-closed die kritische Spur B.

## 2. Spur A — Fast Assurance

Spur A ist nur zulässig, wenn **alle** folgenden Bedingungen erfüllt sind:

- kein Secret-, Datenschutz-, Auth-, Mandanten-, Kryptografie-, Recovery-,
  Migrations-, Kernel-, Server- oder Publikationsbezug;
- keine Änderung eines öffentlichen oder sicherheitsrelevanten Vertrags;
- kein Risiko von Datenverlust, Berechtigungsgewinn oder externer Mutation;
- das Ergebnis ist durch deterministische Befehle vollständig prüfbar;
- eine Fehlentscheidung ist lokal, reversibel und vor dem nächsten Gate
  erkennbar.

Typische Spur-A-Aufgaben sind read-only Inventuren, Git-Refvergleiche,
Format-/Linkprüfungen, Statusdarstellungen, mechanische Dokumentpflege und
bereits vertraglich festgelegte, isolierte Toolchainkorrekturen.

### Ablauf A

1. Der primäre AURELIA-Agent prüft Scope, Branch und Mutationsgrenze.
2. Er führt die Änderung oder Analyse selbst aus.
3. Er führt alle deterministischen Abnahmebefehle frisch aus.
4. Er prüft den Diff gegen Scope, Platzhalter und unbeabsichtigte Dateien.
5. Nur ein vollständig grüner, erklärbarer Befund darf abgeschlossen werden.

Ein separater LLM-Reviewer ist in Spur A nicht obligatorisch. Jede
unerwartete Abweichung, Vertragsunklarheit oder nicht deterministisch
entscheidbare Frage stuft die Aufgabe sofort zu Spur B hoch.

## 3. Spur B — Critical Assurance

Ein einziges der folgenden Merkmale erzwingt Spur B:

- Authentisierung, Autorisierung, Tenant-/Client-Isolation oder Rollen;
- Secrets, Credentials, Egress, personenbezogene oder Art.-9-Daten;
- Kryptografie, Signaturen, Recovery, Backup oder Restore;
- Datenbank-/Schemamigration, Löschung, Reinstallation oder Partitionierung;
- Kernel-ABI, Computation Passport, CopyGuard oder Sicherheitsgate;
- Server-, Netzwerk-, Firewall-, SSH-, IPMI-, GPU- oder USB-Arbeit;
- Änderung eines normativen Vertrags oder einer externen Schnittstelle;
- Publikation, Gatefreigabe oder ein Fehler mit hohem Schadenspotenzial.

### Ablauf B

1. Vor der Implementierung werden Vertrag, Nichtziele, erlaubte Dateien,
   Fehlerverhalten und Abnahmebefehle schriftlich fixiert.
2. Verhalten wird per TDD oder gleichwertigem nachweisbarem RED/GREEN-Verfahren
   implementiert.
3. Der Implementierer prüft den vollständigen relevanten Test- und Diffscope.
4. Ein fokussiertes Spezifikationsreview vergleicht ausschließlich Vertrag,
   relevanten Diff und Evidenz. Es liest nicht erneut das gesamte Projekt.
5. Nur nach Spec-PASS folgt ein separates Qualitäts-/Securityreview.
6. Findings werden nach Schwere, Vertragspunkt, Evidenz und konkreter
   Korrektur angegeben. P0 bis P2 blockieren den nächsten Schritt.
7. Nach Korrektur wird nur der betroffene Reviewumfang plus notwendige
   Regression erneut geprüft. Eine Vollwiederholung braucht einen geänderten
   Vertrag oder einen systemischen Befund.
8. Die primäre AURELIA-Instanz verifiziert alle Reviewerbefunde und trifft die
   endgültige Gateentscheidung.

## 4. Reviewpaket und Stoppregeln

Ein Reviewer erhält ein minimales, vollständiges Paket:

- Ziel und Risikoklasse;
- maßgebliche Vertragsabschnitte;
- exakter Diff oder exakt benannte Dateien;
- Abnahmebefehle und deren frische Ergebnisse;
- bekannte offene Findings;
- explizite Nichtziele und verbotene Aktionen.

Nicht enthalten sind der vollständige Chatverlauf, unbeteiligte historische
Analysen, Secrets, Rohquellen und bereits abgenommene unveränderte Flächen.

Pro Reviewstufe ist regulär eine Korrekturschleife vorgesehen. Bleibt danach
ein P0–P2-Befund offen oder entsteht ein neuer systemischer Befund, stoppt die
Arbeit zur Konsolidierung statt weitere Reviewer rekursiv zu starten.

## 5. Modell- und Reasoningrouting

| Aufgabe | Primärkonfiguration | Separater Review |
|---|---|---|
| Read-only Status, Git, deterministische Inventur | Sol `medium` | keiner |
| Mechanische, isolierte Spur-A-Änderung | Terra `high` oder Sol `medium` | nur bei Eskalation |
| Kritische Implementierung mit festem Vertrag | Sol `high` | fokussiert, erst nach GREEN |
| Spec-Review einer kritischen Änderung | Sol `high` oder geeignetes externes Modell | primär nachverifiziert |
| Security-, Datenschutz-, Migrations- oder Gateentscheidung | Sol `xHigh` | unabhängig, falls materiell |

`xHigh` wird nicht als Dauerstandard verwendet. Es ist nur zulässig, wenn die
Aufgabe nachweisbar von zusätzlicher Exploration oder sicherheitskritischer
Konsolidierung profitiert. Ein günstigeres Modell darf mechanische Prüfungen
oder einen eng begrenzten, sanitisierten Cross-Check übernehmen; sein Ergebnis
ist niemals alleinige Abnahme.

## 6. Token- und Laufzeitdisziplin

- Eine neue CLI-/App-Session beginnt pro Gate oder klar abgegrenztem
  Arbeitspaket mit der kanonischen Lesereihenfolge, nicht mit dem gesamten
  alten Chatverlauf.
- Jeder Vertrag und jede Grenze wird im Prompt genau einmal genannt.
- Reviewer lesen nur die seit dem letzten PASS geänderte Fläche.
- Unabhängige deterministische Prüfungen dürfen parallel laufen; semantische
  Reviewstufen bleiben sequenziell.
- Während laufender Arbeit erfolgt spätestens nach 60 Sekunden ein knapper
  Statushinweis. Lange, stille Reviewer-Warteintervalle werden vermieden.
- Ein schnelleres oder günstigeres Ergebnis zählt nur, wenn dieselben
  Erfolgskriterien und Evidenzpflichten erfüllt sind.

## 7. Aktuelle Einordnung

Die Dokumentation dieser Direktive ist Spur A mit primärer Gegenprüfung. Die
Korrektur des fail-closed Publikationsgraph-Scanners ist wegen Credential- und
Publikationsbezug Spur B. Task 4 bleibt bis zu erneutem Task-3-Spec-PASS und
anschließendem Qualitäts-PASS gesperrt.

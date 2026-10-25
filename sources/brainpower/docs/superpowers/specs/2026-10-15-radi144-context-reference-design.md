# Radi144 – unveränderte Kontext-/Zeitreferenz

Betreiberentscheidung vom 15.10.2026: „Ja, fahre So fort“ zur Empfehlung, die neu erkannten Abweichungen zunächst ohne Originaländerung zu charakterisieren. Keine Korrekturfreigabe. Vorpunkt `checkpoints/Aurelia-P3-Radi144-Context-20261015-062425Z`.

## Ziel und Grenze

Acht genaue Original-AST-Funktionskörper: aus `app/api/resonance.py` `_client_data_from_registry_entry`, `_resolve_client_data_by_id`, `_build_client_data`, `_mirror_api_session`, `_split_focus_sequence`, `_default_client_data`; aus `app/algorithms/client_signature.py` `calculate_birth_frequency`, `_to_julian_day`. Keine Produktmodule/-klassen initialisieren; zwei Originalmethoden an ein eigenes Testobjekt binden. Alle anderen Originaldateien nur als Kontext-/Typquellen lesen und hashen.

Standardbibliothek, originales datetime/hashlib/re, kontrollierter Logger und ausschließlich In-Memory-Registry/Session. Direktes `model_dump()` ist ausdrücklich ein Double, das native date/time unverändert liefert; keine echte Pydantic- oder HTTP-Abnahme. Keine NumPy-/Pillow-/Torchausführung, UI, Dateien/Stores oder tatsächliche Authentisierung. Kein Server, WSL, Access, neue Installation oder Livezustand.

Berechenbare Zeitbeispiele nutzen 2000-01-01, ohne Ort: Julian-Tag2451545, Datumsanteil327.0; HH:MM12:30 ergänzt52.08333333333334. `time(12,30)`, fehlende/falsch formatierte Zeit sowie HH:MM:SS werden getrennt gegen diese Grenzen geprüft. Native Datumsobjekte müssen mit dem Stringdatum übereinstimmen; nur Zeitanteil, nicht ganze Geburtsfrequenz, geht im bekannten Fehlerpfad verloren. Keine aktuelle Organuhr in diesen ausgewählten Funktionen, kein Stochastik-/Precision-Nachweis.

## Zwölf feste Fallgruppen

1. `01_birth_string_hhmm`: Originaldatum/-zeitstrings, unabhängig festgelegte numerische Erwartung.
2. `02_birth_native_date_time`: natives Datum und native Zeit, Vergleich mit gleichem Datum ohne Zeit und mitHH:MM.
3. `03_birth_seconds_and_invalid_time`: HH:MM:SS und unlesbare Zeit ohne Zeitbeitrag.
4. `04_birth_invalid_date`: Originalfallback0 plus kontrollierte Warnung.
5. `05_inline_priority_native_types`: Inline vor ID, native Typen bleiben, kein Registryzugriff beim Build.
6. `06_registry_projection`: exakter Fünffeldumfang, metadata nicht übernommen, Nachnamensliste kopiert.
7. `07_missing_id_404`: Lookup fehlt,404 ohne Session.
8. `08_mixed_inline_id_session`: InlineA berechnet/weitergereicht, RegistryIDB in synthetischer Session; Originalkonflikt als erwarteter Istbefund.
9. `09_id_only_session`: ID-Kontext und Session-ID konsistent.
10. `10_inline_only_session`: kontrolliertes get_or_create, kein ID-Lookup; keine reale Identitätsalgorithmusprüfung.
11. `11_mixed_missing_id_mirror_404`: Inlineaufbau gelingt, Sessionmirror404, keine Session.
12. `12_standalone_default`: ursprünglicher Vierfeldfallback ohne persönliche Daten.

Pro Gruppe mindestens drei tatsächlich geprüfte Erwartungen; vollständige kanonische kleine Ergebnisobjekte inklusive Eingaben/Typen/Lookup-/Speicherversuch und bestätigter synthetischer Session. Keine echten Datensätze oder privaten Identitäten. Native date/time in Belegen mit explizitem Typ und ISOwert serialisieren; nicht als Produktnormalisierung einsetzen.

## Ausführung und Nachweise

Quellen-/Werkzeug-/benannte Gitbindung vor/nach, bereinigte Kindumgebung, frische Kennungen `context-run-1/2`,120s technische Grenze, versteckte Windowskindprozesse. Neues Gate bleibt bis zum unabhängigen SPEC→QUALITY-Vorreview geschlossen. Standardbibliotheken und acht ASTs vor dem Aufrufguard vorbereiten; keine ausführbaren Defaults/Dekoratoren, nur genaue Namen, unveränderte Funktionskörper mit zukünftigen Annotationen. Während Originalaufrufen Datei-/Import-/Netz-/Prozess-/Registry-/ctypes-/Codegenerierung und Standardstreamzugriff sperren. Auditguard ist keine Betriebssystemsandbox; installierte Standardbibliothek/Interpreter bleiben Vertrauensvoraussetzung.

Zwei vollständige Ergebnisse ausschließlich ohne Laufkennung vergleichen. Bei unerwartetem Fehler Ursache/Nachprüffehler erhalten und anhalten. Danach Gate schließen, Bericht/Plan/Wiederaufnahme und lokalen Vorher-/Nachherpunkt mit Hash-/Archiv-/Rücklesen aktualisieren. Gesamt-P3/P4/P5-Gates nicht ersetzen.

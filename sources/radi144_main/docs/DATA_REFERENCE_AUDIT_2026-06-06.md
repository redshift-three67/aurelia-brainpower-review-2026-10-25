# Radi144 db_import Referenzdaten-Audit

Stand: 2026-06-06
Projektwurzel: `/home/klaus999/projects/Radi144`
Audit-Ziel: `db_import/`

## 1. Zweck

Dieses Dokument klassifiziert `db_import/` vor einer kuratierten initialen Git-Baseline. Ziel ist zu entscheiden, ob der Ordner als produktiver Referenzdatenbestand aufgenommen werden kann oder ob er wegen Laufzeit-, Personen-, Duplikat- oder Herkunftsrisiken aus der Baseline ausgeschlossen werden muss.

Wichtig: Die Inhalte wurden fuer diese Klassifizierung statisch analysiert. Es wurden keine Import-/Ranking-/Analysejobs auf den Daten ausgefuehrt und keine Kernengine-Parameter veraendert.

## 2. Produktive Verwendung im aktuellen Code

Verifizierte aktuelle Verbraucher:

- `app/api/resonance.py`
  - `DB_IMPORT_DIR = PROJECT_ROOT / "db_import"`
  - `_list_db_files()` listet rekursiv `*.txt`
  - `/db/list` gibt verfuegbare Datenbanken zurueck
  - `/db/rank` fuehrt zweiphasiges DB-Ranking aus:
    1. Dateinamen-Vorfilter ueber Resonanz gegen den Dateinamen
    2. Inhalts-Scan der Top-30-Dateien mit bis zu 50 Eintraegen je Datei
- `generate_matrix.ps1`
  - nutzt `$PSScriptRoot/db_import`
  - sucht rekursiv `.txt`-Dateien fuer Datenbank-Vorwahl/Wissensfelder/Scan
- `user_workflow.html`
  - verweist beispielhaft auf Server-Pfade unter `db_import/`, u.a. fuer Bildpfad-Eingaben

Bewertung:

`db_import/` ist kein bloßes Archivverzeichnis, sondern Teil der aktuellen DB-/Wissensfeld-Funktionalitaet. Ein pauschales Ignorieren wuerde API-/PowerShell-/Workflow-Funktionalitaet entwerten.

## 3. Inventar

Statisches Ergebnis:

| Metrik | Wert |
|---|---:|
| Dateien gesamt | 59 |
| Gesamtgroesse | 3,857,602 Bytes |
| Dateitypen | 59 x `.txt` |
| JSON-Dateien | 0 |
| Nicht-leere Textzeilen | 83,751 |
| Leere Dateien | 0 |
| Dekodierung beim ersten Versuch | 45 x UTF-8, 14 x Latin-1 |
| Nicht dekodierbare Dateien | 0 |

## 4. Groesste Dateien

| Datei | Bytes |
|---|---:|
| `BIOLOGICAL.txt` | 1,025,688 |
| `BIOLOGICAL_ORGANS_COPEN_ORGANS & SYMPTOMS_RATES.txt` | 507,297 |
| `BIOLOGICAL_COMPLETE.txt` | 461,419 |
| `ENERGY_Meridian_Gesamt_5_Ebenen_gesamt.txt` | 420,086 |
| `Meridian_Gesamt_5_Ebenen_gesamt.txt` | 388,541 |
| `ANALYSIS_COMPLETE.txt` | 222,252 |
| `ANALYSIS_EXTRA.txt` | 127,497 |
| `ANALYSIS_Allergie_Gesamt.txt` | 109,498 |
| `ENERGY_TCM_RATES.txt` | 59,435 |
| `Meridian_Gesamt_neu.txt` | 55,142 |
| `ENERGY_Meridian_Gesamt_neu.txt` | 55,142 |

Bewertung:

Die Groesse ist fuer eine Git-Baseline technisch unkritisch. Der Ordner ist groß genug fuer eine explizite Review, aber nicht groß genug, um Git-LFS oder externes Artefakt-Storage zwingend zu machen.

## 5. Kategorien

Heuristische Dateikategorien nach Dateinamen:

| Kategorie | Anzahl |
|---|---:|
| `ENERGY_*` | 23 |
| `ENERGY_OR_LEGACY_DUP` | 10 |
| `BIOLOGICAL*` | 9 |
| `ANALYSIS_*` | 9 |
| `MIXED_OR_LEGACY` | 8 |

Kandidaten fuer aktive Datenfamilien:

- Analyse/Rife/Symptoms/Time/Percent/Lifetime: `ANALYSIS_*`
- biologische/organische Raten: `BIOLOGICAL*`
- Energie/TCM/Meridiane/Chakren/Acupuncture/Narayani/Gems: `ENERGY_*`
- Legacy-nahe deutsche Namen ohne Prefix koennen Duplikate oder Ursprungstabellen sein

## 6. Duplikate

Exakte SHA256-Duplikatgruppen wurden gefunden:

| Gruppe | Dateien | Bytes je Datei |
|---|---|---:|
| 1 | `BIOLOGICAL_KöRBLER_BODY_CLYSTALS_BASE_44_RATES.txt` / `BIOLOGICAL_KöRBLER_CLYSTALS_BASE_44_LIST_RATES.txt` | 7,331 |
| 2 | `Medizin der Emotionen.txt` / `ENERGY_Medizin_der_Emotionen.txt` | 10,321 |
| 3 | `3 Energiekörper-Reinigung-Pet.txt` / `ENERGY_Energiekörper_Reinigung.txt` | 1,063 |
| 4 | `Meridian_Gesamt_neu.txt` / `ENERGY_Meridian_Gesamt_neu.txt` | 55,142 |
| 5 | `ENERGY_Elimination_Reinigung.txt` / `1 Elimination_Reinigung-Pet.txt` | 3,419 |
| 6 | `Schadstofffrequenzen.txt` / `Schadstofffrequenzen - Kopie.txt` | 2,014 |
| 7 | `Aura Heilung.txt` / `ENERGY_Aura_Heilung.txt` | 7,084 |
| 8 | `Petrov_RATES.txt` / `ENERGY_Petrov_RATES.txt` | 1,114 |
| 9 | `ENERGY_ACUPUNCTURE_RATES - Kopie.txt` / `ENERGY_ACUPUNCTURE_RATES.txt` | 38,520 |

Bewertung:

Duplikate sind vorhanden, aber eine sofortige Loeschung waere vor einer Baseline riskant, weil Dateinamen selbst im aktuellen Ranking als Resonanz-/Vorfilter-Signal genutzt werden. Daher: Duplikate zunaechst dokumentiert belassen; spaeter nur mit expliziter Nutzerfreigabe und Rueckwaertskompatibilitaetsstrategie konsolidieren.

## 7. Sensibilitaets-/Personendaten-Heuristik

Geprueft wurden Muster fuer:

- E-Mail-Adressen
- IBAN-aehnliche Sequenzen
- telefonnummernaehnliche Sequenzen

Ergebnis:

- E-Mail-Treffer: 0
- IBAN-aehnliche Treffer: 0
- telefonnummernaehnliche Treffer: viele, aber aufgrund der Dateien/Ratenstruktur sehr wahrscheinlich numerische Frequenz-/Rate-/Codefolgen, nicht Telefonnummern

Auffaellige Dateinamen, die vor einem finalen öffentlichen Commit manuell bewertet werden sollten:

- `Klaus_Test_Raten_V1.txt`
- `HA_24_01_26_09_00.txt`
- `Raphael_WS_Physis.txt`

Bewertung:

Es gibt nach statischer Heuristik keinen direkten Beleg fuer personenbezogene Kontaktdaten. Einzelne Dateinamen koennen aber personenbezogen oder projekthistorisch wirken und sollten vor einer wirklich externen/veroeffentlichten Baseline noch manuell freigegeben oder neutralisiert werden.

## 8. Herkunfts-/Lizenzrisiko

Nicht abschliessend geklaert.

Die Dateinamen deuten auf kuratierte Frequenz-/Ratenlisten, Copen/Rife/TCM/Narayani/Petrov/Körbler-Referenzen und projektinterne Listen. Ohne Herkunftsnotizen oder Lizenzdatei kann kein rechtssicheres Lizenzurteil getroffen werden.

Empfehlung:

- Fuer eine lokale/private Git-Baseline: als Referenzdaten-Kandidat aufnehmen moeglich.
- Fuer eine veroeffentlichte oder geteilte Remote-Baseline: vorher Herkunft/Lizenz/Weitergaberecht pruefen.
- Optional spaeter `db_import/README.md` oder `docs/REFERENCE_DATA_PROVENANCE.md` anlegen.

## 9. Git-Baseline-Entscheidung

Aktuelle Entscheidung fuer die lokale kuratierte Baseline:

`db_import/` bleibt Git-kandidatenfaehig und wird nicht ignoriert.

Begruendung:

1. Aktuelle API- und PowerShell-Funktionen verwenden diesen Ordner produktiv.
2. Es handelt sich um Text-Referenzdaten, nicht um Runtime-JSON oder Klientendaten.
3. Die Gesamtgroesse ist Git-tauglich.
4. Personendaten-Heuristik zeigt keine E-Mail-/IBAN-Treffer.
5. Duplikate sind dokumentiert, aber aktuell funktional potenziell relevant, weil Dateinamen als Vorfilter-Signal genutzt werden.

Einschraenkung:

Vor einem externen Remote-Push oder einer Veroeffentlichung muss die Herkunfts-/Lizenzfrage separat freigegeben werden.

## 10. Automatisierter Guard

Erweitert wurde:

- `tests/test_repository_data_hygiene.py`

Neue Charakterisierungs-/Baseline-Regel:

- `db_import/` muss existieren.
- Es muessen 59 `.txt`-Referenzdaten vorhanden sein.
- repräsentative zentrale Dateien bleiben Git-kandidatenfaehig:
  - `db_import/BIOLOGICAL.txt`
  - `db_import/ANALYSIS_COMPLETE.txt`
  - `db_import/ENERGY_TCM_RATES.txt`
- `db_import/` darf keine Runtime-JSON-Dateien enthalten.

Hinweis: Dieser Test ist Charakterisierungsabdeckung, kein Produktionscode-TDD-Zyklus. Er passierte sofort, weil er den aktuellen, gewuenschten Bestand einfriert.

## 11. Nicht veraendert

Nicht veraendert:

- Inhalte von `db_import/`
- Kernengine
- Resonanzscore
- Matrixlogik
- DB-Ranking-Algorithmus
- Top-30/Top-50-Scanlogik
- Runtime JSON-Daten
- Secret-/Deploy-Dateien

## 12. Naechste Prioritaet

Nach diesem Audit sind vor einer Initial-Baseline noch zu entscheiden:

1. Sonderfaelle Root-Restore/Packaging:
   - `create_restore_point.py`
   - `create_restore.ps1`
   - `finalize_project.py`
2. Danach kuratierte Baseline-Gruppen vorbereiten.
3. Kein `git add .`; stattdessen gezielte Gruppenaufnahme nach expliziter Freigabe.

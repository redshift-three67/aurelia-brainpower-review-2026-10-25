# Workbench Gate 3 Scanprofil-Pool Design

**Datum:** 2026-07-27
**Status:** Freigegeben
**Scope:** Gate 3 des freigegebenen Operator-Workbench-Korrekturplans

## 1. Ziel

Vor Preview und Start muss die Workbench eindeutig zeigen, welcher Profilpool tatsaechlich gescreent wird. Interne Scanprofile und externe Registry-Quellen werden strikt getrennt. Die aktuell 16 Registry-aktiven Quellen werden erklaert und inspizierbar, erhalten aber weder einen wirkungslosen Aktivierungsschalter noch eine Scanwirkung.

Der vom Operator gepruefte interne Pool wird ueber einen deterministischen Fingerprint an Preview und Start gebunden. Ein fehlender oder veralteter Fingerprint stoppt den Request, bevor eine Operation-ID reserviert oder ein Scanprozess erzeugt wird.

## 2. Ist-Zustand und Problem

Die heutige Anzeige

> Externe Quellen aktiv: 16; davon als Scanprofile integriert: 0.

vermischt zwei verschiedene Begriffe:

- `aktiv` bedeutet nur `enabled=true` und `status=active` in der lokalen `SourceRegistry`;
- `als Scanprofil integriert` ist im Workbench-Katalog fest auf `0` und `registry_only` gesetzt.

Die 16 Quellen beeinflussen heute weder Screening-Pool, Kandidaten, Scores noch Top-N. `scan top3-scan` bezieht seinen Pool ausschliesslich aus `core.profile_sync.get_top_n_analysis_profiles_by_level()` und reicht interne Profil-IDs an `field multiplex-scan` weiter.

Ein normaler Workbench-Nutzer kann externe Quellen nicht als Scanprofile aktivieren. Die Default-Registry ist legacy/read-only, aktuelle Quellen besitzen keinen freigegebenen Profil-/Gruppen-/Rate-Vertrag, und der Admin-Catalog-Runtime-Adapter ist nicht mit dem produktiven Scanpfad verdrahtet.

## 3. Verbindliche Scope-Grenzen

Gate 3 implementiert:

- vollstaendige Wahrheit ueber den aktuellen internen Screening-Pool;
- klare Trennung von Registry-Lifecycle und Scanwirkung;
- inspizierbare, aber nicht scanwirksame externe Quellen;
- Poolquelle, sichere Revisionsdarstellung und deterministischen Fingerprint;
- alphabetische Suche in der internen Profilliste;
- fail-closed Bindung des bestaetigten Pools an Preview und Scanstart;
- Loading-, Timeout-, Fehler- und Retry-Zustaende;
- responsive und tastaturbedienbare Darstellung.

Gate 3 implementiert ausdruecklich nicht:

- Source-Enable/Disable in der normalen Workbench;
- Import, Normalisierung, Publish oder Aktivierung externer Profile;
- neue Netzwerkabfragen;
- Aenderungen an Scoreformel, Top-N-Logik oder internen Profilen;
- produktive Admin-Catalog-Autoritaet;
- stillen Fallback von einer aktivierten Catalog-Autoritaet auf Legacy.

Die echte externe Profilintegration bleibt Gate 14. Sie benoetigt einen revisionsgebundenen Profil-, Gruppen- und Rate-Provenienzvertrag sowie Admin-, Tenant- und Runtime-Gates.

## 4. Autoritaeten

### 4.1 Aktuelle Scanprofil-Autoritaet

`core.profile_sync` bleibt in Gate 3 die einzige produktive Profilautoritaet. Der API-Katalog und `top3-scan` muessen denselben Funktionspfad `get_top_n_analysis_profiles_by_level(profile_level)` verwenden.

Der Response weist diese Autoritaet als `legacy` mit dem sichtbaren Label `Legacy` aus. Eine versionierte Revision existiert fuer diesen Pool nicht; deshalb ist `revision=null` die einzig wahrheitsgetreue Angabe.

### 4.2 Externe Registry-Autoritaet

Die `SourceRegistry` beschreibt Repository-Lifecycle und Readiness. `active` bedeutet nicht Netzwerkzugriff, importierte Daten oder Scanwirkung. Gate 3 darf diese Eintraege nur als separate Registry-Information anzeigen.

### 4.3 Zukunftspfad

`Catalog Shadow` und `Catalog aktiv` sind reservierte Poolquellen fuer Gate 14. Gate 3 rendert die vom Backend gelieferte Quelle, aktiviert aber keinen Catalog-Provider.

## 5. API-Datenvertrag

`GET /api/workbench/scan-profile-catalog?profile_level=<1..5>` liefert mindestens; die Workbench selbst bietet weiterhin nur die freigegebenen Level 1 bis 4 an:

```json
{
  "schema_version": 1,
  "profile_level": 3,
  "pool_authority": {
    "source": "legacy",
    "label": "Legacy",
    "revision": null,
    "revision_short": null,
    "fingerprint": "<64 lowercase hex characters>",
    "fingerprint_short": "<first 12 hex characters>"
  },
  "internal": {
    "count": 55,
    "profiles": [
      {"id": "pathogen", "label": "Pathogene Belastungen"}
    ]
  },
  "external": {
    "count": 0,
    "profiles": [],
    "integration_status": "registry_only",
    "scan_effect": false,
    "activation_available": false,
    "activation_gate": "gate_14",
    "active_source_count": 16,
    "active_sources": [
      {
        "id": "nlm_mesh",
        "label": "NLM MeSH",
        "scan_effect": false,
        "reason_code": "registry_metadata_only"
      }
    ]
  },
  "total_scan_profiles": 55
}
```

Nur sichere, bereits in der Workbench verwendete Source-ID/-Label-Werte werden angezeigt. URLs, lokale Pfade, Grants, Secrets und Adminmetadaten bleiben ausgeschlossen.

`external.count` bleibt aus Kompatibilitaetsgruenden die Zahl externer Scanprofile und damit `0`. `active_source_count` bezeichnet eindeutig die separate Registry-Menge.

## 6. Fingerprint-Vertrag

### 6.1 Kanonischer Input

Der SHA-256-Input ist kanonisches UTF-8-JSON mit:

```json
{
  "schema_version": 1,
  "profile_level": 3,
  "pool_source": "legacy",
  "profiles": [
    {"id": "<authoritative id>", "label": "<authoritative label>"}
  ]
}
```

Serialisierung:

- `ensure_ascii=false`;
- `sort_keys=true`;
- Separatoren `(',', ':')`;
- Profilreihenfolge bleibt exakt die autoritative Screening-Reihenfolge.

IDs und Labels werden beide gebunden. Die Reihenfolge kann bei Scoregleichstand relevant sein; Labels koennen im bestehenden Phase-2-Pfad als Fallbackfokus wirken. Eine Aenderung an Level, Quelle, ID, Label oder Reihenfolge erzeugt deshalb einen anderen Fingerprint.

### 6.2 Nicht enthalten

Registry-Quellen, Registry-Revision und Registry-Status sind nicht enthalten, solange `external.scan_effect=false` gilt. Eine reine Registry-Aenderung darf den internen Scanpool nicht als geaendert ausweisen.

### 6.3 Darstellung

Das Backend liefert den vollstaendigen 64-stelligen Fingerprint fuer die Requestbindung und die ersten 12 Zeichen fuer die UI. Die UI zeigt niemals selbst berechnete Hashes.

## 7. Preview- und Startvertrag

`Phase1ScanRequest` erhaelt das Pflichtfeld:

```text
scan_profile_pool_fingerprint: 64 lowercase hexadecimal characters
```

Die Workbench uebernimmt ausschliesslich den vollstaendigen Fingerprint aus dem aktuell erfolgreichen Katalogresponse fuer dasselbe `profile_level`.

Vor `scan_preview` und vor `_start_operation()` in `scan_job_start` gilt:

1. internen Pool fuer `request.profile_level` erneut aus `core.profile_sync` laden;
2. aktuellen Fingerprint serverseitig berechnen;
3. Requestwert mit dem aktuellen Wert vergleichen;
4. bei Abweichung HTTP 409 mit redigierter Meldung „Scanprofil-Pool hat sich geaendert. Bitte neu laden und erneut pruefen.“;
5. keinen Launcher aufrufen, keine Operation-ID reservieren und keinen Scanjob erzeugen.

Ein syntaktisch fehlender oder ungueltiger Fingerprint wird bereits als HTTP 422 abgelehnt. Der Fingerprint wird nicht an CLI, Export oder Berichtstext weitergereicht. Er ist Bestandteil des Request-/Idempotenzvertrags, aber kein Analyseparameter.

## 8. UI-Vertrag

### 8.1 Zusammenfassung

Die Reviewkarte verwendet ausschliesslich Response- und aktuelle Formdaten:

> Level 3 prueft 55 interne Screening-Profile; anschliessend werden Top-5 vollstaendig analysiert.

Zahlen werden nicht im Frontend hardcodiert.

### 8.2 Badges

- Poolquelle: `Legacy`, `Catalog Shadow` oder `Catalog aktiv` aus dem Response;
- Revision nur, wenn vorhanden, und nur in sicherer Kurzform;
- Fingerprint als 12-stellige Kurzform.

### 8.3 Interne Profile

Ein `<details>` enthaelt:

- sichtbares Suchfeld mit Label;
- case-insensitive Suche ueber Profil-ID und Label;
- alphabetische Anzeige nach Label, ohne den autoritativen Response zu mutieren;
- Ergebniszaehler „X von Y Profilen“;
- sichere DOM-Erzeugung ueber `textContent`, kein `innerHTML`.

Eine leere Suche zeigt einen erklaerten Nulltreffer, niemals einen leeren bestaetigten Pool.

### 8.4 Externe Registry-Quellen

Die primaere Aussage lautet:

> 16 Registry-Quellen sind betriebsbereit; 0 als Scanprofile freigegeben. Diese Quellen haben keine Wirkung auf den aktuellen Scan, Profilpool oder Score. Externe Scanprofile koennen erst nach validierter Catalog-Freigabe in Gate 14 aktiviert werden.

Ein separates `<details>` listet Source-ID und Label alphabetisch. Jeder Eintrag ist als „keine Scanwirkung“ markiert. Es gibt keine Checkbox, keinen Toggle und keinen Aktivierungsbutton.

### 8.5 Loading und Fehler

- Bei `loading`: Skeleton/Status „Scanprofil-Pool wird geladen“, Preview und Start deaktiviert.
- Bei Timeout/Fehler: HTTP-Klasse und redigierter Grund, Retry-Button, Preview und Start deaktiviert.
- Bei `ready`: Aktionen nur freigeben, wenn Response-Level dem aktuellen Formularlevel entspricht und der Fingerprint syntaktisch gueltig ist.
- Eine spaete Response fuer ein altes Level oder eine alte Fallgeneration darf Zustand und Aktionen nicht ueberschreiben.
- Ein Levelwechsel verwirft den alten Katalog/Fingerprint sofort.

Die bestehende Single-Flight-/Reservierungslogik bleibt zusaetzlich wirksam. Kein Katalogstatus darf einen bereits laufenden Scan entsperren.

## 9. Fehler- und Sicherheitsvertrag

- Registry- oder Profilkatalogfehler werden als redigiertes HTTP 503 abgebildet; lokale Pfade erscheinen nicht im Payload.
- Ungueltige Level werden vor Registryzugriff als HTTP 422 abgelehnt.
- Fingerprint-Mismatch ist HTTP 409 und verraet weder Profilnamen noch Serverpfade.
- Externe Quellen bleiben reine Anzeige; keine Mutation, kein Netzwerkzugriff und kein Catalog-Publish aus der Workbench.
- Der normale API-Key ist keine Adminfreigabe.
- Der Scanstart bleibt owner-/tenantgebunden und idempotent; Gate 3 aendert diese Autoritaeten nicht.

## 10. Test- und Abnahmevertrag

### Backend

- Fingerprint ist bei identischem geordnetem Pool stabil.
- Level-, ID-, Label- oder Reihenfolgenaenderung aendert den Fingerprint.
- Aenderungen ausschliesslich an Registry-Quellen aendern ihn nicht.
- Katalogresponse enthaelt Quelle, null Revision, Voll-/Kurzfingerprint und externe `scan_effect=false`-Metadaten.
- Levelzaehler werden aus realen Profilen abgeleitet, nicht hardcodiert.
- Preview und Start akzeptieren den aktuellen Fingerprint.
- Fehlender/ungueltiger Fingerprint ergibt 422.
- Veralteter Fingerprint ergibt 409 vor Launcher, Operation-Claim und Jobstart.
- Registryfehler bleiben redigiert.

### Frontend/Node

- Formpayload uebernimmt nur Fingerprint des aktuellen Levels.
- Levelwechsel loescht den Fingerprint sofort.
- Loading/Error sperren Preview und Start; Ready entsperrt nur ohne aktive Scanreservation.
- Zusammenfassung kombiniert Response-Level/-Count mit aktuellem Top-N.
- Suchfilter ist case-insensitive, alphabetisch und DOM-sicher.
- Externe Aussage nennt `active_source_count`, `count=0`, keine Scanwirkung und Gate 14.
- Keine interaktiven Aktivierungselemente im externen Quellenbereich.

### Browser

- Desktop, Tablet und 375 px ohne horizontalen Dokumentoverflow.
- Suche filtert Profile und aktualisiert den Zaehler.
- Externe Details sind tastaturbedienbar und zeigen keine Scanwirkung.
- Ladefehler zeigt Retry und haelt Aktionen gesperrt.
- Spaete Levelresponse kann den aktuellen Pool nicht ueberschreiben.
- Preview-/Startrequest enthaelt den angezeigten Vollfingerprint.

### Regression

- `top3-scan` verwendet weiterhin exakt den internen `core.profile_sync`-Pool.
- Externe SourceRegistry-Eintraege veraendern weder CLI-Kommando noch Scores oder Top-N.
- Gate-0-/Gate-1-/Gate-2-Nachbarn, vollstaendige Playwright-Suite und vollstaendige Python-Suite bleiben gruen.

## 11. Abnahmegrenze

Gate 3 ist technisch abnahmebereit, wenn:

- der Operator den konkreten internen Pool vor Start durchsuchen und pruefen kann;
- die 16 Registry-Quellen eindeutig als nicht scanwirksam erklaert sind;
- kein wirkungsloser Aktivierungsschalter existiert;
- Preview und Start nur mit dem aktuell bestaetigten Pool-Fingerprint moeglich sind;
- Fehler, Timeout und stale Responses fail-closed bleiben;
- Spec-Compliance- und Code-Quality-Review keine offenen Critical/Important Findings enthalten;
- fokussierte und vollstaendige Testmatrizen auf unveraenderten Bytes bestanden sind.

## 12. Restrisiko und Folgegate

Gate 3 beweist nur Transparenz und Bindung der heutigen Legacy-Autoritaet. Es macht externe Quellen nicht scanfaehig. Gate 14 muss vor jeder echten Integration Profil-/Gruppen-/Rate-Schemas, Source-Adapter, Revision/Hash, Adminfreigabe, Tenantbindung, Entitlements, Runtime-Provider, Shadow-Vergleich, Rollback und fail-closed Aktivierung gemeinsam abnehmen.

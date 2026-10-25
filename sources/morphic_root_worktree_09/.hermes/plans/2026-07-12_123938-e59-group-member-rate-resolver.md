# E5.9 – Vertrauenswürdiger Mitgliedsratenresolver: Freigabe- und Umsetzungsplan

> **For Hermes:** Implement gate-by-gate with strict TDD. Do not wire a productive group scan before every E5.9 gate is green and separately approved.

**Goal:** Reale Gruppenmitgliedsraten serverseitig und deterministisch aus pseudonymen `cli-...`-Referenzen auflösen, ohne Rohvektoren aus dem Browser anzunehmen, ohne historische Reports auszulesen und ohne Legacy-Daten still als vertrauenswürdig zu behandeln.

**Architecture:** E5.9 definiert zunächst die versionierte Semantik `group-member-baseline-v1`: Eine Mitgliedssignatur wird serverseitig aus der kanonischen Identitätsbasis `name + first_name + birth_date + birth_place` mit den bestehenden Defaultwerten für Bild und Planet erzeugt. Die Auflösung erfolgt über einen owner-/workspace-/tenant-gebundenen Source-Adapter und gibt Raten ausschließlich in-memory an `build_group_draft_opt_in()` weiter. Bestehende Klartext-Runtime-Manifeste werden nicht automatisch zu einer vertrauenswürdigen Gruppenquelle erklärt; Legacy-Einträge ohne explizite Owner-/Tenant-Metadaten müssen für Gruppenwirkung fail-closed bleiben.

**Stand:** 2026-07-12 12:39 CEST

---

## 1. Verifizierter Ausgangsbefund

| Befund | Codebeleg | Konsequenz |
|---|---|---|
| Der aktive Encoder benötigt Name, Vorname, Geburtsdatum und Geburtsort; Bild, Personalprofil und Planet sind optional | `core/profiles/profile.py:183-191`, `services/analysis_service.py:28-42` | Eine reproduzierbare Default-Baseline ist fachlich möglich |
| Der aktive CLI-Pfad erzeugt `ClientProfile` und Raten nur temporär | `apps/cli/commands/field.py:2936-2948` | Aktuelle Mitgliedsraten werden bisher nicht als wiederverwendbarer Snapshot gespeichert |
| `RuntimeManifestService` speichert Identitätsfelder in `clients.json` im Klartext | `core/compliance/runtime_manifest.py:108-126` | Dieser Store darf nicht ohne zusätzlichen Trust-Gate als produktive Gruppenquelle gelten |
| Client-IDs sind deterministische SHA-256-Pseudonyme aus Identitätsfeldern | `core/compliance/runtime_manifest.py:38-50` | `cli-...` kann als Lookup-Schlüssel dienen, ist aber keine Authentifizierung |
| Runtime-Clienteinträge besitzen aktuell weder `tenant_id` noch `owner_id` | `core/compliance/runtime_manifest.py:115-124` | Ein tenant-/owner-sicherer Resolver ist heute nicht möglich |
| Gruppen-Drafts werden derzeit nur nach Runtime-Pfad gehasht namespaced | `apps/web/group_drafts.py:35-39` | Vor E5.9 muss der Draft-Namespace zusätzlich an Tenant/Workspace gebunden werden |
| Es gibt keinen Client-ID-zu-Rate-Snapshot-Resolver | projektweite Suche nach `member_rates`, `rate_snapshot`, `client_id.*ClientProfile` | Neue, versionierte Resolverlogik ist notwendig |
| Report-/Artefaktpfade enthalten historische Ergebnisse | `RuntimeManifestService.register_artifact()` | Reports dürfen nicht als Rate-Quelle geparst werden: inkonsistent, schwer redigierbar und löschungsanfällig |

---

## 2. Gewählte fachliche Semantik

### `group-member-baseline-v1`

Für jedes eingewilligte Gruppenmitglied wird serverseitig exakt folgender `ClientProfile` erzeugt:

```python
ClientProfile(
    name=identity.last_name,
    first_name=identity.first_name,
    birth_date=identity.birth_date,
    birth_place=identity.birth_place,
    image_signature=None,
    personal_profile=None,
    planet_type="",
)
```

Danach wird ausschließlich `AnalysisService.encode_profile(profile)` verwendet.

Diese Semantik bedeutet ausdrücklich:

- **kein** Wiederverwenden alter Scanresultate;
- **kein** Parsen von Reports oder Exportdateien;
- **kein** Bild, Planet oder Profiltemplate aus früheren Runs;
- **kein** Browser-Upload von Ratenarrays;
- deterministische, versionsgebundene Identitäts-Baseline;
- spätere abweichende Semantik benötigt `group-member-baseline-v2` oder `group-member-observed-v1`, niemals stilles Überschreiben.

---

## 3. Gate-Reihenfolge

### Gate E5.9.0 – Gruppen-Draft-Namespace owner-/tenant-binden

**Ziel:** Ein Draft eines Tenants darf unter demselben Runtime-Pfad nicht von einem anderen Tenant gelistet oder geladen werden.

**Dateien:**
- Modify: `apps/web/group_drafts.py`
- Modify: `apps/web/main.py`
- Extend: `tests/test_web_group_drafts.py`

**RED-Tests:**
1. Gleicher Runtime-Pfad, anderer `tenant_id` → getrennte DPAPI-Verzeichnisse.
2. Gleicher Tenant, anderer Workspace → getrennte Verzeichnisse.
3. Safe-Summary enthält weiterhin keine Tenant-, Owner- oder Pfadangaben.
4. Bestehende Legacy-Drafts aus dem alten Namespace werden nicht automatisch übernommen.

**Implementierung:** `build_group_draft_store(runtime_dir, context)` hasht mindestens Runtime-Pfad, `tenant_id` und `workspace_id`. `operator_id` bleibt bewusst aus dem Pfadhash, weil OS-DPAPI bereits an den Windows-Benutzer bindet und wechselnde Hostdarstellungen keine Drafts verwaisen lassen sollen.

---

### Gate E5.9.1 – Reiner, versionierter Baseline-Resolver

**Ziel:** Pseudonyme Mitglieder aus einem explizit bereitgestellten, owner-gebundenen Identitätssource deterministisch in Baseline-Raten auflösen.

**Dateien:**
- Create: `core/profiles/group_member_rate_resolver.py`
- Create: `tests/test_group_member_rate_resolver.py`

**Verträge:**

```python
@dataclass(frozen=True)
class GroupMemberIdentity:
    client_id: str
    owner_id: str
    tenant_id: str
    first_name: str
    last_name: str
    birth_date: str
    birth_place: str
    analysis_consent: bool
    consent_version: str

class GroupMemberIdentitySource(Protocol):
    def resolve(self, client_id: str) -> GroupMemberIdentity: ...
```

**RED-Tests:**
1. Zwei synthetische Identitäten → exakt erwartete zehnwertige Baseline-Arrays.
2. Eingabereihenfolge ändert das Mapping nicht.
3. Unbekannte ID, fremder Owner/Tenant, fehlende Einwilligung, falsche Consent-Version und doppelte ID → `ValueError`/`OwnershipError`.
4. Ergebnis-Safe-Summary enthält nur Anzahl, Resolver-Version und Zweck, nie Identität oder Raten.
5. Resolver importiert keine Web-, Report-, Job-, Trace- oder Manifestmodule.

**Implementierung:** Der reine Resolver erhält `OperatorContext`, `GroupMemberIdentitySource` und eine exakte Menge pseudonymer IDs. Er erzeugt `ClientProfile` mit den oben festgeschriebenen Defaults und liefert `Mapping[str, np.ndarray]` nur in-memory zurück.

---

### Gate E5.9.2 – Runtime-Manifest nur als explizit gehärteter Source-Adapter

**Ziel:** Neue Clientregistrierungen können owner-/tenant-gebunden gelesen werden; Legacy-Einträge bleiben für Gruppenwirkung untrusted.

**Dateien:**
- Modify: `core/compliance/runtime_manifest.py`
- Create: `core/compliance/group_member_identity_source.py`
- Extend: `tests/test_runtime_privacy_manifest.py`
- Create: `tests/test_group_member_identity_source.py`

**Regeln:**
1. Neue Clienteinträge erhalten `owner_id`, `workspace_id`, `tenant_id` und eine versionierte, default-false Gruppenanalyse-Einwilligung.
2. `list_clients_safe()` bleibt redigiert.
3. Legacy-Einträge ohne diese Metadaten bleiben für bestehende Manifest-/Erasure-Funktionen lesbar, aber der Gruppenresolver lehnt sie ab.
4. Keine automatische Migration oder Einwilligungsannahme.
5. Keine Ratenarrays werden im Manifest gespeichert.
6. Die vorhandene Klartext-Speicherung wird als bestehende technische Schuld dokumentiert; E5.9 erweitert sie nicht um neue Rohdaten.

**Separate Sicherheitsentscheidung:** Vor einem echten Multiuser-/Netzwerkbetrieb ist der komplette Client-Identity-Store zu verschlüsseln oder in einen authentifizierten Tenant-Store zu migrieren. Der lokale Einoperatorbetrieb allein macht Klartext nicht zu einem allgemeinen Produktionsstandard.

---

### Gate E5.9.3 – Resolver mit lokalem Gruppen-Draft verbinden

**Ziel:** Die bestehende Gruppenmitgliedsliste wird serverseitig in Baseline-Raten aufgelöst und durch die bereits fertige Autorisierungs-/Opt-in-Kette geführt.

**Dateien:**
- Modify: `apps/web/group_analysis_activation.py`
- Extend: `tests/test_group_draft_opt_in.py`
- Create: `tests/test_group_member_resolution_activation.py`

**RED-Tests:**
1. Draft-Mitgliedsmenge muss exakt der Resolver-Ausgabe entsprechen.
2. Ein fehlender/fremder/untrusted Client verhindert jede Wirkung.
3. Draft-`analysis_consent`, individuelle Identitätseinwilligung und Owner/Tenant müssen alle erfüllt sein.
4. Keine Rohidentität und kein Ratenarray werden serialisiert.
5. Aktivierter synthetischer Flow verändert definiert die Analyse; deaktivierter Flow bleibt bitgleich.

**Wichtig:** Dieser Gate bleibt zunächst eine direkte serverseitige Python-API, keine neue `/api/scan/*`-Route.

---

### Gate E5.9.4 – Privacy-, Erasure- und Widerrufsgate

**Ziel:** Widerruf oder Löschung eines Mitglieds entzieht sofort die Resolverfähigkeit.

**Dateien:**
- Extend: `core/compliance/runtime_manifest.py`
- Extend: `tests/test_runtime_privacy_manifest.py`
- Create: `tests/test_group_member_consent_revocation.py`

**Tests:**
1. `analysis_consent=False` nach Widerruf → Resolver fail-closed.
2. Gelöschter Client → Resolver fail-closed.
3. Abgelaufene Consent-Version → Resolver fail-closed.
4. Erasure-Summary enthält keine Gruppenmitgliedschaft anderer Personen.
5. Audit enthält nur Aktion/Outcome/Version, keine Gruppenbezeichnung, Mitgliedsliste oder Raten.

---

### Gate E5.9.5 – Freigabeentscheidung vor E5.10

Vor produktiver Scanverdrahtung müssen folgende Punkte explizit bestätigt sein:

| Entscheidung | Empfohlener Wert |
|---|---|
| Resolver-Semantik | `group-member-baseline-v1` |
| Bilder früherer Runs | ausgeschlossen |
| Planet/Profiltemplate früherer Runs | ausgeschlossen |
| Browser-Rohvektoren | verboten |
| Report-/Export-Parsing | verboten |
| Mindestmitglieder | 2 |
| Gruppenstärke | explizit, `[0,1]`, kein versteckter Default |
| Legacy-Clients ohne Owner/Tenant/Consent | fail-closed |
| Gruppen- und Geo-Aktivierung gemeinsam | verboten |
| Default ohne Gruppen-Opt-in | bitgleich |

Erst danach folgt E5.10 als eigener Produktivgate.

---

## 4. Nicht Teil von E5.9

- Keine Änderung von `Phase1ScanRequest`.
- Keine CLI-Flags für Gruppenraten.
- Keine Gruppenwerte in Launcher, Jobs, Reports, Traces oder Manifest-Safe-Ausgaben.
- Keine Geo-Logik.
- Keine automatische Migration bestehender Clienteinwilligungen.
- Keine Behauptung echter Authentifizierung durch den lokalen `OperatorContext`.
- Kein Commit/Push ohne ausdrückliche Freigabe.

---

## 5. Verifikation je Gate

```bash
PYTHONUTF8=1 OPENBLAS_NUM_THREADS=1 /c/morphic_v1/.venv/Scripts/python.exe -m pytest <fokustests> -q
PYTHONUTF8=1 OPENBLAS_NUM_THREADS=1 /c/morphic_v1/.venv/Scripts/python.exe -m pytest tests -q --ignore=tests/test_top5_workflow_smoke.py
PYTHONUTF8=1 OPENBLAS_NUM_THREADS=1 /c/morphic_v1/.venv/Scripts/python.exe -m pytest tests/test_top5_workflow_smoke.py::test_top5_scan_writes_multiplex_exports -q
node --check apps/web/static/app.js
git diff --check
```

Zusätzlich nach E5.9.3: statische Suche, dass Resolver-/Aktivierungstypen weiterhin nicht in Scan-, CLI-, Report-, Job-, Trace- oder Manifest-Ausgabepfade importiert werden.

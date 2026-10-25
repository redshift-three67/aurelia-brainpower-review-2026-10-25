# 🗺️ REMEDY IMPORT ROADMAP

**Letzte Aktualisierung:** 29.11.2025, 11:40 Uhr (nach Tiefenscan & Konsolidierung)

---

## ✅ ABGESCHLOSSEN & KONSOLIDIERT

### Heel (249 Mittel in DB, 81 mit Keywords)
- **Status:** ✅ Importiert + Bereinigt (29.11.2025)
- **Kategorie:** `homotoxikologie_heel` (KORRIGIERT von phytotherapie_heel)
- **Logic Injection:** ✅ 1110 bereinigte Keywords + erweiterte Profil-Keywords
- **Quelle:** `Antihomotoxikologie.pdf`
- **PowerShell-Profil:** Nr. 53 (`heel_remedies`)
- **Besonderheiten:** Kombipräparate, Injeele, Suis-Präparate
- **Integration:** ✅ In Standard-Profilen verfügbar (Schmerz, Leber, etc.)

### Nutramedix (48 Mittel)
- **Status:** ✅ Bereinigt (29.11.2025) - 72 Müll-Einträge gelöscht
- **Kategorie:** `phytotherapie_nutramedix`
- **Logic Injection:** ✅ Bereinigte Keywords + erweiterte Profil-Keywords
- **Quelle:** `NUTRAMEDIX-Kompakt.pdf`
- **PowerShell-Profil:** Nr. 54 (`nutramedix_remedies`)
- **Besonderheiten:** Borreliose-Protokolle, Entgiftung, Immunsystem
- **Integration:** ✅ In Standard-Profilen verfügbar (Entgiftung, Immunsystem, etc.)

---

## 🎯 GEPLANTE IMPORTE

### Priorität 1: Homöopathie-Basis

#### 1. **Klassische Einzelmittel**
- **Umfang:** ~200 Mittel (Arnica, Belladonna, Nux vomica, etc.)
- **Potenzen:** C30, C200, D6, D12, D30
- **Quelle:** Homöopathisches Repertorium / Materia Medica
- **Kategorie:** `homoeopathie_klassisch`
- **Aufwand:** Mittel (strukturierte Daten)

#### 2. **Schüssler-Salze**
- **Umfang:** 27 Mittel (12 Basis + 15 Ergänzung)
- **Potenzen:** D6, D12
- **Quelle:** Schüssler-Literatur
- **Kategorie:** `schuessler_salze`
- **Aufwand:** Gering (klar definiert)

### Priorität 2: Phytotherapie

#### 3. **Pascoe Naturmedizin**
- **Umfang:** ~50-80 Mittel
- **Quelle:** Pascoe-Produktkatalog
- **Kategorie:** `phytotherapie_pascoe`
- **Aufwand:** Mittel (PDF-Extraktion)

#### 4. **Ceres Urtinkturen**
- **Umfang:** ~100 Mittel
- **Quelle:** Ceres-Produktliste
- **Kategorie:** `phytotherapie_ceres`
- **Aufwand:** Mittel (strukturierte Daten)

#### 5. **Weleda**
- **Umfang:** ~80 Mittel
- **Quelle:** Weleda-Katalog
- **Kategorie:** `phytotherapie_weleda`
- **Aufwand:** Mittel (PDF-Extraktion)

### Priorität 3: Spezial-Therapien

#### 6. **Bach-Blüten**
- **Umfang:** 38 Mittel + 1 Rescue
- **Quelle:** Bach-Blüten-Literatur
- **Kategorie:** `bach_blueten`
- **Aufwand:** Gering (klar definiert)

#### 7. **Spagyrik (Phylak)**
- **Umfang:** ~100 Mittel
- **Quelle:** Phylak-Produktliste
- **Kategorie:** `spagyrik_phylak`
- **Aufwand:** Mittel (strukturierte Daten)

#### 8. **Gemmotherapie**
- **Umfang:** ~50 Mittel
- **Quelle:** Gemmotherapie-Literatur
- **Kategorie:** `gemmotherapie`
- **Aufwand:** Mittel (strukturierte Daten)

### Priorität 4: Orthomolekulare Medizin

#### 9. **Vitamine & Mineralien**
- **Umfang:** ~40 Mittel
- **Quelle:** Orthomolekulare Literatur
- **Kategorie:** `orthomolekular_basis`
- **Aufwand:** Gering (strukturierte Daten)

#### 10. **Aminosäuren & Enzyme**
- **Umfang:** ~30 Mittel
- **Quelle:** Orthomolekulare Literatur
- **Kategorie:** `orthomolekular_erweitert`
- **Aufwand:** Mittel (strukturierte Daten)

---

## 🛠️ IMPORT-WORKFLOW (STANDARDISIERT)

### Phase 1: Extraktion
1. PDF/Katalog analysieren
2. Produktnamen extrahieren (Whitelist-basiert)
3. Indikationen/Eigenschaften sammeln
4. JSON generieren (`<hersteller>_import_ready.json`)

### Phase 2: Import
1. AI-Beschreibungen generieren (Ollama)
2. In Datenbank importieren (`add_remedy`)
3. Duplikate vermeiden (`INSERT OR IGNORE`)

### Phase 3: Logic Injection
1. Indikationen als Keywords injizieren
2. Priorität setzen (5 für Index-Begriffe)
3. Intelligente Suche aktivieren

### Phase 4: Validierung
1. Test-Scan durchführen
2. Keyword-Abdeckung prüfen
3. PowerShell-Integration testen

---

## 📊 AKTUELLE STATISTIK (29.11.2025)

| Kategorie | DB-Einträge | Mit Keywords | Status |
|-----------|-------------|--------------|--------|
| **Heel** | 249 | 81 | ✅ Bereinigt |
| **Nutramedix** | 48 | 48 | ✅ Bereinigt |
| **Kohärente Harmonisierungen** | ~1200 | ~1200 | ✅ Bestehend |
| **Homöopathie** | 172 | ? | ⏳ Prüfen |
| **Schüssler** | 137 | ? | ⏳ Prüfen |
| **GESAMT** | **~1700** | **~1500** | |

---

## 🎯 ZIEL-STATISTIK

| Kategorie | Aktuell | Ziel |
|-----------|---------|------|
| **Heel** | 249 | 249 ✅ |
| **Nutramedix** | 48 | 48 ✅ |
| **Homöopathie** | 172 | 200 |
| **Schüssler** | 137 | 137 ✅ |
| **Phytotherapie** | ~300 | 400+ |
| **Bach-Blüten** | 38 | 39 |
| **Orthomolekular** | 0 | 70 |
| **GESAMT** | **~1700** | **~2000** |

---

## 🔧 KONSOLIDIERTER UMSETZUNGSPLAN

### ✅ PHASE 1: TIEFENSCAN & BEREINIGUNG (ABGESCHLOSSEN)
- [x] Nutramedix bereinigt (120 → 48 Einträge)
- [x] Heel-Kategorie korrigiert (`homotoxikologie_heel`)
- [x] Heel-Keywords bereinigt (2754 → 1110)
- [x] PowerShell-Profile 53/54 erstellt
- [x] Registry-Unterstützung implementiert
- [x] Remedy-Service Kategorie-Filter korrigiert

### 🔄 PHASE 2: KEYWORD-ERWEITERUNG (IN ARBEIT)
- [ ] `extend_remedy_keywords.py` ausführen
- [ ] Heel in allen Profilen verfügbar machen
- [ ] Nutramedix in allen Profilen verfügbar machen
- [ ] Integrationstest wiederholen

### ⏳ PHASE 3: WEITERE IMPORTE
1. **Schüssler-Salze prüfen** - bereits 137 in DB, Keywords prüfen
2. **Pascoe Naturmedizin** - ~50-80 Mittel
3. **Ceres Urtinkturen** - ~100 Mittel
4. **Weleda** - ~80 Mittel

### ⏳ PHASE 4: QUALITÄTSSICHERUNG
- [ ] Alle Profile testen
- [ ] HTML-Reports prüfen
- [ ] Synergy-Analyse validieren
- [ ] Dokumentation aktualisieren

---

## 🚀 NÄCHSTER SCHRITT

**SOFORT:** `python tools\extend_remedy_keywords.py` ausführen

**DANACH:** Integrationstest wiederholen mit `python tools\test_remedy_integration.py`

---

**Stand:** 29.11.2025, 11:40 Uhr

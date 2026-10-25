# Z-Anatomy Integration Guide

## Downloads

### 1. Z-Anatomy Blender-Datei (Hauptquelle)
- **URL**: https://github.com/Z-Anatomy/Models-of-human-anatomy
- **Format**: `.blend` (~1.5 GB)
- **Lizenz**: CC BY-SA (basierend auf BodyParts3D)
- **Inhalt**: Komplettes menschliches Anatomie-Modell mit benannten Collections

### 2. Z-Anatomy Sketchfab (Einzelsysteme)
- **URL**: https://sketchfab.com/Z-Anatomy
- **Modelle**: Angiologie, Splanchnologie, Myologie, Neurologie, Arthrologie
- **Format**: GLB/GLTF direkt downloadbar

### 3. BodyParts3D (Original-Datenquelle)
- **Browser**: https://lifesciencedb.jp/bp3d/
- **Bulk-Download**: https://dbarchive.biosciencedbc.jp/en/bodyparts3d/download.html
- **Format**: OBJ/STL sortiert nach FMA-ID

### 4. FMA Ontology (Struktur-IDs)
- **URL**: https://bioportal.bioontology.org/ontologies/FMA
- **104.721 Klassen** mit hierarchischen Relationen

---

## Blender Export-Workflow

```
1. Blender >= 3.6 öffnen
2. Z-Anatomy .blend Datei laden
3. Organ-Collection auswählen (z.B. "Heart")
4. Alle Meshes in der Collection selektieren (A in Outliner)
5. File > Export > glTF 2.0 (.glb)
6. Export-Einstellungen:
   ✅ Include: Selected Objects
   ✅ Mesh: Apply Modifiers
   ✅ Compression: Draco (Level 6)
   ❌ Animation: Deaktiviert
   ❌ Shape Keys: Deaktiviert
7. Benennung: heart_z-anatomy.glb
8. Upload via Modell-Bibliothek im System
```

---

## FMA-ID Zuordnung (Verifiziert)

| Organ | FMA-ID | FMA Name | Z-Anatomy Collection |
|-------|--------|----------|---------------------|
| Herz | FMA_7088 | Heart | Heart |
| Gehirn | FMA_50801 | Brain | Brain |
| Leber | FMA_7197 | Liver | Liver |
| Niere | FMA_7203 | Kidney | Kidney |
| Lunge | FMA_7195 | Lung | Lung |
| Wirbelsäule | FMA_11966 | Vertebral column | Vertebral column |
| Ganzkörper | FMA_20394 | Body proper | Body |
| Haut (TCM) | FMA_24728 | Skin | Integument |

### Sub-Strukturen (Beispiel Herz)

| Region | FMA-ID | FMA Name |
|--------|--------|----------|
| Apex | FMA_7170 | Apex of heart |
| Basis | FMA_7163 | Base of heart |
| Linker Ventrikel | FMA_7101 | Left ventricle |
| Rechter Ventrikel | FMA_7098 | Right ventricle |
| Linker Vorhof | FMA_7097 | Left atrium |
| Rechter Vorhof | FMA_7096 | Right atrium |
| Septum | FMA_7133 | Interventricular septum |

---

## Quellen für erweiterte Pilot-Daten

### Hochauflösende Anatomie
| Quelle | URL | Besonderheit |
|--------|-----|-------------|
| Allen Human Brain Atlas | https://human.brain-map.org/ | 3D-Koordinaten + Genexpression |
| Visible Human Project | https://www.nlm.nih.gov/databases/download/vhp.html | Cryosection mit CT/MRT |
| IT'IS Virtual Population | https://itis.swiss/virtual-population/ | >300 Gewebetypen + dielektrische Daten |
| Open Anatomy Project | https://www.openanatomy.org/ | Kuratierte Atlanten |

### Akupunktur / TCM Daten
| Quelle | URL | Besonderheit |
|--------|-----|-------------|
| WHO Standard Acupuncture Points | WHO-Publikation | 361 standardisierte Punkte |
| AcuMap (Open Source) | GitHub diverse | 3D-Koordinaten der Meridianpunkte |
| Korean Acupuncture Atlas | KIOM | Hochauflösendes 3D-Mapping |

### NLS / Bioresonanz Referenz
| Quelle | Beschreibung |
|--------|-------------|
| BodyParts3D FMA-Browser | Sub-Organ-Ebene bis Gewebetyp, ideal für S-Punkt-Generierung |
| FMA Part-Of Hierarchie | Automatische Ableitung von Scan-Regionen aus Ontologie |

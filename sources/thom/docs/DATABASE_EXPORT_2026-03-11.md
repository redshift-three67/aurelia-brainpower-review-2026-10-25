# Datenbank-Export — Stand 2026-03-11

## Übersicht

| Tabelle | Datensätze |
|---|---|
| clients | 5 |
| client_vectors | 27 |
| client_groups | 1 |
| client_group_members | 0 |
| treatment_sessions | 8 |
| chreode_trajectories | 5 |
| harmonization_jobs | 1 |
| harmonization_protocols | 0 |
| resonance_results | 0 |
| organ_schemas | 8 |
| organ_landmarks | 268 |
| organ_scan_points | 162 |
| anatomy_models | 13 |
| anatomy_resonance_points | 10 |
| remedies | 100 |
| word_energies | 10 |
| word_energy_collections | 1 |

---

## 1. clients (5 Datensätze)

```json
[
  {
    "id": "a864bfa7-4651-4f71-85d9-635c69184e12",
    "first_name": "Hubert",
    "last_name": "Mayer",
    "birth_date": "1967-04-09",
    "birth_place": "Augsburg",
    "field_signature": "FS-02AFF235",
    "photo_url": null,
    "notes": "",
    "user_id": null,
    "created_at": "2025-12-30T23:16:24.188726+00"
  },
  {
    "id": "50cc0718-2f0b-4516-a7d9-f1acb818c078",
    "first_name": "K",
    "last_name": "Deisenhofer",
    "birth_date": "1966-03-09",
    "birth_place": "Augsburg",
    "field_signature": "FS-4279B4E9",
    "photo_url": null,
    "notes": "",
    "user_id": null,
    "created_at": "2025-12-31T07:33:39.256938+00"
  },
  {
    "id": "8c244adb-bfe8-474c-8d35-bad2537b7272",
    "first_name": "Hannelore",
    "last_name": "Knott",
    "birth_date": "1940-04-23",
    "birth_place": "Augsburg",
    "field_signature": "FS-4077DAAD",
    "photo_url": "https://yoryyvfuscyfumeseour.supabase.co/storage/v1/object/public/client-photos/8c244adb-bfe8-474c-8d35-bad2537b7272/1767234921329.jpg",
    "notes": "",
    "user_id": null,
    "created_at": "2026-01-01T02:35:19.563129+00"
  },
  {
    "id": "15865547-9ed4-4f22-8011-3e212b723abf",
    "first_name": "Joachim",
    "last_name": "Schneider",
    "birth_date": "1959-04-22",
    "birth_place": "Thierhaupten",
    "field_signature": "FS-74FE34DD",
    "photo_url": null,
    "notes": "",
    "user_id": null,
    "created_at": "2026-01-26T15:38:06.9077+00"
  },
  {
    "id": "49fd92e8-468d-4f64-860d-26bfc08849f2",
    "first_name": "Klaus",
    "last_name": "Deisenhofer",
    "birth_date": "1966-04-09",
    "birth_place": "Augsburg",
    "field_signature": "FS-78985FCB",
    "photo_url": "https://yoryyvfuscyfumeseour.supabase.co/storage/v1/object/public/client-photos/49fd92e8-468d-4f64-860d-26bfc08849f2/1772801222179.jpg",
    "notes": "",
    "user_id": "6685651c-fcd7-445b-9b5c-d609fdb4fb0b",
    "created_at": "2026-03-05T11:53:27.377493+00"
  }
]
```

---

## 2. client_vectors (27 Datensätze — Auszug der wichtigsten)

```json
[
  {
    "id": "9ec654d8-a2dc-435c-a78e-79e929870a50",
    "client_id": "a864bfa7-...-635c69184e12",
    "dimension_physical": -0.2818,
    "dimension_emotional": -0.1364,
    "dimension_mental": -0.1272,
    "dimension_energy": 0.2969,
    "dimension_stress": -0.1296,
    "attractor_distance": 0.7659,
    "phase": "stable",
    "primary_concern": "Zentrales Nervensystem",
    "session_id": "session-1767136646910",
    "input_method": "manual",
    "created_at": "2025-12-30T23:17:24.787247+00"
  },
  {
    "id": "1cbbc72b-148f-4dde-b1d7-628f5bb40e14",
    "client_id": "50cc0718-...-f1acb818c078",
    "dimension_physical": -0.6789,
    "dimension_emotional": -0.6094,
    "dimension_mental": -0.4081,
    "dimension_energy": 0.2229,
    "dimension_stress": 0.0544,
    "attractor_distance": 0.4873,
    "phase": "transition",
    "primary_concern": "Medulla Oblongata",
    "session_id": "session-1767199142423",
    "created_at": "2025-12-31T16:39:01.121213+00"
  }
]
```

*Vollständige 27 Vektoren für 3 Klienten (Hubert Mayer: 1, K Deisenhofer: 18, Klaus Deisenhofer: 8)*

---

## 3. treatment_sessions (8 Datensätze)

Alle 8 Sitzungen gehören zu Klaus Deisenhofer (49fd92e8-...).

```json
[
  {
    "id": "95260c54-...",
    "client_id": "49fd92e8-...",
    "session_number": 1,
    "session_date": "2026-03-06T12:01:11.673875+00",
    "status": "active",
    "vector_snapshot": {
      "dimensions": [-0.551, 0.117, -0.133, 0.271, -0.336],
      "phase": "transition",
      "stability": 0.639,
      "bifurcationRisk": 0.245
    }
  },
  {
    "id": "37ed96cf-...",
    "session_number": 2,
    "status": "active",
    "vector_snapshot": {
      "dimensions": [-0.203, 0.172, 0.006, 0.369, -0.142],
      "phase": "stable",
      "stability": 0.762,
      "bifurcationRisk": 0.089
    }
  },
  {
    "id": "60568504-...",
    "session_number": 8,
    "session_date": "2026-03-11T07:42:53.146939+00",
    "status": "active",
    "vector_snapshot": {
      "dimensions": [-0.244, -0.360, 0.030, 0.415, -0.143],
      "phase": "transition",
      "stability": 0.691,
      "bifurcationRisk": 0.084
    }
  }
]
```

---

## 4. chreode_trajectories (5 Datensätze)

```json
[
  {
    "id": "96184cf8-...",
    "client_id": "49fd92e8-...",
    "session_id": "1d210e96-...",
    "dimensions": [-0.285, 0.158, -0.239, 0.480, -0.108],
    "phase": "transition",
    "stability": 0.682,
    "bifurcation_risk": 0.056,
    "chreode_alignment": 0.423,
    "attractor_distance": 0.637,
    "created_at": "2026-03-06T23:28:04.34417+00"
  },
  {
    "id": "8ab22ee9-...",
    "dimensions": [-0.774, -0.443, -0.496, 0.072, -0.256],
    "phase": "transition",
    "stability": 0.473,
    "bifurcation_risk": 0.237,
    "chreode_alignment": 0.294,
    "created_at": "2026-03-07T19:09:50.401224+00"
  },
  {
    "id": "19849792-...",
    "dimensions": [-0.244, -0.360, 0.030, 0.415, -0.143],
    "phase": "transition",
    "stability": 0.691,
    "bifurcation_risk": 0.084,
    "chreode_alignment": 0.429,
    "created_at": "2026-03-11T07:42:53.353373+00"
  }
]
```

---

## 5. harmonization_jobs (1 Datensatz)

```json
{
  "id": "cfc315e5-...",
  "client_id": "49fd92e8-...",
  "job_type": "meridian_sequence",
  "status": "completed",
  "progress": 100,
  "result_data": {
    "meridianIds": ["HT", "SI", "PC", "TE", "LU", "DU", "YANGQIAO", "YANGWEI", "nls-thyroid", "nls-lymph", "nls-spleen", "nls-heart", "nls-pancreas", "nls-liver"],
    "pattern": "Fire-Stagnation, Qi bewegen",
    "pointCount": 49,
    "totalDuration": 3005,
    "points": [
      {"id": "HT1", "frequency": 341.3, "meridianId": "HT"},
      {"id": "HT2", "frequency": 349.9, "meridianId": "HT"},
      {"id": "SI1", "frequency": 343.5, "meridianId": "SI"},
      {"id": "DU-opening", "frequency": 136.1, "meridianId": "DU"},
      {"id": "nls-...", "frequency": 9.2, "meridianId": "nls-thyroid"}
    ]
  },
  "target_frequencies": [341.3, 349.9, 358.4, 367, 375.5, 384.1, 392.6, 343.5, 350.4, 357.3, 364.2, 371.1, 378, 384.9, 432, 408, 460.8, 136.1, 152.8, 164.2, 9.2, 9.45, 7.65, 5.6, 6.82, 1.5, 1.55, 7.3, 1.75, 7.25, 7.5, 3, 9.1, 1.9, 6.48],
  "created_at": "2026-03-06T13:20:51.062065+00"
}
```

---

## 6. client_groups (1 Datensatz)

```json
{
  "id": "d1a5ce22-ff04-4cbc-b91f-ddbdb7da1083",
  "name": "Klaus",
  "description": null,
  "color": "#6366f1",
  "user_id": "6685651c-fcd7-445b-9b5c-d609fdb4fb0b",
  "created_at": "2026-03-08T12:41:29.699713+00"
}
```

---

## 7. organ_schemas (8 Datensätze)

```json
[
  {
    "organ_code": "BRAIN",
    "organ_name": "Brain",
    "source_concept_id": "FMA_50801",
    "coordinate_system": "RAS",
    "regions": [
      {"region_code": "LFRONT", "name": "Left Frontal Lobe"},
      {"region_code": "RFRONT", "name": "Right Frontal Lobe"},
      {"region_code": "LPARI", "name": "Left Parietal Lobe"},
      {"region_code": "RPARI", "name": "Right Parietal Lobe"},
      {"region_code": "LTEMP", "name": "Left Temporal Lobe"},
      {"region_code": "RTEMP", "name": "Right Temporal Lobe"},
      {"region_code": "LOCC", "name": "Left Occipital Lobe"},
      {"region_code": "ROCC", "name": "Right Occipital Lobe"},
      {"region_code": "LCEREB", "name": "Left Cerebellum"},
      {"region_code": "RCEREB", "name": "Right Cerebellum"},
      {"region_code": "BRAINSTEM", "name": "Brainstem"},
      {"region_code": "MIDLINE", "name": "Midline"}
    ],
    "sampling_config": {
      "method": "region_geodesic_fps",
      "min_surface_distance_mm": 6,
      "target_points_per_region": {"BRAINSTEM": 3, "LCEREB": 4, "LFRONT": 4, "RFRONT": 4}
    }
  },
  {
    "organ_code": "HEART",
    "organ_name": "Heart",
    "source_concept_id": "FMA_7088",
    "regions": [
      {"region_code": "APEX", "name": "Apex cordis"},
      {"region_code": "BASE", "name": "Basis cordis"},
      {"region_code": "LV", "name": "Left Ventricle"},
      {"region_code": "RV", "name": "Right Ventricle"},
      {"region_code": "LA", "name": "Left Atrium"},
      {"region_code": "RA", "name": "Right Atrium"},
      {"region_code": "SEPT", "name": "Septum"}
    ]
  },
  {
    "organ_code": "KIDNEY_PAIR",
    "source_concept_id": "FMA_7203"
  },
  {
    "organ_code": "LIVER",
    "source_concept_id": "FMA_7197"
  },
  {
    "organ_code": "LUNG_PAIR",
    "source_concept_id": "FMA_7195"
  },
  {
    "organ_code": "SPINE_PELVIS",
    "source_concept_id": "FMA_11966"
  },
  {
    "organ_code": "TCM_SURFACE",
    "source_concept_id": null
  },
  {
    "organ_code": "WHOLEBODY",
    "source_concept_id": null
  }
]
```

---

## 8. anatomy_models (13 Datensätze)

```json
[
  {
    "name": "Standard Ganzkörper",
    "source": "custom",
    "category": "full_body",
    "file_path": "/models/human-body.glb",
    "storage_type": "local",
    "is_default": true,
    "gender": "neutral",
    "supports_meridian_mapping": true,
    "visible_layers": ["meridians", "chakras", "resonance_points", "nls_scan"]
  },
  {
    "name": "Z-Anatomy Vollkörper (männlich)",
    "source": "z-anatomy",
    "category": "full_body",
    "file_path": "3d-models/z-anatomy-male-full.glb",
    "storage_type": "cloud",
    "gender": "male",
    "supports_organ_layers": true
  },
  {
    "name": "Z-Anatomy Vollkörper (weiblich)",
    "source": "z-anatomy",
    "category": "full_body",
    "file_path": "3d-models/z-anatomy-female-full.glb",
    "storage_type": "cloud",
    "gender": "female"
  },
  {
    "name": "BodyParts3D Herz",
    "source": "bodyparts3d",
    "category": "organ",
    "file_path": "3d-models/bodyparts3d-heart.glb",
    "applicable_organ_systems": ["heart"],
    "visible_layers": ["nls_scan"]
  },
  {
    "name": "BodyParts3D Gehirn",
    "source": "bodyparts3d",
    "category": "organ",
    "file_path": "3d-models/bodyparts3d-brain.glb",
    "applicable_organ_systems": ["brain"],
    "visible_layers": ["nls_scan"]
  },
  {"name": "BodyParts3D Leber", "applicable_organ_systems": ["liver"]},
  {"name": "BodyParts3D Niere", "applicable_organ_systems": ["kidney"]},
  {"name": "BodyParts3D Lunge", "applicable_organ_systems": ["lung"]},
  {"name": "BodyParts3D Wirbelsäule", "applicable_organ_systems": ["spine"]},
  {"name": "BodyParts3D Becken", "applicable_organ_systems": ["pelvis"]},
  {"name": "BodyParts3D Magen-Darm", "applicable_organ_systems": ["gi_tract"]},
  {"name": "BodyParts3D Schädel", "applicable_organ_systems": ["skull"]},
  {"name": "BodyParts3D Skelett", "applicable_organ_systems": ["skeleton"]}
]
```

---

## 9. anatomy_resonance_points (10 Datensätze)

```json
[
  {"name": "Herz", "name_latin": "Cor", "body_region": "thorax", "primary_frequency": 528, "harmonic_frequencies": [396, 639, 741], "x": 0, "y": 0.6, "z": 0.1, "meridian_associations": ["heart", "small_intestine"]},
  {"name": "Leber", "name_latin": "Hepar", "body_region": "abdomen", "primary_frequency": 317.83, "harmonic_frequencies": [174, 285], "x": 0.15, "y": 0.45, "z": 0.05, "meridian_associations": ["liver", "gallbladder"]},
  {"name": "Niere Links", "name_latin": "Ren sinister", "body_region": "retroperitoneum", "primary_frequency": 319.88, "x": -0.1, "y": 0.4, "z": -0.1},
  {"name": "Niere Rechts", "name_latin": "Ren dexter", "primary_frequency": 319.88, "x": 0.1, "y": 0.38, "z": -0.1},
  {"name": "Lunge Links", "name_latin": "Pulmo sinister", "primary_frequency": 220, "x": -0.12, "y": 0.65, "z": 0},
  {"name": "Lunge Rechts", "name_latin": "Pulmo dexter", "primary_frequency": 220, "x": 0.12, "y": 0.65, "z": 0},
  {"name": "Magen", "name_latin": "Gaster", "primary_frequency": 110, "x": -0.05, "y": 0.5, "z": 0.08},
  {"name": "Gehirn", "name_latin": "Cerebrum", "primary_frequency": 40, "harmonic_frequencies": [7.83, 14, 21], "x": 0, "y": 0.9, "z": 0},
  {"name": "Thymus", "name_latin": "Thymus", "primary_frequency": 639, "x": 0, "y": 0.7, "z": 0.05},
  {"name": "Schilddrüse", "name_latin": "Glandula thyroidea", "primary_frequency": 741, "x": 0, "y": 0.8, "z": 0.05}
]
```

---

## 10. word_energies (10 Datensätze)

```json
[
  {"word": "Angst", "frequency": 20, "category": "negative", "chakra": "root", "organ_system": "adrenal", "emotional_quality": "fear"},
  {"word": "Stress", "frequency": 25, "category": "negative", "chakra": "solar_plexus", "organ_system": "nervous_system", "emotional_quality": "tension"},
  {"word": "Trauer", "frequency": 15, "category": "negative", "chakra": "heart", "organ_system": "lungs", "emotional_quality": "grief"},
  {"word": "Wut", "frequency": 35, "category": "negative", "chakra": "solar_plexus", "organ_system": "liver", "emotional_quality": "anger"},
  {"word": "Freude", "frequency": 396, "category": "positive", "chakra": "sacral", "organ_system": "sacral", "emotional_quality": "joy"},
  {"word": "Frieden", "frequency": 639, "category": "positive", "chakra": "heart", "organ_system": "thymus", "emotional_quality": "peace"},
  {"word": "Gesundheit", "frequency": 852, "category": "positive", "chakra": "third_eye", "organ_system": "pineal", "emotional_quality": "clarity"},
  {"word": "Harmonie", "frequency": 741, "category": "positive", "chakra": "throat", "organ_system": "thyroid", "emotional_quality": "balance"},
  {"word": "Kraft", "frequency": 174, "category": "positive", "chakra": "root", "organ_system": "adrenal", "emotional_quality": "strength"},
  {"word": "Liebe", "frequency": 528, "category": "positive", "chakra": "heart", "organ_system": "heart", "emotional_quality": "love"}
]
```

---

## 11. word_energy_collections (1 Datensatz)

```json
{
  "id": "f567090f-...",
  "name": "Meridiane",
  "words": ["Kohärente Harmonsierung Meridiane", "Entlade Fremdenergien, Gelübde, Verfluchungen und Verwünschungen"],
  "user_id": "6685651c-fcd7-445b-9b5c-d609fdb4fb0b"
}
```

---

## 12. remedies (100 Datensätze — Zusammenfassung)

### Bachblüten (38 Stück)
| Name | Frequenz | Element | Meridiane | Emotionales Muster |
|---|---|---|---|---|
| Agrimony | 35.2 | Metall | LU, LI | Verbergen innerer Qualen |
| Aspen | 42.8 | Wasser | KI, BL | Unbestimmte Ängste |
| Beech | 38.5 | Holz | LR, GB | Intoleranz und Kritiksucht |
| Centaury | 31.7 | Erde | SP, ST | Willensschwäche |
| Cerato | 44.1 | Feuer | HT, SI | Mangelndes Selbstvertrauen |
| Cherry Plum | 48.3 | Holz | LR, GB | Angst vor Kontrollverlust |
| ... | | | | |
| Willow | 33.1 | Holz | LR, GB | Selbstmitleid und Groll |

### Schüßler-Salze (12 Stück)
| Name | Frequenz | Element | Meridiane |
|---|---|---|---|
| Nr. 1 Calcium fluoratum | 22.3 | Wasser | KI, BL |
| Nr. 2 Calcium phosphoricum | 24.5 | Erde | SP, ST |
| ... | | | |
| Nr. 12 Calcium sulfuricum | 30.8 | Metall | LU, LI |

### Homöopathie (50 Stück)
| Name | Frequenz | Element | Meridiane | Potenz |
|---|---|---|---|---|
| Aconitum napellus | 45.2 | Wasser | KI, BL | C30 |
| Arnica montana | 38.7 | Feuer | HT, SI | C30 |
| Belladonna | 52.3 | Feuer | HT, SI | C30 |
| ... | | | | |

---

## 13. organ_scan_points (162 Datensätze — Organsystem-Übersicht)

| Organ-System | Punkte | Beispiel-Punkt | Frequenz |
|---|---|---|---|
| adrenal | 6 | NNR Zona glomerulosa | 3.8 Hz |
| brain | 8 | Frontallappen | 8.0 Hz |
| cardiovascular | 9 | Aortenbogen | 1.3 Hz |
| digestive | 15 | Speiseröhre | 4.2 Hz |
| ear | 6 | Äußerer Gehörgang | 11.0 Hz |
| eye | 8 | Netzhaut | 10.5 Hz |
| heart | 6 | Rechter Vorhof | 1.5 Hz |
| kidney | 8 | Nierenrinde | 2.8 Hz |
| liver | 8 | Rechter Leberlappen | 3.0 Hz |
| lung | 6 | Oberlappen rechts | 2.2 Hz |
| lymph | 10 | Thymus | 6.5 Hz |
| pancreas | 6 | Pankreaskopf | 7.0 Hz |
| reproductive | 8 | Prostata/Uterus | 4.5 Hz |
| spleen | 4 | Milzkapsel | 5.5 Hz |
| spine | 26 | C1 Atlas | 12.0 Hz |
| stomach | 6 | Magenfundus | 3.5 Hz |
| thyroid | 8 | Schilddrüse re. Lappen | 9.0 Hz |
| urinary | 8 | Nierenbecken | 5.0 Hz |

---

## 14. organ_landmarks (268 Datensätze — Verteilung)

| Organ | A-Punkte | S-Punkte | Gesamt |
|---|---|---|---|
| BRAIN | 8 | 44 | 52 |
| HEART | 9 | 36 | 45 |
| KIDNEY_PAIR | 6 | 18 | 24 |
| LIVER | 6 | 18 | 24 |
| LUNG_PAIR | 6 | 22 | 28 |
| SPINE_PELVIS | 8 | 23 | 31 |
| TCM_SURFACE | 4 | 25 | 29 |
| WHOLEBODY | 10 | 25 | 35 |

### Beispiel-Landmarks (BRAIN)
```json
[
  {"point_id": "BRAIN_A_001", "label": "Left frontal pole", "point_class": "A", "region_code": "LFRONT", "x": 32, "y": 82, "z": 18, "scan_frequency": 40, "structure_concept_id": "FMA_74886", "mirror_pair": "BRAIN_A_002", "confidence": 1.0},
  {"point_id": "BRAIN_A_002", "label": "Right frontal pole", "point_class": "A", "region_code": "RFRONT", "x": -32, "y": 82, "z": 18, "mirror_pair": "BRAIN_A_001", "confidence": 1.0},
  {"point_id": "BRAIN_S_001", "label": "L frontal superior", "point_class": "S", "region_code": "LFRONT", "x": 28, "y": 70, "z": 30, "scan_frequency": 38, "placement_method": "generated_fps", "confidence": 0.8}
]
```

---

*Export-Datum: 2026-03-11T07:49:00+00 | Quell-Projekt: 7d414a8e-f393-427d-962d-848204bdd57c*

# Profil-Übersicht & NLS-Datenstruktur

Diese Dokumentation bietet einen detaillierten Überblick über alle verfügbaren Analyse-Profile, die zugrundeliegenden NLS-Datenstrukturen und Empfehlungen zur Erweiterung des Systems.

---

## 1. Übersicht der Analyse-Profile

Profile definieren, welche Item-Gruppen für einen Scan herangezogen werden.

### A. Standard-Profile (Basis)

| Profil | Beschreibung | Enthaltene Hauptgruppen | Anwendungsfall |
| :--- | :--- | :--- | :--- |
| **full** (Standard) | Ganzheitlicher Scan über alle Ebenen | *Alle verfügbaren Gruppen* (Pathogen, Toxin, Regulation, Psyche, Meridiane, etc.) | Erstanamnese, Komplett-Check |
| **pathogen** | Fokus auf Infektionen | `bakterien`, `viren`, `parasiten`, `pilze` (jeweils inkl. `_fein` & `_detailliert`) | Verdacht auf akute/chronische Infektionen |
| **toxin** | Umweltbelastungen & Gifte | `schwermetalle`, `chemikalien`, `strahlung_tox`, `wohnraumgifte` | Entgiftungs-Therapie, Umweltmedizin |
| **regulation** | Funktionelle Balance | `chakren`, `meridiane`, `entgiftung_organe`, `hormone`, `nervensystem` | Regulationsmedizin, Energiearbeit |
| **meridiane_detailliert** | Tiefe TCM-Analyse | `meridiane` (Haupt), `meridiane_detailliert_fein` (Akupunkturpunkte) | Akupunktur, TCM-Diagnostik |
| **psychosomatik** | Mentale & Emotionale Felder | `bachblueten`, `psyche_remedies`, `emotionen`, `glaubenssaetze` (geplant) | Psychosomatische Begleitung |

### B. Spezial-Profile (Registry V1)

Diese Profile sind modular in `apps/cli/profiles/registry.py` definiert und bieten maximale Detailtiefe für Fachbereiche.

| Profil | Fokus | Detail-Gruppen (Auszug) |
| :--- | :--- | :--- |
| **gehirn_detailliert** | Neurologie & ZNS | `nervensystem_zns`, `hirnnerven`, `neurotransmitter`, `schwindel_*`, `schmerz_kopf`, `schlafstoerungen` |
| **immunsystem_detailliert** | Immunologie | `immunsystem_angeboren/_erworben`, `autoimmun`, `zytokine`, `entzuendung`, `mikronaehrstoffe` |
| **lymphsystem_detailliert** | Entgiftung & Drainage | `entgiftung_leber` (Phasen 1-3), `lymphe`, `niere`, `darm`, `haut`, `toxine_remedies` |

---

## 2. NLS Datenstruktur (Datenbasis)

Die Engine greift auf CSV-Dateien in `core/subgroups/` zurück. Jede Gruppe entspricht einer Datei oder einem Abschnitt.

| Kategorie | Untergruppen (Dateinamen-Muster) | Inhaltstyp | Detailgrad |
| :--- | :--- | :--- | :--- |
| **Anatomie** | `wirbelsaeule_*.csv`, `nervensystem_*.csv` | Organe, Segmente | Physisch |
| **Pathogene** | `bakterien.csv`, `viren.csv`, `parasiten.csv` | Erreger-Namen | Spezifisch (Gattung/Art) |
| **Toxine** | `schwermetalle.csv`, `chemikalien.csv` | Substanzen | Chemisch |
| **Regulation** | `chakren.csv`, `meridiane.csv` | Energiezentren | Energetisch |
| **Remedies** | `homoeopathie_*.csv`, `spagyrik.csv`, `orthomolekular.csv` | Mittel, Potenzen | Therapeutisch |

**Struktur der Einträge:**
- `label`: Name des Items (z.B. "Borrelia burgdorferi")
- `rates`: Radionische Raten (z.B. `[123.4, 567.8]`)
- `group`: Zugehörigkeit (z.B. `bakterien`)
- `description` (Optional): Erklärungstext

---

## 3. Multiplex-Strukturen

Der "Multiplex-Scan" kombiniert verschiedene Analyse-Ebenen:

1.  **Basis-Scan**: Scannt alle Items des Profils gegen das h-Level (Entropie).
2.  **Sub-Analyse**: Erzeugt für Top-Treffer "Feldtest-Kandidaten" (dynamische Untergruppen).
3.  **Resonanz-Ebenen**: Berechnet Copen-Raten (Potenzen) und 13-Ebenen-Resonanz (Physisch bis Spirituell).
4.  **Quantum Synergy**: Sucht Kreuzverbindungen (z.B. "Leberbelastung + Wut + Schwermetall").
5.  **3D-Mapping**: Verortet Treffer im virtuellen Raum (via `core/nls3d_points_new.py`).

---

## 4. Empfehlungen zur Erweiterung

Um die Akkuranz und den Nutzen weiter zu steigern, empfehlen wir folgende Erweiterungen:

| Bereich | Maßnahme | Priorität | Aufwand |
| :--- | :--- | :--- | :--- |
| **Zahnmedizin** | Neues Profil **`zahn_matrix`**: Verknüpfung von Odontonen (Zähnen) mit Organen und Emotionen. | Hoch | Mittel |
| **Systemik** | Neues Profil **`systemik`**: Familienstrukturen, Ahnenfelder, systemische Glaubenssätze. | Mittel | Gering |
| **3D-Modell** | **Organ-Visualisierung**: Integration eines transparenten 3D-Körpermodells in den Viewer als Referenz. | Hoch | Mittel |
| **Hardware** | **TrueRNG Support**: Einbindung von USB-Rauschgeneratoren für "echten" Quantenzufall. | Sehr Hoch | Gering |
| **Biofeedback** | **GSR/HRV**: Echtzeit-Stressmessung zur Steuerung der Scan-Tiefe (Wiederholung bei Stress). | Mittel | Hoch |
| **Datenbank** | **Veterinär-Modus**: Eigene Listen für Hunde/Katzen/Pferde (Anatomie abweichend). | Niedrig | Hoch |

---

*Stand: 26.11.2025 – Generiert durch Radialgo2 AI Assistant*

from __future__ import annotations

import hashlib
import math
import logging
from pathlib import Path
from typing import List, Dict

import json
import re
import numpy as np

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")

# Import erweiterte Gruppen-Definitionen
try:
    from . import groups_extended as gext
    GROUPS_EXTENDED_AVAILABLE = True
except ImportError as exc:
    GROUPS_EXTENDED_AVAILABLE = False
    gext = None
    logger.warning("groups_extended konnte nicht geladen werden: %s", exc)

try:
    from . import groups_extended_v2 as gext2
    GROUPS_EXTENDED_V2_AVAILABLE = True
except ImportError as exc:
    GROUPS_EXTENDED_V2_AVAILABLE = False
    gext2 = None
    logger.warning("groups_extended_v2 konnte nicht geladen werden: %s", exc)

# Phase 4 Gruppen (44 neue FEIN und MULTIPLEX Gruppen)
try:
    from . import groups_phase4_corrected as gp4_1
    from . import groups_phase4_priority2 as gp4_2
    from . import groups_phase4_priority3 as gp4_3
    GROUPS_PHASE4_AVAILABLE = True
except ImportError as exc:
    GROUPS_PHASE4_AVAILABLE = False
    gp4_1 = None
    gp4_2 = None
    gp4_3 = None
    logger.warning("groups_phase4 Module konnten nicht geladen werden: %s", exc)

# Phase 5 Gruppen (30 neue FEIN und MULTIPLEX Gruppen - Lücken-Schließung)
try:
    from . import groups_phase5_priority1 as gp5_1
    from . import groups_phase5_priority2 as gp5_2
    from . import groups_phase5_priority3_4 as gp5_3
    from . import groups_phase5_priority5 as gp5_5
    GROUPS_PHASE5_AVAILABLE = True
except ImportError as exc:
    GROUPS_PHASE5_AVAILABLE = False
    gp5_1 = None
    gp5_2 = None
    gp5_3 = None
    gp5_5 = None
    logger.warning("groups_phase5 Module konnten nicht geladen werden: %s", exc)

SCHUMANN_F0 = 7.83
PHI = (1.0 + 5.0 ** 0.5) / 2.0

_GROUP_DATA_DIR = Path(__file__).resolve().parent / "data" / "groups"
_MEDICA_JSON_PATH = Path(__file__).resolve().parents[2] / "listen" / "Medica.json"
_TCM_TXT_PATH = Path(__file__).resolve().parents[2] / "listen" / "tcm.txt"
_HOMEOPATHY_POTENCIES = ["D0", "D6", "D12", "D30", "C30", "C200", "M", "LM1", "LM2"]


def _u01(seed: str) -> float:
    h = hashlib.sha256(seed.encode("utf-8")).digest()
    return int.from_bytes(h[:8], "big") / (2 ** 64)


def _rate_from_freq(f: float) -> float:
    f = max(f, 1e-9)
    return float((math.log10(f / SCHUMANN_F0) * 100.0) % 100.0)


def _musical_rate(n: int) -> float:
    f = SCHUMANN_F0 * (2.0 ** (n / 12.0))
    return _rate_from_freq(f)


def _phi_rate(m: int) -> float:
    f = SCHUMANN_F0 * (PHI ** m)
    return _rate_from_freq(f)


def _load_group_labels_from_file(group: str) -> List[str] | None:
    txt_path = _GROUP_DATA_DIR / f"{group}.txt"
    json_path = _GROUP_DATA_DIR / f"{group}.json"

    if txt_path.exists():
        try:
            text = txt_path.read_text(encoding="utf-8")
        except Exception:
            return None
        labels: List[str] = []
        for line in text.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "|" in line:
                label = line.split("|", 1)[0].strip()
            else:
                label = line
            if label:
                labels.append(label)
        if not labels:
            return None
        return labels

    if json_path.exists():
        try:
            raw = json_path.read_text(encoding="utf-8")
            data = json.loads(raw)
        except Exception:
            return None

        labels_json: List[str] = []

        def _extract_from_seq(seq: list[object]) -> None:
            for item in seq:
                if isinstance(item, str):
                    label = item.strip()
                    if label:
                        labels_json.append(label)
                elif isinstance(item, dict):
                    name = item.get("label") or item.get("name")
                    if isinstance(name, str):
                        label = name.strip()
                        if label:
                            labels_json.append(label)

        if isinstance(data, list):
            _extract_from_seq(data)
        elif isinstance(data, dict):
            seq = data.get("labels")
            if isinstance(seq, list):
                _extract_from_seq(seq)

        if not labels_json:
            return None
        return labels_json

    return None


def _load_remedy_labels_from_db(category: str) -> List[str] | None:
    """Lädt Remedy-Labels aus der SQLite-Datenbank für eine bestimmte Kategorie."""
    try:
        import sqlite3
        db_path = Path(__file__).resolve().parents[2] / "data" / "remedies.db"
        if not db_path.exists():
            return None
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name FROM remedies 
            WHERE category = ? 
            ORDER BY name
        """, (category,))
        labels = [row[0] for row in cursor.fetchall()]
        conn.close()
        return labels if labels else None
    except Exception as e:
        logger.warning(f"Konnte Remedy-Labels nicht aus DB laden: {e}")
        return None


def _load_remedy_labels_from_medica() -> List[str] | None:
    try:
        if not _MEDICA_JSON_PATH.exists():
            return None
        raw = _MEDICA_JSON_PATH.read_text(encoding="utf-8")
        data = json.loads(raw)
    except Exception:
        return None

    clinical = data.get("clinicalSymptoms")
    if not isinstance(clinical, list):
        return None

    remedies: set[str] = set()
    for entry in clinical:
        if not isinstance(entry, dict):
            continue
        rem_list = entry.get("remedies")
        if not isinstance(rem_list, list):
            continue
        for name in rem_list:
            if isinstance(name, str):
                label = name.strip()
                if label:
                    remedies.add(label)

    if not remedies:
        return None
    return sorted(remedies)


def _load_tcm_formulas() -> List[Dict[str, str]] | None:
    try:
        if not _TCM_TXT_PATH.exists():
            return None
        try:
            text = _TCM_TXT_PATH.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            text = _TCM_TXT_PATH.read_text(encoding="latin-1")
    except Exception:
        return None

    formulas: List[Dict[str, str]] = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        # Remove leading index
        first_space = line.find(" ")
        if first_space <= 0:
            continue
        rest = line[first_space + 1 :].strip()
        # Remove trailing numeric code (external rate), we generate our own rates
        parts = rest.rsplit(" ", 1)
        if len(parts) == 2 and parts[1].isdigit():
            rest = parts[0].rstrip()
        # Split name and description by two or more spaces
        name_desc = re.split(r"\s{2,}", rest, maxsplit=1)
        if not name_desc:
            continue
        name = name_desc[0].strip()
        description = name_desc[1].strip() if len(name_desc) > 1 else ""
        if not name:
            continue
        formulas.append({"label": name, "description": description})

    if not formulas:
        return None
    return formulas


_GROUP_LABELS = {
    "kreislauf": [
        "Aorta", "Vena cava", "Koronararterien", "Arteriolen", "Kapillaren",
        "Mitralklappe", "Aortenklappe", "Trikuspidalklappe", "Pulmonalklappe",
        "SA-Knoten", "AV-Knoten", "His-Buendel",
    ],
    "chakren": [
        "Wurzelchakra", "Sakralchakra", "Solarplexus", "Herzchakra",
        "Kehlchakra", "Stirnchakra", "Kronenchakra",
    ],
    "meridiane": [
        "Lunge", "Dickdarm", "Magen", "Milz-Pankreas", "Herz", "DuennDarm",
        "Blase", "Niere", "Perikard", "Drei-Erwaermer", "Gallenblase", "Leber",
    ],
    "bakterien": [
        "Streptokokken", "Staphylokokken", "E.coli", "Helicobacter", "Borrelien",
    ],
    "viren": [
        "Influenza", "EBV", "HSV", "CMV", "HPV",
    ],
    "parasiten": [
        "Giardia", "Toxoplasma", "Ascaris", "Taenia",
    ],
    "pilze": [
        "Candida", "Aspergillus", "Malassezia",
    ],
    "schwermetalle": [
        "Quecksilber", "Blei", "Cadmium", "Aluminium", "Arsen",
    ],
    # Neue DB-lose Gruppen
    "endokrin": [
        "Schilddruesenachse", "Nebennieren", "Hypophyse", "Ovarien/Testes", "Pankreas",
    ],
    "detox": [
        "Leber", "Gallenfluss", "Niere", "Lymphe", "Haut",
    ],
    "entgiftung_leber": [
        "Leber – Phase 1 Aktivierung (Cytochrom-P450)",
        "Leber – Phase 1 Überlastung (oxidativer Stress)",
        "Leber – Phase 2 Konjugationskapazität",
        "Leber – Phase 2 Überlastung (Cofaktor-Mangel)",
        "Leber – Phase 3 Transport & Ausscheidung",
        "Glutathion-Status (GSH)",
        "Methylierungskapazität (SAMe)",
        "Gallenfluss & Gallensäuren", 
        "Leberzellregeneration (Hepatozyten)",
        "Entgiftung fettlöslicher Toxine",
        "Entgiftung wasserlöslicher Toxine",
        "Darm-Leber-Achse (enterohepatischer Kreislauf)",
    ],
    "mikrozirkulation": [
        "Kapillaren", "Endothel-NO", "Ery-Formbarkeit", "Viskositaet",
    ],
    "mitochondrien": [
        "Komplex I", "Komplex II", "Komplex III", "Komplex IV", "Komplex V", "CoQ10", "ROS",
    ],
    "entzuendung": [
        "IL-6", "TNF-alpha", "CRP", "NF-kB", "Mikroglia",
    ],
    "allergene": [
        "Histamin", "DAO", "Gluten", "Laktose", "Nickel",
    ],
    "mikronaehrstoffe": [
        "B-Komplex", "Vitamin D", "Vitamin K2", "Magnesium", "Zink", "Selen", "Eisen",
    ],
    "wirbelsaeule": [
        "Zervikal", "Thorakal", "Lumbal", "Sakrum", "Nervenaustritte",
    ],
    "odontone": [
        "Quadrant 1", "Quadrant 2", "Quadrant 3", "Quadrant 4", "Front/Hinter", "Meridianbezug",
    ],
    "schlaf": [
        "Melatonin", "HPA-Achse", "REM", "NREM", "Circadiane Uhr",
    ],
    # Quellenbasierte, aber DB-lose Gruppen (prozedural):
    "tcm_punkte": [
        "LI4", "ST36", "SP6", "PC6", "LV3", "GB20", "KI3", "HT7", "BL60", "DU20",
    ],
    "nebenchakren": [
        "Milzchakra", "Handchakra", "Fußchakra", "Ohrenchakra", "Nabelchakra", "Thymuschakra",
    ],
    "tcm_full": [
        "LU1", "LI1", "ST1", "SP1", "HT1", "SI1", "BL1", "KI1", "PC1", "TE1", "GB1", "LV1", "Ren1", "Du1",
    ],
    "chakren_full": [
        "Wurzelchakra", "Sakralchakra", "Solarplexus", "Herzchakra", "Kehlchakra", "Stirnchakra", "Kronenchakra",
    ],
    "extra_meridiane": [
        "Du Mai", "Ren Mai", "Chong Mai", "Dai Mai", "Yangqiao Mai", "Yinqiao Mai", "Yangwei Mai", "Yinwei Mai",
    ],
    "chakren_erweitert": [
        "Thymuschakra", "Hara", "Handchakra links", "Handchakra rechts", "Fußchakra links", "Fußchakra rechts",
    ],
    "tcm_punkte_extended": [
        "LU1", "LU5", "LU7", "LU9", "LI11", "ST25", "ST36", "ST40", "SP3", "SP6", "HT7", "SI3", "BL23", "BL40", "BL60", "KI3", "PC6", "TE5", "GB34", "LV3", "Ren12", "Ren17", "Du20",
    ],
    "spagyrik": [
        "Sulfur", "Mercurius", "Sal", "Ars Metallorum", "Antimonium", "Cuprum", "Ferrum",
    ],
    "laser_protokolle": [
        "Nogier A", "Nogier B", "Nogier C", "Nogier D", "Nogier E", "Nogier F", "Nogier G",
        "Bahr 1", "Bahr 2", "Bahr 3", "Bahr 4", "Bahr 5", "Bahr 6", "Bahr 7",
    ],
    "farbtherapie": [
        "Rot–Grün", "Blau–Orange", "Gelb–Violett", "Cyan–Rot", "Magenta–Grün", "Gelb–Indigo",
    ],
    "edelsteine": [
        "Amethyst", "Bergkristall", "Rosenquarz", "Citrin", "Achat", "Jaspis", "Sodalith", "Labradorit", "Turmalin", "Malachit",
    ],
    "rife_cafl_proc": [
        "CAFL-Band 1", "CAFL-Band 2", "CAFL-Band 3", "CAFL-Band 4", "CAFL-Band 5", "CAFL-Band 6",
    ],
    "baklayan_proc": [
        "Baklayan 1", "Baklayan 2", "Baklayan 3", "Baklayan 4", "Baklayan 5", "Baklayan 6",
    ],
    "ps_freq": ["PS-Freq Placeholder"],
    "schwermetalle_tox": ["Blei", "Quecksilber", "Cadmium", "Arsen", "Aluminium", "Nickel", "Chrom", "Kupfer"],
    "strahlung_tox": ["5G", "WLAN 2.4 GHz", "WLAN 5 GHz", "Bluetooth", "DECT", "LTE 1800", "UMTS", "Röntgen", "Gamma"],
    "zahnorgane": ["Zahn 11", "Zahn 21", "Zahn 31", "Zahn 41", "Schmelz", "Dentin", "Pulpa", "Parodont", "Zement", "Alveolarknochen", "Gingiva"],
    # Feiner differenzierte Erreger- und Toxinlisten für Multiplex-Scans
    "bakterien_fein": [
        "Bakterien – Streptococcus pyogenes",
        "Bakterien – Streptococcus pneumoniae",
        "Bakterien – Staphylococcus aureus",
        "Bakterien – Borrelia burgdorferi",
        "Bakterien – Borrelia garinii",
        "Bakterien – Helicobacter pylori",
        "Bakterien – E.coli (pathogen)",
        "Bakterien – Clostridium difficile",
        "Bakterien – Mycoplasma pneumoniae",
        "Bakterien – Chlamydia trachomatis",
        "Bakterien – Campylobacter jejuni",
        "Bakterien – Yersinia enterocolitica",
        "Bakterien – Salmonella spp.",
        "Bakterien – Klebsiella pneumoniae",
        "Bakterien – Pseudomonas aeruginosa",
        "Bakterien – Listeria monocytogenes",
    ],
    "viren_fein": [
        "Viren – EBV",
        "Viren – CMV",
        "Viren – HSV-1",
        "Viren – HSV-2",
        "Viren – VZV",
        "Viren – HHV-6",
        "Viren – HPV (low risk)",
        "Viren – HPV (high risk)",
        "Viren – Influenza A",
        "Viren – Influenza B",
        "Viren – Adenoviren",
        "Viren – Enteroviren",
        "Viren – Parvovirus B19",
        "Viren – Hepatitis B",
        "Viren – Hepatitis C",
        "Viren – Retroviren (endogen)",
    ],
    "parasiten_fein": [
        "Parasiten – Giardia lamblia",
        "Parasiten – Toxoplasma gondii",
        "Parasiten – Entamoeba histolytica",
        "Parasiten – Blastocystis hominis",
        "Parasiten – Ascaris lumbricoides",
        "Parasiten – Trichuris trichiura",
        "Parasiten – Taenia saginata",
        "Parasiten – Taenia solium",
        "Parasiten – Opisthorchis felineus",
        "Parasiten – Fasciola hepatica",
        "Parasiten – Strongyloides stercoralis",
        "Parasiten – Dientamoeba fragilis",
        "Parasiten – Ancylostoma duodenale",
        "Parasiten – Necator americanus",
        "Parasiten – Schistosoma spp.",
        "Parasiten – Echinococcus granulosus",
    ],
    "pilze_fein": [
        "Pilze – Candida albicans",
        "Pilze – Candida glabrata",
        "Pilze – Candida parapsilosis",
        "Pilze – Aspergillus fumigatus",
        "Pilze – Aspergillus niger",
        "Pilze – Malassezia furfur",
        "Pilze – Penicillium spp.",
        "Pilze – Mucor spp.",
        "Pilze – Trichophyton rubrum",
        "Pilze – Microsporum canis",
        "Pilze – Cryptococcus neoformans",
        "Pilze – Histoplasma capsulatum",
        "Pilze – Coccidioides spp.",
        "Pilze – Saccharomyces cerevisiae",
        "Pilze – Fusarium spp.",
        "Pilze – Alternaria alternata",
    ],
    "pestizide_tox": [
        "Pestizide – Glyphosat",
        "Pestizide – Atrazin",
        "Pestizide – DDT",
        "Pestizide – Lindan",
        "Pestizide – Organophosphate (gesamt)",
        "Pestizide – Neonicotinoide",
        "Pestizide – Pyrethroide",
        "Pestizide – Herbizide (gesamt)",
        "Pestizide – Fungizide (gesamt)",
        "Pestizide – Insektizide (gesamt)",
    ],
    "chemikalien_tox": [
        "Chemikalien – Phthalate (Weichmacher)",
        "Chemikalien – Bisphenol A",
        "Chemikalien – VOC (Lösungsmittel)",
        "Chemikalien – Formaldehyd",
        "Chemikalien – Flammschutzmittel",
        "Chemikalien – PCB",
        "Chemikalien – Dioxine",
        "Chemikalien – PAK (polyzyklische Aromaten)",
        "Chemikalien – Schwimmbadchemie",
        "Chemikalien – Reinigungsmittelreste",
    ],
    "geopathie": [
        "Geopathie – Wasserader",
        "Geopathie – Verwerfung",
        "Geopathie – Hartmann-Gitter",
        "Geopathie – Curry-Gitter",
        "Geopathie – Kreuzungspunkte",
        "Geopathie – Gitternetz-Knotenpunkt",
        "Geopathie – unterirdische Hohlräume",
        "Geopathie – geologische Störung",
    ],
    "emf_fein": [
        "EMF – 5G n78 (3.5 GHz)",
        "EMF – 5G n28 (700 MHz)",
        "EMF – 5G n258 (26 GHz)",
        "EMF – WLAN 2.4 GHz",
        "EMF – WLAN 5 GHz",
        "EMF – DECT",
        "EMF – LTE 800",
        "EMF – LTE 1800",
        "EMF – UMTS 2100",
        "EMF – Bluetooth",
        "EMF – PLC (Powerline)",
        "EMF – Hochspannungsleitung",
        "EMF – Trafostation",
        "EMF – Smart Meter",
        "EMF – Bahnstrom",
        "EMF – Radar",
    ],
    # Neue, klientenorientierte Felder – Emotion, Physisch, Mental, Astral
    "emotion": [
        "Emotion – Angst (Akut)",
        "Emotion – Angst (Grundton)",
        "Emotion – Vertrauen (Ressource)",
        "Emotion – Freude (Ausdruck)",
        "Emotion – Trauer (nicht gelebte)",
        "Emotion – Traurigkeit (akut)",
        "Emotion – Traurigkeit (Grundton)",
        "Emotion – Wut (unterdrückt)",
        "Emotion – Wut (konstruktiv)",
        "Emotion – Aggression (explosiv)",
        "Emotion – Aggression (implosiv)",
        "Emotion – Scham (alte Prägungen)",
        "Emotion – Schuld (übernommene Themen)",
        "Emotion – Schuldgefühl gegenüber anderen",
        "Emotion – Schuldgefühl sich selbst gegenüber",
        "Emotion – Ekel / Abwehr",
        "Emotion – Einsamkeit / Isolation",
        "Emotion – Überforderung / Stress",
        "Emotion – innere Ruhe (Entspannung)",
        "Emotion – Sicherheit / Geborgenheit",
        "Emotion – Unsicherheit / innere Unruhe",
        "Emotion – Verbundenheit (Herzöffnung)",
        "Emotion – Abgeschnittenheit / innere Leere",
        "Emotion – Mut / innere Stärke",
        "Emotion – Hoffnung / Zuversicht",
        "Emotion – Resignation / Aufgeben",
        "Emotion – Enttäuschung / Frustration",
        "Emotion – Begeisterung / Inspiration",
        "Emotion – Neugier / kindliche Offenheit",
        "Emotion – innere Freude (stiller Grundton)",
        "Emotion – innerer Friede (tiefe Ruhe)",
    ],
    "physisch": [
        "Physisch – Nervensystem (Übererregung)",
        "Physisch – Nervensystem (Erschöpfung)",
        "Physisch – Nervensystem (vegetativ sympathikoton)",
        "Physisch – Nervensystem (vegetativ parasympathikoton)",
        "Physisch – Hormonsystem (Dysbalance)",
        "Physisch – Hormonsystem (Stressachsen-Aktivierung)",
        "Physisch – Hormonsystem (Schilddrüsenachse)",
        "Physisch – Hormonsystem (Sexualhormone)",
        "Physisch – Immunsystem (Belastung)",
        "Physisch – Immunsystem (Autoimmunität)",
        "Physisch – Immunsystem (Immunschwäche)",
        "Physisch – Immunsystem (Regulation)",
        "Physisch – Verdauungssystem (Verarbeitung)",
        "Physisch – Verdauungssystem (Motilitätsstörung)",
        "Physisch – Verdauungssystem (Resorption)",
        "Physisch – Verdauungssystem (Barrierestörung)",
        "Physisch – Herz-Kreislauf (Rhythmus)",
        "Physisch – Herz-Kreislauf (Blutdruckregulation)",
        "Physisch – Herz-Kreislauf (Gefäßwand/Endothel)",
        "Physisch – Herz-Kreislauf (Mikrozirkulation)",
        "Physisch – Faszien/Struktur (Spannung)",
        "Physisch – Faszien/Struktur (Blockierungen)",
        "Physisch – Faszien/Struktur (Stabilität)",
        "Physisch – Faszien/Struktur (Regeneration)",
        "Physisch – Regeneration (Schlafqualität)",
        "Physisch – Regeneration (Tiefschlaf)",
        "Physisch – Regeneration (Tagesschläfrigkeit)",
        "Physisch – Regeneration (Erholungsfähigkeit)",
        "Physisch – Entgiftung (Leber)",
        "Physisch – Entgiftung (Niere)",
        "Physisch – Entgiftung (Lymphe)",
        "Physisch – Entgiftung (Haut/Schleimhäute)",
        "Physisch – Darmflora (Dysbiose)",
        "Physisch – Darmflora (Fehlbesiedlung)",
        "Physisch – Darmflora (Diversität)",
        "Physisch – Darmflora (Regeneration)",
        "Physisch – Mikrozirkulation (Kapillaren)",
        "Physisch – Mikrozirkulation (Viskosität)",
        "Physisch – Mikrozirkulation (Erythrozytenform)",
        "Physisch – Mikrozirkulation (Endothel-NO)",
        "Physisch – Muskulatur (Verspannung)",
        "Physisch – Muskulatur (Schwäche)",
        "Physisch – Muskulatur (Regeneration)",
        "Physisch – Muskulatur (Triggerpunkte)",
        "Physisch – Gelenke (Degeneration)",
        "Physisch – Gelenke (Entzündung)",
        "Physisch – Gelenke (Beweglichkeit)",
        "Physisch – Gelenke (Stabilität/Bänder)",
        "Physisch – Atemsystem (Lunge/Bronchien)",
        "Physisch – Atemsystem (Ventilation)",
        "Physisch – Atemsystem (Gasaustausch)",
        "Physisch – Atemsystem (allergische Reaktion)",
        "Physisch – Stoffwechsel (Blutzuckerregulation)",
        "Physisch – Stoffwechsel (Insulinresistenz)",
        "Physisch – Stoffwechsel (Lipidstoffwechsel)",
        "Physisch – Stoffwechsel (Säure-Basen-Haushalt)",
        "Physisch – Mitochondrien (ATP-Bildung)",
        "Physisch – Mitochondrien (ROS-Belastung)",
        "Physisch – Mitochondrien (Biogenese)",
        "Physisch – Mitochondrien (Membranpotential)",
        "Physisch – Schmerzsystem (akut)",
        "Physisch – Schmerzsystem (chronisch)",
        "Physisch – Schmerzsystem (Zentralisierung)",
        "Physisch – Schmerzsystem (Modulation/Endorphine)",
    ],
    "mental": [
        "Mental – Glaubenssatz (Ich bin nicht genug)",
        "Mental – Glaubenssatz (Ich darf meinen Weg gehen)",
        "Mental – Glaubenssatz (Ich bin nicht wichtig)",
        "Mental – Glaubenssatz (Ich muss perfekt sein)",
        "Mental – Grübeln / Overthinking",
        "Mental – Katastrophisieren (Worst-Case-Denken)",
        "Mental – Zukunftsangst",
        "Mental – Vergangenheitsbindung",
        "Mental – Klarheit / Fokus",
        "Mental – Präsenz im Hier und Jetzt",
        "Mental – Ablenkbarkeit / Zerstreutheit",
        "Mental – Entscheidungsfähigkeit",
        "Mental – innere Ausrichtung (Zielklarheit)",
        "Mental – Prioritäten setzen",
        "Mental – Zielumsetzung / Dranbleiben",
        "Mental – Planung / Struktur",
        "Mental – Selbstbild (einschränkend)",
        "Mental – Selbstbild (tragend)",
        "Mental – innerer Kritiker / Selbstabwertung",
        "Mental – Selbstakzeptanz",
        "Mental – mentale Erschöpfung",
        "Mental – mentale Übererregung",
        "Mental – Reizüberflutung",
        "Mental – Regeneration / geistige Ruhe",
        "Mental – Perfektionismus / Kontrollbedürfnis",
        "Mental – Prokrastination / Aufschieben",
        "Mental – Kreativer Fluss / Inspiration",
        "Mental – Flexibilität / Anpassungsfähigkeit",
        "Mental – Offenheit für Neues",
        "Mental – starre Denkmuster",
        "Mental – innere Ausrichtung (Herz-Kopf-Kohärenz)",
        "Mental – Verbundenheit mit Intuition",
    ],
    "astral": [
        "Astral – fremde Felder / Überlagerungen",
        "Astral – Bindungen (alte Themen)",
        "Astral – Räume (Wohn-/Arbeitsfeld)",
        "Astral – Ahnenfeld (ungeklärte Themen)",
        "Astral – Schutz / Abgrenzung",
        "Astral – Seelenauftrag (Resonanz)",
        "Astral – kollektives Feld (Belastung)",
        "Astral – kollektives Feld (Ressource)",
        "Astral – geopatische Zonen / Erdstrahlung",
        "Astral – technische Felder (Elektrosmog)",
        "Astral – technische Felder (WLAN/5G)",
        "Astral – Portale / Übergänge (Ortswechsel)",
        "Astral – frühere Inkarnationen (offene Themen)",
        "Astral – spirituelle Führung / Guides (Ressource)",
        "Astral – Ortsgedächtnis (Ereignisse)",
        "Astral – Gruppenfelder (Familie)",
        "Astral – Gruppenfelder (Team / Praxis)",
        "Astral – Naturfelder (Wald)",
        "Astral – Naturfelder (Wasser)",
        "Astral – Naturfelder (Berge)",
        "Astral – Schlafplatz (Regenerationsfeld)",
        "Astral – Arbeitsumfeld (Belastung)",
        "Astral – Reise-/Transitfelder",
        "Astral – Räume nach Konflikten",
        "Astral – Räume nach Heilung / Klärung",
        "Astral – Verbindung zur Quelle / Transzendenz",
        "Astral – Inkarnationsvertrag / Lebensweg",
        "Astral – Familiensystem (unausgesprochene Themen)",
        "Astral – Kollektivfeld (Angst)",
        "Astral – Kollektivfeld (Vertrauen)",
        "Astral – Feld der Praxis / Klientensystem",
        "Astral – digitale Felder (Online, Social Media)",
    ],
}

# Erweitere _GROUP_LABELS mit 37 neuen FEIN und MULTIPLEX Gruppen aus groups_extended_v2.py
if GROUPS_EXTENDED_V2_AVAILABLE and gext2 is not None:
    _GROUP_LABELS.update({
        # STRUKTURELLE SYSTEME - FEIN
        "wirbelsaeule_fein": gext2.WIRBELSAEULE_FEIN,
        "wirbelsaeule_bandscheiben_fein": gext2.WIRBELSAEULE_BANDSCHEIBEN_FEIN,
        "zahnorgane_fein": gext2.ZAHNORGANE_FEIN,
        
        # NERVENSYSTEM - FEIN
        "nervensystem_zns_fein": gext2.NERVENSYSTEM_ZNS_FEIN,
        "nervensystem_pns_fein": gext2.NERVENSYSTEM_PNS_FEIN,
        "nervensystem_hirnnerven_fein": gext2.NERVENSYSTEM_HIRNNERVEN_FEIN,
        "nervensystem_neurotransmitter_fein": gext2.NERVENSYSTEM_NEUROTRANSMITTER_FEIN,
        
        # LYMPHSYSTEM - FEIN
        "lymphsystem_lymphknoten_fein": gext2.LYMPHSYSTEM_LYMPHKNOTEN_FEIN,
        
        # IMMUNSYSTEM - FEIN
        "immunsystem_angeboren_fein": gext2.IMMUNSYSTEM_ANGEBOREN_FEIN,
        "immunsystem_erworben_fein": gext2.IMMUNSYSTEM_ERWORBEN_FEIN,
        "immunsystem_zytokine_fein": gext2.IMMUNSYSTEM_ZYTOKINE_FEIN,
        "immunsystem_autoimmun_fein": gext2.IMMUNSYSTEM_AUTOIMMUN_FEIN,
        
        # KNOCHEN & GELENKE - FEIN
        "knochen_gelenke_fein": gext2.KNOCHEN_GELENKE_FEIN,
        
        # VERDAUUNG - FEIN
        "verdauung_duenndarm_fein": gext2.VERDAUUNG_DUENNDARM_FEIN,
        "verdauung_dickdarm_fein": gext2.VERDAUUNG_DICKDARM_FEIN,
        "verdauung_mikrobiom_fein": gext2.VERDAUUNG_MIKROBIOM_FEIN,
        
        # ATMUNG - FEIN
        "atmung_lunge_fein": gext2.ATMUNG_LUNGE_FEIN,
        
        # ENTGIFTUNG - FEIN
        "entgiftung_leber_phase1_fein": gext2.ENTGIFTUNG_LEBER_PHASE1_FEIN,
        "entgiftung_leber_phase2_fein": gext2.ENTGIFTUNG_LEBER_PHASE2_FEIN,
        "entgiftung_leber_phase3_fein": gext2.ENTGIFTUNG_LEBER_PHASE3_FEIN,
        
        # SYMPTOMATIK - FEIN
        "schmerz_kopf_fein": gext2.SCHMERZ_KOPF_FEIN,
        "schlafstoerungen_fein": gext2.SCHLAFSTOERUNGEN_FEIN,
        "hautprobleme_fein": gext2.HAUTPROBLEME_FEIN,
        
        # REMEDIES - ORTHOMOLEKULAR FEIN
        "orthomolekular_vitamine_fein": gext2.ORTHOMOLEKULAR_VITAMINE_FEIN,
        "orthomolekular_mineralien_fein": gext2.ORTHOMOLEKULAR_MINERALIEN_FEIN,
        "orthomolekular_aminosauren_fein": gext2.ORTHOMOLEKULAR_AMINOSAUREN_FEIN,
        
        # REMEDIES - MULTIPLEX (KOMBINATIONEN)
        "homoeopathie_multiplex": gext2.HOMOEOPATHIE_MULTIPLEX,
        "tcm_rezepturen_multiplex": gext2.TCM_REZEPTUREN_MULTIPLEX,
        "spagyrik_multiplex": gext2.SPAGYRIK_MULTIPLEX,
        "bachblueten_multiplex": gext2.BACHBLUETEN_MULTIPLEX,
        "schuessler_multiplex": gext2.SCHUESSLER_MULTIPLEX,
        "phytotherapie_tees_multiplex": gext2.PHYTOTHERAPIE_TEES_MULTIPLEX,
        "phytotherapie_tinkturen_multiplex": gext2.PHYTOTHERAPIE_TINKTUREN_MULTIPLEX,
        "aromatherapie_multiplex": gext2.AROMATHERAPIE_MULTIPLEX,
        "orthomolekular_multiplex": gext2.ORTHOMOLEKULAR_MULTIPLEX,
        "frequenz_clark_multiplex": gext2.FREQUENZ_CLARK_MULTIPLEX,
        "frequenz_rife_multiplex": gext2.FREQUENZ_RIFE_MULTIPLEX,
        "frequenz_solfeggio_multiplex": gext2.FREQUENZ_SOLFEGGIO_MULTIPLEX,
        
        # PHASE 2 VERFEINERUNGEN
        "schwindel_vestibular_fein": gext2.SCHWINDEL_VESTIBULAR_FEIN,
        "schwindel_zentral_fein": gext2.SCHWINDEL_ZENTRAL_FEIN,
        "kreislauf_fein": gext2.KREISLAUF_FEIN,
        "herz_fein": gext2.HERZ_FEIN,
        "schilddruese_fein": gext2.SCHILDDRUESE_FEIN,
        "nebenniere_fein": gext2.NEBENNIERE_FEIN,
        "hypophyse_fein": gext2.HYPOPHYSE_FEIN,
        
        # PHASE 3 VERFEINERUNGEN (OPTIONAL)
        "auge_fein": gext2.AUGE_FEIN,
        "ohr_fein": gext2.OHR_FEIN,
        "muskulatur_fein": gext2.MUSKULATUR_FEIN,
        "faszien_fein": gext2.FASZIEN_FEIN,
        "blut_fein": gext2.BLUT_FEIN,
    })

# Erweitere _GROUP_LABELS mit 44 neuen PHASE 4 Gruppen (A-M: Zähne, Wirbelsäule, Strahlung, etc.)
if GROUPS_PHASE4_AVAILABLE and gp4_1 is not None and gp4_2 is not None and gp4_3 is not None:
    _GROUP_LABELS.update({
        # A) ZÄHNE (4 Gruppen)
        "zahn_symptome_fein": gp4_1.ZAHN_SYMPTOME_FEIN,
        "zahn_pathologien_fein": gp4_1.ZAHN_PATHOLOGIEN_FEIN,
        "zahn_materialien_fein": gp4_1.ZAHN_MATERIALIEN_FEIN,
        "zahn_remedies_multiplex": gp4_1.ZAHN_REMEDIES_MULTIPLEX,
        
        # B) WIRBELSÄULE (3 Gruppen)
        "wirbelsaeule_symptome_fein": gp4_1.WIRBELSAEULE_SYMPTOME_FEIN,
        "wirbelsaeule_pathologien_fein": gp4_1.WIRBELSAEULE_PATHOLOGIEN_FEIN,
        "wirbelsaeule_remedies_multiplex": gp4_1.WIRBELSAEULE_REMEDIES_MULTIPLEX,
        
        # C) STRAHLUNG & GEOPATHIE (4 Gruppen)
        "strahlung_symptome_fein": gp4_2.STRAHLUNG_SYMPTOME_FEIN,
        "strahlung_quellen_fein": gp4_2.STRAHLUNG_QUELLEN_FEIN,
        "geopathie_fein": gp4_2.GEOPATHIE_FEIN,
        "strahlung_schutz_multiplex": gp4_2.STRAHLUNG_SCHUTZ_MULTIPLEX,
        
        # D) ENTGIFTUNG (3 Gruppen)
        "entgiftung_symptome_fein": gp4_2.ENTGIFTUNG_SYMPTOME_FEIN,
        "entgiftung_organe_fein": gp4_2.ENTGIFTUNG_ORGANE_FEIN,
        "entgiftung_remedies_multiplex": gp4_2.ENTGIFTUNG_REMEDIES_MULTIPLEX,
        
        # E) VERDAUUNG (3 Gruppen)
        "verdauung_symptome_fein": gp4_2.VERDAUUNG_SYMPTOME_FEIN,
        "verdauung_pathologien_fein": gp4_2.VERDAUUNG_PATHOLOGIEN_FEIN,
        "verdauung_remedies_multiplex": gp4_2.VERDAUUNG_REMEDIES_MULTIPLEX,
        
        # F) NERVENSYSTEM (3 Gruppen)
        "nerven_symptome_fein": gp4_1.NERVEN_SYMPTOME_FEIN,
        "nerven_pathologien_fein": gp4_1.NERVEN_PATHOLOGIEN_FEIN,
        "nerven_remedies_multiplex": gp4_1.NERVEN_REMEDIES_MULTIPLEX,
        
        # G) HERZ-KREISLAUF (4 Gruppen)
        "herz_symptome_fein": gp4_1.HERZ_SYMPTOME_FEIN,
        "kreislauf_symptome_fein": gp4_1.KREISLAUF_SYMPTOME_FEIN,
        "herz_pathologien_fein": gp4_1.HERZ_PATHOLOGIEN_FEIN,
        "herz_remedies_multiplex": gp4_1.HERZ_REMEDIES_MULTIPLEX,
        
        # H) KNOCHEN & GELENKE (3 Gruppen)
        "knochen_symptome_fein": gp4_3.KNOCHEN_SYMPTOME_FEIN,
        "knochen_pathologien_fein": gp4_3.KNOCHEN_PATHOLOGIEN_FEIN,
        "knochen_remedies_multiplex": gp4_3.KNOCHEN_REMEDIES_MULTIPLEX,
        
        # I) TOXINE & SCHWERMETALLE (4 Gruppen)
        "toxine_symptome_fein": gp4_2.TOXINE_SYMPTOME_FEIN,
        "schwermetalle_detailliert_fein": gp4_2.SCHWERMETALLE_DETAILLIERT_FEIN,
        "chemikalien_detailliert_fein": gp4_2.CHEMIKALIEN_DETAILLIERT_FEIN,
        "toxine_remedies_multiplex": gp4_2.TOXINE_REMEDIES_MULTIPLEX,
        
        # J) ATMUNG (3 Gruppen)
        "atmung_symptome_fein": gp4_3.ATMUNG_SYMPTOME_FEIN,
        "atmung_pathologien_fein": gp4_3.ATMUNG_PATHOLOGIEN_FEIN,
        "atmung_remedies_multiplex": gp4_3.ATMUNG_REMEDIES_MULTIPLEX,
        
        # K) HORMONELLES SYSTEM (4 Gruppen)
        "hormone_symptome_fein": gp4_3.HORMONE_SYMPTOME_FEIN,
        "hormone_schilddruese_fein": gp4_3.HORMONE_SCHILDDRUESE_FEIN,
        "hormone_geschlecht_fein": gp4_3.HORMONE_GESCHLECHT_FEIN,
        "hormone_remedies_multiplex": gp4_3.HORMONE_REMEDIES_MULTIPLEX,
        
        # L) LUFTBELASTUNGEN & WOHNRAUMGIFTE (3 Gruppen)
        "luft_symptome_fein": gp4_3.LUFT_SYMPTOME_FEIN,
        "wohnraumgifte_fein": gp4_3.WOHNRAUMGIFTE_FEIN,
        "luft_remedies_multiplex": gp4_3.LUFT_REMEDIES_MULTIPLEX,
        
        # M) NAHRUNGSMITTELBELASTUNGEN (3 Gruppen)
        "nahrung_symptome_fein": gp4_3.NAHRUNG_SYMPTOME_FEIN,
        "nahrung_unvertraeglichkeiten_fein": gp4_3.NAHRUNG_UNVERTRAEGLICHKEITEN_FEIN,
        "nahrung_remedies_multiplex": gp4_3.NAHRUNG_REMEDIES_MULTIPLEX,
    })

# Erweitere _GROUP_LABELS mit 30 neuen PHASE 5 Gruppen (Lücken-Schließung)
if GROUPS_PHASE5_AVAILABLE and gp5_1 is not None and gp5_2 is not None and gp5_3 is not None and gp5_5 is not None:
    _GROUP_LABELS.update({
        # INFEKTIONEN & ERREGER (8 Gruppen)
        "bakterien_detailliert_fein": gp5_1.BAKTERIEN_DETAILLIERT_FEIN,
        "viren_detailliert_fein": gp5_1.VIREN_DETAILLIERT_FEIN,
        "pilze_detailliert_fein": gp5_1.PILZE_DETAILLIERT_FEIN,
        "parasiten_detailliert_fein": gp5_1.PARASITEN_DETAILLIERT_FEIN,
        "biofilme_fein": gp5_1.BIOFILME_FEIN,
        "infektions_symptome_fein": gp5_1.INFEKTIONS_SYMPTOME_FEIN,
        "anti_infektions_remedies_multiplex": gp5_1.ANTI_INFEKTIONS_REMEDIES_MULTIPLEX,
        "immunstaerkung_remedies_multiplex": gp5_1.IMMUNSTAERKUNG_REMEDIES_MULTIPLEX,
        
        # NÄHRSTOFFMÄNGEL (6 Gruppen)
        "vitamine_detailliert_fein": gp5_2.VITAMINE_DETAILLIERT_FEIN,
        "mineralien_spurenelemente_detailliert_fein": gp5_2.MINERALIEN_SPURENELEMENTE_DETAILLIERT_FEIN,
        "aminosaeuren_detailliert_fein": gp5_2.AMINOSAEUREN_DETAILLIERT_FEIN,
        "fettsaeuren_detailliert_fein": gp5_2.FETTSAEUREN_DETAILLIERT_FEIN,
        "naehrstoffmangel_symptome_fein": gp5_2.NAEHRSTOFFMANGEL_SYMPTOME_FEIN,
        "orthomolekular_therapie_multiplex": gp5_2.ORTHOMOLEKULAR_THERAPIE_MULTIPLEX,
        
        # ENERGETISCHE SYSTEME (4 Gruppen)
        "chakren_detailliert_fein": gp5_3.CHAKREN_DETAILLIERT_FEIN,
        "meridiane_detailliert_fein": gp5_3.MERIDIANE_DETAILLIERT_FEIN,
        "energetische_blockaden_fein": gp5_3.ENERGETISCHE_BLOCKADEN_FEIN,
        "energie_remedies_multiplex": gp5_3.ENERGIE_REMEDIES_MULTIPLEX,
        
        # PSYCHE & EMOTIONEN (3 Gruppen)
        "emotionale_blockaden_fein": gp5_3.EMOTIONALE_BLOCKADEN_FEIN,
        "psychosomatik_fein": gp5_3.PSYCHOSOMATIK_FEIN,
        "psyche_remedies_multiplex": gp5_3.PSYCHE_REMEDIES_MULTIPLEX,
        
        # WEITERE SYSTEME (9 Gruppen)
        "miasmatik_fein": gp5_5.MIASMATIK_FEIN,
        "umweltbelastungen_erweitert_fein": gp5_5.UMWELTBELASTUNGEN_ERWEITERT_FEIN,
        "urogenitalsystem_fein": gp5_5.UROGENITALSYSTEM_FEIN,
        "haut_detailliert_fein": gp5_5.HAUT_DETAILLIERT_FEIN,
        "kinderkrankheiten_fein": gp5_5.KINDERKRANKHEITEN_FEIN,
        "schwangerschaft_geburt_fein": gp5_5.SCHWANGERSCHAFT_GEBURT_FEIN,
        "wechseljahre_detailliert_fein": gp5_5.WECHSELJAHRE_DETAILLIERT_FEIN,
        "altersbeschwerden_fein": gp5_5.ALTERSBESCHWERDEN_FEIN,
        "miasmatik_remedies_multiplex": gp5_5.MIASMATIK_REMEDIES_MULTIPLEX,
    })

# Erweitere _GROUP_LABELS mit neuen Gruppen aus groups_extended.py
if GROUPS_EXTENDED_AVAILABLE and gext is not None:
    _GROUP_LABELS.update({
        # WIRBELSÄULE (erweitert)
        "wirbelsaeule_hws": gext.WIRBELSAEULE_HWS,
        "wirbelsaeule_bws": gext.WIRBELSAEULE_BWS,
        "wirbelsaeule_lws": gext.WIRBELSAEULE_LWS,
        "wirbelsaeule_sakral": gext.WIRBELSAEULE_SAKRAL,
        "wirbelsaeule_bandscheiben": gext.WIRBELSAEULE_BANDSCHEIBEN,
        "wirbelsaeule_facetten": gext.WIRBELSAEULE_FACETTEN,
        
        # ZAHNBEZÜGE ORGANE (erweitert)
        "zahnorgane_quadrant1": gext.ZAHNORGANE_QUADRANT1,
        "zahnorgane_quadrant2": gext.ZAHNORGANE_QUADRANT2,
        "zahnorgane_quadrant3": gext.ZAHNORGANE_QUADRANT3,
        "zahnorgane_quadrant4": gext.ZAHNORGANE_QUADRANT4,
        "zahnorgane_weisheitszaehne": gext.ZAHNORGANE_WEISHEITSZAEHNE,
        "zahnorgane_frontzaehne": gext.ZAHNORGANE_FRONTZAEHNE,
        "zahnorgane_kiefergelenk": gext.ZAHNORGANE_KIEFERGELENK,
        "zahnorgane_kiefer_herde": gext.ZAHNORGANE_KIEFER_HERDE,
        
        # NERVENSYSTEM (erweitert)
        "nervensystem_zns": gext.NERVENSYSTEM_ZNS,
        "nervensystem_pns": gext.NERVENSYSTEM_PNS,
        "nervensystem_vegetativ": gext.NERVENSYSTEM_VEGETATIV,
        "nervensystem_hirnnerven": gext.NERVENSYSTEM_HIRNNERVEN,
        "nervensystem_plexus": gext.NERVENSYSTEM_PLEXUS,
        "nervensystem_neurotransmitter": gext.NERVENSYSTEM_NEUROTRANSMITTER,
        
        # LYMPHSYSTEM (neu)
        "lymphsystem_lymphknoten": gext.LYMPHSYSTEM_LYMPHKNOTEN,
        "lymphsystem_milz": gext.LYMPHSYSTEM_MILZ,
        "lymphsystem_thymus": gext.LYMPHSYSTEM_THYMUS,
        "lymphsystem_tonsillen": gext.LYMPHSYSTEM_TONSILLEN,
        "lymphsystem_drainage": gext.LYMPHSYSTEM_DRAINAGE,
        
        # IMMUNSYSTEM (erweitert)
        "immunsystem_angeboren": gext.IMMUNSYSTEM_ANGEBOREN,
        "immunsystem_erworben": gext.IMMUNSYSTEM_ERWORBEN,
        "immunsystem_zytokine": gext.IMMUNSYSTEM_ZYTOKINE,
        "immunsystem_antikoerper": gext.IMMUNSYSTEM_ANTIKOERPER,
        "immunsystem_autoimmun": gext.IMMUNSYSTEM_AUTOIMMUN,
        
        # KNOCHEN (neu)
        "knochen_osteoporose": gext.KNOCHEN_OSTEOPOROSE,
        "knochen_osteoblasten": gext.KNOCHEN_OSTEOBLASTEN,
        "knochen_osteoklasten": gext.KNOCHEN_OSTEOKLASTEN,
        "knochen_gelenke": gext.KNOCHEN_GELENKE,
        "knochen_knorpel": gext.KNOCHEN_KNORPEL,
        
        # VERDAUUNG (erweitert)
        "verdauung_magen": gext.VERDAUUNG_MAGEN,
        "verdauung_duenndarm": gext.VERDAUUNG_DUENNDARM,
        "verdauung_dickdarm": gext.VERDAUUNG_DICKDARM,
        "verdauung_leber": gext.VERDAUUNG_LEBER,
        "verdauung_galle": gext.VERDAUUNG_GALLE,
        "verdauung_pankreas": gext.VERDAUUNG_PANKREAS,
        "verdauung_mikrobiom": gext.VERDAUUNG_MIKROBIOM,
        "verdauung_barriere": gext.VERDAUUNG_BARRIERE,
        
        # ATMUNG (erweitert)
        "atmung_lunge": gext.ATMUNG_LUNGE,
        "atmung_bronchien": gext.ATMUNG_BRONCHIEN,
        "atmung_zwerchfell": gext.ATMUNG_ZWERCHFELL,
        "atmung_nase": gext.ATMUNG_NASE,
        "atmung_rachen": gext.ATMUNG_RACHEN,
        
        # ENTGIFTUNG (erweitert)
        "entgiftung_leber_phase1": gext.ENTGIFTUNG_LEBER_PHASE1,
        "entgiftung_leber_phase2": gext.ENTGIFTUNG_LEBER_PHASE2,
        "entgiftung_leber_phase3": gext.ENTGIFTUNG_LEBER_PHASE3,
        "entgiftung_niere": gext.ENTGIFTUNG_NIERE,
        "entgiftung_haut": gext.ENTGIFTUNG_HAUT,
        "entgiftung_lymphe": gext.ENTGIFTUNG_LYMPHE,
        "entgiftung_darm": gext.ENTGIFTUNG_DARM,
        
        # SYMPTOMATIK - SCHWINDEL
        "schwindel_vestibular": gext.SCHWINDEL_VESTIBULAR,
        "schwindel_zentral": gext.SCHWINDEL_ZENTRAL,
        "schwindel_kreislauf": gext.SCHWINDEL_KREISLAUF,
        "schwindel_hws": gext.SCHWINDEL_HWS,
        "schwindel_medikament": gext.SCHWINDEL_MEDIKAMENT,
        
        # WEITERE SYMPTOMATIKEN
        "schmerz_kopf": gext.SCHMERZ_KOPF,
        "schmerz_ruecken": gext.SCHMERZ_RUECKEN,
        "schmerz_gelenk": gext.SCHMERZ_GELENK,
        "muedigkeit_chronisch": gext.MUEDIGKEIT_CHRONISCH,
        "schlafstoerungen": gext.SCHLAFSTOERUNGEN,
        "konzentration": gext.KONZENTRATION,
        "hautprobleme": gext.HAUTPROBLEME,
        "allergien_symptom": gext.ALLERGIEN,
        
        # REMEDIES - BACHBLÜTEN
        "bachblueten_38": gext.BACHBLUETEN_38,
        "bachblueten_rescue": gext.BACHBLUETEN_RESCUE,
        "bachblueten_emotionen": gext.BACHBLUETEN_EMOTIONEN,
        
        # HOMÖOPATHIE (erweitert)
        "homoeopathie_nosoden": gext.HOMOEOPATHIE_NOSODEN,
        "homoeopathie_sarcoden": gext.HOMOEOPATHIE_SARCODEN,
        "homoeopathie_komplexmittel": gext.HOMOEOPATHIE_KOMPLEXMITTEL,
        "homoeopathie_isopathie": gext.HOMOEOPATHIE_ISOPATHIE,
        
        # SCHÜSSLER-SALZE
        "schuessler_12": gext.SCHUESSLER_12,
        "schuessler_ergaenzung": gext.SCHUESSLER_ERGAENZUNG,
        
        # PHYTOTHERAPIE
        "phytotherapie_tees": gext.PHYTOTHERAPIE_TEES,
        "phytotherapie_tinkturen": gext.PHYTOTHERAPIE_TINKTUREN,
        "phytotherapie_extrakte": gext.PHYTOTHERAPIE_EXTRAKTE,
        "phytotherapie_ayurveda": gext.PHYTOTHERAPIE_AYURVEDA,
        
        # AROMATHERAPIE
        "aromatherapie_oele": gext.AROMATHERAPIE_OELE,
        "aromatherapie_mischungen": gext.AROMATHERAPIE_MISCHUNGEN,
        
        # ORGANOTHERAPIE
        "organotherapie_glandulae": gext.ORGANOTHERAPIE_GLANDULAE,
        
        # ORTHOMOLEKULAR
        "orthomolekular_vitamine": gext.ORTHOMOLEKULAR_VITAMINE,
        "orthomolekular_mineralien": gext.ORTHOMOLEKULAR_MINERALIEN,
        "orthomolekular_aminosauren": gext.ORTHOMOLEKULAR_AMINOSAUREN,
        "orthomolekular_fettsauren": gext.ORTHOMOLEKULAR_FETTSAUREN,
        
        # PEPTIDE
        "peptide_bioregulator": gext.PEPTIDE_BIOREGULATOR,
        "peptide_thymus": gext.PEPTIDE_THYMUS,
        
        # FREQUENZTHERAPIE (erweitert)
        "frequenz_clark": gext.FREQUENZ_CLARK,
        "frequenz_royal_rife": gext.FREQUENZ_ROYAL_RIFE,
        "frequenz_solfeggio": gext.FREQUENZ_SOLFEGGIO,
        "frequenz_binaural": gext.FREQUENZ_BINAURAL,
        
        # ENERGETISCHE REMEDIES
        "edelsteine_chakren": gext.EDELSTEINE_CHAKREN,
        "edelsteine_schutz": gext.EDELSTEINE_SCHUTZ,
        "kristalle_heilung": gext.KRISTALLE_HEILUNG,
        
        # BIOPHYSIKALISCHE THERAPIEN
        "magnetfeld": gext.MAGNETFELD,
        "licht_farbe": gext.LICHT_FARBE,
        "klang_therapie": gext.KLANG_THERAPIE,
        
        # MODERNE THERAPIEN
        "stammzellen_aktivierung": gext.STAMMZELLEN_AKTIVIERUNG,
        "nad_booster": gext.NAD_BOOSTER,
        "autophagie_aktivierung": gext.AUTOPHAGIE_AKTIVIERUNG,
        
        # TRADITIONELLE SYSTEME
        "ayurveda_dosha": gext.AYURVEDA_DOSHA,
        "tibetische_medizin": gext.TIBETISCHE_MEDIZIN,
        "unani_medizin": gext.UNANI_MEDIZIN,
    })


def _labels_from(*group_names: str, fallback: list[str]) -> list[str]:
    labels: list[str] = []
    for group_name in group_names:
        labels.extend(_GROUP_LABELS.get(group_name, []))
    return labels or fallback


# Profil-Integritaetsgruppen: diese Namen werden von Profilen und Remedy-
# Auto-Matcher referenziert und muessen direkt im Gruppenkatalog aufloesbar sein.
_GROUP_LABELS.update({
    # Atmung, Allergie, Nahrung
    "lunge_funktion_fein": _labels_from(
        "atmung_lunge_fein",
        fallback=[
            "Alveolen Gasaustausch",
            "Lungenvolumen Regulation",
            "Bronchiale Ventilation",
            "Sauerstoffaufnahme",
            "CO2-Abatmung",
            "Surfactant Balance",
        ],
    ),
    "lunge_pathologien_fein": _labels_from(
        "atmung_pathologien_fein",
        fallback=[
            "Bronchitis Resonanz",
            "Pneumonie Resonanz",
            "Asthma Resonanz",
            "COPD Resonanz",
            "Lungenfibrose Resonanz",
        ],
    ),
    "bronchien_fein": _labels_from(
        "atmung_bronchien",
        fallback=[
            "Bronchien Hauptaeste",
            "Bronchiolen",
            "Bronchialschleimhaut",
            "Bronchialsekret",
            "Bronchospasmus",
        ],
    ),
    "atemwege_obere_fein": _labels_from(
        "atmung_nase", "atmung_rachen",
        fallback=[
            "Nasenschleimhaut",
            "Nasennebenhoehlen",
            "Rachenraum",
            "Kehlkopf",
            "Stimmbaender",
            "Tubenbelueftung",
        ],
    ),
    "allergie_atemwege_fein": [
        "Pollenbelastung Atemwege",
        "Hausstaubmilben Atemwege",
        "Schimmelsporen Atemwege",
        "Allergische Rhinitis",
        "Bronchiale Hyperreaktivitaet",
        "Histaminreaktion Bronchien",
    ],
    "allergie_haut_fein": [
        "Urtikaria",
        "Ekzematische Reaktion",
        "Kontaktallergie Haut",
        "Pruritus allergisch",
        "Mastzellreaktion Haut",
    ],
    "allergie_nahrung_fein": _labels_from(
        "nahrung_unvertraeglichkeiten_fein",
        fallback=[
            "Nahrungsmittelallergie",
            "Pseudoallergie Nahrung",
            "Histaminreiche Nahrung",
            "Milcheiweissreaktion",
            "Weizenreaktion",
        ],
    ),
    "histamin_fein": [
        "Histaminabbau",
        "DAO-Aktivitaet",
        "Mastzellaktivierung",
        "Histaminliberatoren",
        "Histaminintoleranz",
    ],
    "laktose_fein": ["Laktose", "Laktase", "Milchzucker", "Duennndarm Laktase", "Laktosemalabsorption"],
    "gluten_fein": ["Gluten", "Gliadin", "Weizenprotein", "Darmbarriere Gluten", "Zonulin Resonanz"],
    "fruktose_fein": ["Fruktose", "Fruktosetransporter", "Fruktosemalabsorption", "Obstzucker Belastung", "Darmgasbildung"],
    "allergie_remedies_multiplex": [
        "Allergie - homoeopathische Einzelmittel",
        "Allergie - Schuessler Salze",
        "Allergie - Heel Komplexmittel",
        "Allergie - Pflanzenextrakte",
        "Allergie - Bachblueten Begleitung",
    ],

    # Herz, Kreislauf, Lymphe
    "blutdruck_fein": ["Systolischer Blutdruck", "Diastolischer Blutdruck", "Gefaeßtonus", "Renin-Angiotensin-System", "Barorezeptoren"],
    "gefaesse_fein": ["Arterien", "Venen", "Kapillaren", "Endothel", "Mikrozirkulation", "Gefaeßelastizitaet"],
    "herz_rhythmus_fein": ["Sinusknoten", "AV-Knoten", "Herzrhythmus Variabilitaet", "Extrasystolen", "Reizleitungssystem"],
    "lymphsystem": _labels_from(
        "lymphsystem_lymphknoten", "lymphsystem_milz", "lymphsystem_thymus", "lymphsystem_tonsillen", "lymphsystem_drainage",
        fallback=["Lymphknoten", "Milz", "Thymus", "Tonsillen", "Lymphdrainage"],
    ),
    "lymphsystem_fein": _labels_from(
        "lymphsystem_lymphknoten_fein", "lymphsystem_drainage",
        fallback=["Lymphfluss", "Lymphstau", "Lymphknoten fein", "Gewebsdrainage", "Immunlymphatik"],
    ),
    "kreislauf_remedies_multiplex": ["Kreislauf - Crataegus", "Kreislauf - Schuessler Salze", "Kreislauf - homoeopathische Mittel", "Kreislauf - Mikrozirkulation"],

    # Endokrin, Hormone, Stoffwechsel
    "endokrin_fein": _labels_from(
        "schilddruese_fein", "nebenniere_fein", "hypophyse_fein", "hormone_symptome_fein",
        fallback=["Hypophyse", "Schilddruese", "Nebenniere", "Pankreas endokrin", "Gonaden"],
    ),
    "schilddruese": _labels_from("schilddruese_fein", fallback=["Schilddruese", "T3", "T4", "TSH", "Jodstoffwechsel"]),
    "nebenniere": _labels_from("nebenniere_fein", fallback=["Nebenniere", "Cortisol", "DHEA", "Aldosteron", "Stressachse"]),
    "hypothalamus_fein": ["Hypothalamus", "HPA-Achse", "Temperaturregulation", "Hunger-Saettigung", "Neuroendokrine Steuerung"],
    "hormone_pathologien_fein": ["Hormonelle Dysbalance", "Hypothyreose Resonanz", "Hyperthyreose Resonanz", "Nebennierenstress", "Zyklusstörung Resonanz"],
    "geschlechtshormone_fein": _labels_from(
        "hormone_geschlecht_fein",
        fallback=["Oestrogen", "Progesteron", "Testosteron", "LH", "FSH", "Zyklusachse"],
    ),
    "endokrin_remedies_multiplex": ["Endokrin - homoeopathische Mittel", "Endokrin - Spagyrik", "Endokrin - Adaptogene", "Endokrin - Schuessler Salze"],
    "hormon_remedies_multiplex": _labels_from(
        "hormone_remedies_multiplex",
        fallback=["Hormone - Komplexmittel", "Hormone - Adaptogene", "Hormone - Schuessler Salze", "Hormone - Phytotherapie"],
    ),
    "adaptogene_multiplex": ["Ashwagandha", "Rhodiola", "Eleuthero", "Schisandra", "Tulsi", "Reishi"],
    "mitochondrien_fein": _labels_from("mitochondrien", fallback=["Mitochondrien", "Atmungskette", "ATP Synthase", "Mitochondriale Membran", "Citratzyklus"]),
    "energie_stoffwechsel_fein": ["Citratzyklus", "Glykolyse", "Beta-Oxidation", "NADH", "FADH2", "Zellenergie"],
    "atp_produktion_fein": ["ATP Synthase", "ADP ATP Zyklus", "Oxidative Phosphorylierung", "Mitochondriale Protonenpumpe", "Magnesium ATP"],
    "oxidativer_stress_fein": ["ROS Balance", "Glutathion", "Superoxiddismutase", "Katalase", "Lipidperoxidation", "Nitrosativer Stress"],

    # Leber, Niere, Urogenital
    "leber_enzyme_fein": ["AST", "ALT", "Gamma-GT", "ALP", "Bilirubin", "Cytochrom P450"],
    "leber_pathologien_fein": ["Leberstau", "Fettleber Resonanz", "Cholestase Resonanz", "Leberentzündung Resonanz", "Fibrose Resonanz"],
    "niere_funktion_fein": ["Glomerulus Filtration", "Tubulus Rueckresorption", "Elektrolyt Balance", "Saeure-Basen-Regulation", "Renale Ausscheidung"],
    "niere_pathologien_fein": ["Nierenstau", "Nierenbecken Resonanz", "Glomerulaere Belastung", "Tubulusbelastung", "Kristallbelastung"],
    "blase_harnwege_fein": ["Harnblase", "Harnleiter", "Harnroehre", "Urothel", "Restharn Resonanz", "Harnwegsflora"],
    "prostata_fein": ["Prostata Gewebe", "Prostatasekret", "Beckenboden Prostata", "Androgenachse Prostata", "Prostata Stau"],
    "leber_remedies_multiplex": ["Leber - Mariendistel", "Leber - Chelidonium", "Leber - Schuessler Salze", "Leber - Entgiftungskomplex"],
    "niere_remedies_multiplex": ["Niere - Solidago", "Niere - Berberis", "Niere - Schuessler Salze", "Niere - Drainagekomplex"],
    "detox_remedies_multiplex": _labels_from(
        "entgiftung_remedies_multiplex",
        fallback=["Detox - Leber", "Detox - Niere", "Detox - Lymphe", "Detox - Darm", "Detox - Haut"],
    ),
    "zeolith_multiplex": ["Zeolith", "Klinoptilolith", "Mineralische Bindung", "Darmbindung", "Toxinbindung"],
    "chlorella_multiplex": ["Chlorella vulgaris", "Chlorella pyrenoidosa", "Algenbindung", "Chlorophyll Resonanz", "Mikroalgen Detox"],

    # Bewegungsapparat, Schmerz
    "bewegungsapparat_muskeln": _labels_from("muskulatur_fein", fallback=["Skelettmuskulatur", "Muskeltonus", "Myofaszien", "Triggerpunkte", "Muskelstoffwechsel"]),
    "bewegungsapparat_muskeln_fein": _labels_from("muskulatur_fein", fallback=["Muskelfaser", "Myofibrille", "Muskelspindel", "Sehnenansatz Muskel", "Muskelerholung"]),
    "bewegungsapparat_gelenke": _labels_from("knochen_gelenke", fallback=["Gelenk", "Knorpel", "Synovia", "Kapsel", "Gelenkspalt"]),
    "bewegungsapparat_gelenke_fein": _labels_from("knochen_gelenke_fein", fallback=["Synovialmembran", "Hyaliner Knorpel", "Gelenkkapsel", "Subchondraler Knochen", "Gelenkstoffwechsel"]),
    "bewegungsapparat_sehnen": ["Achillessehne", "Rotatorenmanschette", "Patellarsehne", "Sehnenansatz", "Sehnengleitgewebe", "Tendinopathie Resonanz"],
    "bewegungsapparat_baender": ["Kreuzbaender", "Aussenbaender", "Innenbaender", "Kapselbandapparat", "Bandstabilitaet", "Ligamentaere Spannung"],
    "schmerz_muskel": ["Myalgie", "Muskeltriggerpunkt", "Muskelkrampf", "Myofasziale Spannung", "Muskelentzündung Resonanz"],
    "schmerz_nerven_fein": ["Neuralgie", "Nervenwurzel Schmerz", "Polyneuropathie Resonanz", "Nozizeption", "Nervenreizleitung Schmerz"],
    "schmerz_chronisch_fein": ["Chronische Schmerzspur", "Zentrale Sensibilisierung", "Schmerzgedaechtnis", "Entzuendlicher Schmerz", "Belastungsschmerz"],
    "bewegung_remedies_multiplex": ["Bewegung - homoeopathische Mittel", "Bewegung - Schuessler Salze", "Bewegung - Mineralstoffe", "Bewegung - Spagyrik"],
    "schmerz_remedies_multiplex": ["Schmerz - homoeopathische Mittel", "Schmerz - Heel Komplexmittel", "Schmerz - Schuessler Salze", "Schmerz - Phytotherapie"],
    "mineralstoffe_multiplex": ["Magnesium", "Calcium", "Kalium", "Natrium", "Zink", "Mangan", "Silicium"],

    # Haut, Zaehne, Stoerfelder
    "haut_pathologien_fein": _labels_from("haut_detailliert_fein", fallback=["Dermatitis Resonanz", "Ekzem Resonanz", "Psoriasis Resonanz", "Akne Resonanz", "Hautbarriere"]),
    "haut_allergien_fein": _labels_from("allergie_haut_fein", fallback=["Kontaktallergie", "Urtikaria", "Mastzellhaut", "Pruritus", "Ekzem allergisch"]),
    "haut_remedies_multiplex": ["Haut - homoeopathische Mittel", "Haut - Schuessler Salze", "Haut - Spagyrik", "Haut - Pflanzenextrakte"],
    "zahn_herde_fein": _labels_from("zahnorgane_kiefer_herde", fallback=["Zahnherd", "Wurzelspitze", "Parodontaler Herd", "Kieferknochen Herd", "Fokale Belastung Zahn"]),
    "odontone_fein": _labels_from("odontone", fallback=["Odonton 11-18", "Odonton 21-28", "Odonton 31-38", "Odonton 41-48", "Zahn-Organ-Bezug"]),
    "tote_zaehne_fein": ["Devitaler Zahn", "Wurzelbehandelter Zahn", "Apikale Belastung", "Anaerobe Zahnflora", "Thioether Mercaptan Resonanz"],
    "zahn_meridiane_fein": ["Zahnmeridian Schneidezahn", "Zahnmeridian Eckzahn", "Zahnmeridian Praemolar", "Zahnmeridian Molar", "Zahn-Organ-Meridian"],
    "kiefergelenk_fein": _labels_from("zahnorgane_kiefergelenk", fallback=["Kiefergelenk", "Diskus articularis", "Masseter", "Temporalis", "Okklusion"]),
    "nico_fdok_fein": ["NICO Resonanz", "FDOK Resonanz", "Kieferostitis", "Knochenmark Belastung Kiefer", "Fettig-degenerative Kieferzone"],
    "kavitaeten_fein": ["Kavitaet Kiefer", "Extraktionsareal", "Knochenhohlraum", "Kieferknochen Drainage", "Chronischer Kieferherd"],
    "narben_stoerfelder_fein": ["Narbenfeld", "Operationsnarbe", "Impfnarbe", "Verbrennungsnarbe", "Faszienverklebung Narbe", "Narbendurchblutung"],
    "stoerfeld_remedies_multiplex": ["Stoerfeld - homoeopathische Mittel", "Stoerfeld - Narbenmittel", "Stoerfeld - Lymphdrainage", "Stoerfeld - Entgiftungskomplex"],

    # Toxine, Medikamente, Umwelt
    "pestizide_detailliert_fein": ["Organophosphate", "Glyphosat", "Pyrethroide", "Carbamate", "Fungizidrueckstaende", "Pestizid-Mix"],
    "herbizide_fein": ["Glyphosat", "Glufosinat", "2,4-D", "Dicamba", "Atrazin", "Herbizid Rueckstand"],
    "insektizide_fein": ["Pyrethroide", "Neonicotinoide", "Organophosphate", "Carbamate", "Permethrin", "Insektizid Rueckstand"],
    "medikamente_tox": ["Arzneimittelbelastung", "Metaboliten Belastung", "Lebermedikation", "Nierenmedikation", "Polypharmazie Resonanz"],
    "medikamente_detailliert_fein": ["Analgetika Belastung", "Antibiotika Belastung", "Antihistaminika Belastung", "PPI Belastung", "Statine Belastung", "Psychopharmaka Belastung"],
    "medikamente_nebenwirkungen_fein": ["Nebenwirkungsresonanz", "Mitochondriale Medikamentenlast", "Leberenzym Induktion", "QT-Belastung", "Darmflora Medikamentenlast"],
    "strahlung_remedies_multiplex": ["Strahlung - Schutzmittel", "Strahlung - homoeopathische Mittel", "Strahlung - Mineralien", "Strahlung - Antioxidantien"],

    # Infektion, Darm, Auto-Matcher
    "immun_remedies_multiplex": _labels_from(
        "immunstaerkung_remedies_multiplex",
        fallback=["Immun - Nosoden", "Immun - Isopathie", "Immun - Phytotherapie", "Immun - Frequenzmittel"],
    ),
    "probiotika_multiplex": ["Lactobacillus", "Bifidobacterium", "Saccharomyces boulardii", "Akkermansia", "Butyratbildner"],
    "enzyme_multiplex": ["Protease", "Lipase", "Amylase", "Laktase", "DAO", "Pankreasenzyme"],

    # Psyche, Miasmatik, Erbe
    "psyche_emotion_fein": _labels_from("psychosomatik_fein", "emotionale_blockaden_fein", fallback=["Emotionale Regulation", "Affektspannung", "Herzfeld Emotion", "Trauerresonanz", "Freuderesonanz"]),
    "psyche_stress_fein": ["Sympathikus Stress", "Cortisol Stress", "Vagus Bremse", "Stressgedaechtnis", "Erschoepfungsstress"],
    "psyche_trauma_fein": ["Traumaspeicher", "Schockresonanz", "Bindungstrauma", "Koerpererinnerung Trauma", "Freeze Reaktion"],
    "psyche_depression_fein": ["Antriebsfeld", "Melancholie Resonanz", "Serotonin Achse", "Dopamin Achse", "Lichtmangel Resonanz"],
    "psyche_angst_fein": ["Angstkreis", "Panikresonanz", "Amygdala Aktivierung", "Sicherheitsfeld", "Vegetative Alarmreaktion"],
    "miasma_psora": ["Psora Hautfeld", "Psora Reaktionslage", "Juckreiz Miasma", "Mangelreaktion Psora", "Chronische Reizlage Psora"],
    "miasma_sykose": ["Sykose Stau", "Warzenfeld", "Schleimhautstau", "Chronische Sekretion", "Proliferationsresonanz"],
    "miasma_syphilinie": ["Syphilinie Destruktion", "Ulzeration Resonanz", "Knochenresonanz Syphilinie", "Degenerationsmuster", "Nachtverschlimmerung"],
    "miasma_tuberkulinie": ["Tuberkulinie Wechselhaftigkeit", "Atemfeld Miasma", "Erschoepfung Tuberkulinie", "Wandernde Symptome", "Familienmuster Tuberkulinie"],
    "miasma_karzinogenie": ["Karzinogenie Reaktionslage", "Regulationsstarre", "Tiefe Erschoepfung", "Zellmilieu Resonanz", "Familienbelastung Karzinogenie"],
    "miasma_symptome_fein": _labels_from("miasmatik_fein", fallback=["Miasmatische Symptomlage", "Chronische Reaktionslage", "Familienmuster", "Konstitutionelle Belastung"]),
    "erbbelastungen_fein": ["Familiensystem Belastung", "Epigenetische Resonanz", "Transgenerationale Spur", "Konstitutionelle Erblast", "Ahnenfeld Belastung"],

    # Schwindel
    "schwindel_remedies_multiplex": ["Schwindel - homoeopathische Mittel", "Schwindel - Kreislaufmittel", "Schwindel - HWS Bezug", "Schwindel - Schuessler Salze"],
})

_DYNAMIC_GROUPS = [
    "homoeopathie_klassisch",
    "homoeopathie_klassisch_potenzen",
    "tcm_rezepturen",
    "tcm_rezepturen_potenzen",
    # Hersteller-spezifische Remedy-Gruppen (aus remedies.db geladen)
    "heel_remedies_multiplex",
    "nutramedix_remedies_multiplex",
    "schuessler_remedies_multiplex",
    # OOREP Homöopathie (2432 klassische Einzelmittel aus Open Online Repertory)
    "oorep_homeopathy_multiplex",
]

MIN_EXPECTED_GROUPS = 200
if len(_GROUP_LABELS) < MIN_EXPECTED_GROUPS:
    logger.warning(
        "Nur %s Gruppen geladen – erwartet ≥ %s. Prüfe Gruppen-Module!",
        len(_GROUP_LABELS),
        MIN_EXPECTED_GROUPS,
    )

PERSONAL_FAMILY_VECTORS: Dict[str, list[float]] = {
    "emotion": [1.0, 0.0, 0.0, 0.0],
    "physisch": [0.0, 1.0, 0.0, 0.0],
    "mental": [0.0, 0.0, 1.0, 0.0],
    "astral": [0.0, 0.0, 0.0, 1.0],
}

EXCLUDED_GROUPS = {
    "laser_protokolle",
    "rife_cafl_proc",
    "baklayan_proc",
    # neue klientenorientierte Felder sollen die alte Gruppenliste nicht verändern
    "emotion",
    "physisch",
    "mental",
    "astral",
    # Hinweis: bakterien_fein, viren_fein, parasiten_fein, pilze_fein
    # wurden entfernt, damit sie im pathogen-Profil nutzbar sind
}


def list_groups() -> List[str]:
    base = [g for g in _GROUP_LABELS.keys() if g not in EXCLUDED_GROUPS]
    dynamic = [g for g in _DYNAMIC_GROUPS if g not in EXCLUDED_GROUPS]
    
    # B.A.T. Gruppen hinzufügen
    bat_groups = []
    try:
        from .bat_groups import list_bat_groups
        bat_groups = list_bat_groups()
    except ImportError:
        pass
    
    return base + dynamic + bat_groups


def _base_offset_for_group(group: str) -> float:
    # leichte Verschiebung je Gruppe, um prozedurale Ratenfamilien zu trennen
    return {
        "kreislauf": 0.0,
        "chakren": 3.0,
        "meridiane": 6.0,
        "bakterien": 9.0,
        "viren": 12.0,
        "parasiten": 15.0,
        "pilze": 18.0,
        "schwermetalle": 21.0,
        # neue Gruppen, fortlaufende Offsets
        "endokrin": 24.0,
        "detox": 27.0,
        "mikrozirkulation": 30.0,
        "mitochondrien": 33.0,
        "entzuendung": 36.0,
        "allergene": 39.0,
        "mikronaehrstoffe": 42.0,
        "wirbelsaeule": 45.0,
        "odontone": 48.0,
        "schlaf": 51.0,
        # neue prozedurale Gruppen – fortlaufend ab 54
        "tcm_punkte": 54.0,
        "nebenchakren": 57.0,
        "spagyrik": 60.0,
        "laser_protokolle": 63.0,
        "farbtherapie": 66.0,
        "edelsteine": 69.0,
        "rife_cafl_proc": 72.0,
        "baklayan_proc": 75.0,
        "ps_freq": 96.0,
        "schwermetalle_tox": 97.0,
        "strahlung_tox": 98.0,
        "zahnorgane": 99.0,
        "extra_meridiane": 78.0,
        "chakren_erweitert": 81.0,
        "tcm_punkte_extended": 84.0,
        "tcm_full": 87.0,
        "chakren_full": 90.0,
        "emotion": 92.0,
        "physisch": 93.0,
        "mental": 94.0,
        "astral": 95.0,
    }.get(group, 0.0)


# Beschreibungen wichtiger Akupunkturpunkte (Auszug)
_TCM_DESC = {
    "LU1": "Zhongfu – Front-Mu Punkt der Lunge, lindert Husten & Brustschmerzen",
    "LI4": "Hegu – Yuan-Quellpunkt Dickdarm, Allgemeiner Schmerzpunkt",
    "ST36": "Zusanli – He-Meer Magen, stärkt Qi und Blut",
    "SP6": "Sanyinjiao – Treffpunkt 3 Yin-Beine, tonisiert Milz, Blut & Yin",
    "HT7": "Shenmen – Yuan Herz, beruhigt Geist",
    "PC6": "Neiguan – Luo Perikard, reguliert Herz, Übelkeit",
    "LV3": "Taichong – Yuan Leber, bewegt Leber-Qi",
    "GB20": "Fengchi – eliminiert Wind, klärt Sinne",
    "KI3": "Taixi – Yuan Niere, stärkt Niere Yin/Yang",
}


def generate_candidates_for_group(group: str, seed: str, k: int = 32) -> List[Dict]:
    # B.A.T. Gruppen behandeln
    if group.startswith('bat_'):
        try:
            from .bat_groups import get_bat_items
            bat_items = get_bat_items(group)
            if bat_items:
                out = []
                items_to_use = bat_items[:k] if k > 0 else bat_items
                for item in items_to_use:
                    # Generiere Rate basierend auf Frequenz
                    freq_val = item.get('value', 0)
                    rate = (freq_val / 10.0) % 100.0 if freq_val else _u01(f"{seed}|{group}|{item['label']}") * 100
                    out.append({
                        'label': item['label'],
                        'rates': [rate, (rate + 10) % 100],
                        'group': item.get('group', group),
                        'frequency': item.get('frequency', ''),
                        'harmonization': item.get('harmonization', ''),
                    })
                return out
        except ImportError:
            pass
        return []
    
    labels = _GROUP_LABELS.get(group)

    if group == "tcm_rezepturen" or group == "tcm_rezepturen_potenzen":
        formulas = _load_tcm_formulas()
        if not formulas:
            # Wenn tcm.txt nicht lesbar ist, lieber keine Kandidaten zurückgeben
            # als synthetische Platzhalter-Labels wie "tcm_rezepturen-itemX".
            return []
        base_off = _base_offset_for_group(group)
        out: List[Dict] = []
        if group == "tcm_rezepturen":
            total = k if k > 0 else len(formulas)
            if total <= 0:
                formulas = []
            for i in range(total):
                f = formulas[i % len(formulas)]
                label = f["label"]
                u0 = _u01(f"{seed}|{group}|{label}|n")
                u1 = _u01(f"{seed}|{group}|{label}|m")
                n = int(round(u0 * 72)) - 36
                m = int(round(u1 * 12)) - 6
                r1 = (_musical_rate(n) + base_off) % 100.0
                r2 = (_phi_rate(m) + base_off) % 100.0
                base = (r1 + r2) / 2.0
                off = int(round(_u01(f"{seed}|{group}|{label}|off") * 20))
                r_pair = [float(base % 100.0), float((base + off) % 100.0)]
                out.append({"label": label, "rates": r_pair, "description": f.get("description", "")})
            return out
        else:
            combos = []
            for f in formulas:
                name = f["label"]
                desc = f.get("description", "")
                for pot in _HOMEOPATHY_POTENCIES:
                    combos.append((f"{name} {pot}", desc, pot))
            if not combos:
                combos = []
            total = k if k > 0 else len(combos)
            if total <= 0:
                return []
            for i in range(total):
                label, desc, pot = combos[i % len(combos)]
                u0 = _u01(f"{seed}|{group}|{label}|n")
                u1 = _u01(f"{seed}|{group}|{label}|m")
                n = int(round(u0 * 72)) - 36
                m = int(round(u1 * 12)) - 6
                r1 = (_musical_rate(n) + base_off) % 100.0
                r2 = (_phi_rate(m) + base_off) % 100.0
                base = (r1 + r2) / 2.0
                off = int(round(_u01(f"{seed}|{group}|{label}|off") * 20))
                r_pair = [float(base % 100.0), float((base + off) % 100.0)]
                out.append({"label": label, "rates": r_pair, "description": desc, "potency": pot})
            return out
    if group == "tcm_full":
        counts = {
            "LU": 11, "LI": 20, "ST": 45, "SP": 21, "HT": 9, "SI": 19,
            "BL": 67, "KI": 27, "PC": 9, "TE": 23, "GB": 44, "LV": 14,
            "Ren": 24, "Du": 28,
        }
        labels = []
        for prefix, nmax in counts.items():
            for n in range(1, nmax + 1):
                labels.append(f"{prefix}{n}")
        if k <= 0:
            k = len(labels)
    elif group == "chakren_full":
        main = [
            ("Wurzelchakra", 194.18),
            ("Sakralchakra", 210.42),
            ("Solarplexus", 126.22),
            ("Herzchakra", 341.3),
            ("Kehlchakra", 384.0),
            ("Stirnchakra", 432.0),
            ("Kronenchakra", 963.0),
        ]
        ext = [
            "Thymuschakra", "Hara", "Handchakra links", "Handchakra rechts", "Fußchakra links", "Fußchakra rechts", "Milzchakra", "Nabelchakra",
        ]
        labels = [n for n, _ in main] + ext
        if k <= 0:
            k = len(labels)
    elif group == "ps_freq":
        # 0.00 – 100.00 Hertz in 0.1-Hertz-Schritten
        step = 0.1
        freqs = np.arange(0.0, 100.0 + 1e-9, step)
        labels = [f"{f:05.2f} Hertz" for f in freqs]
        k = len(labels)
        out = []
        for lab in labels:
            f = float(lab.split()[0])
            rate_val = float((f) % 100.0)
            out.append({"label": lab, "rates": [rate_val]})
        return out
    elif group == "schwermetalle_tox" or group == "strahlung_tox" or group == "zahnorgane":
        # einfache zweier-Raten pro Item (musical+phi versetzt)
        base_off = _base_offset_for_group(group)
        out = []
        for label in _GROUP_LABELS[group]:
            u0 = _u01(f"{seed}|{group}|{label}|n")
            u1 = _u01(f"{seed}|{group}|{label}|m")
            n = int(round(u0 * 72)) - 36
            m = int(round(u1 * 12)) - 6
            r1 = (_musical_rate(n) + base_off) % 100.0
            r2 = (_phi_rate(m) + base_off) % 100.0
            out.append({"label": label, "rates": [r1, r2]})
        return out

    if labels is None:
        file_labels = _load_group_labels_from_file(group)
        if file_labels is not None:
            labels = file_labels

    if labels is None and group.startswith("homoeopathie_"):
        base_labels = _load_remedy_labels_from_medica()
        if base_labels is not None:
            if group == "homoeopathie_klassisch":
                labels = base_labels
            elif group == "homoeopathie_klassisch_potenzen":
                expanded: List[str] = []
                for name in base_labels:
                    for pot in _HOMEOPATHY_POTENCIES:
                        expanded.append(f"{name} {pot}")
                labels = expanded

    # NEU: Lade Remedy-Labels aus der Datenbank für Hersteller-Multiplex-Gruppen
    if labels is None:
        db_category_map = {
            "heel_remedies_multiplex": "homotoxikologie_heel",
            "nutramedix_remedies_multiplex": "phytotherapie_nutramedix",
            "schuessler_remedies_multiplex": "Kohärente Harmonisierung mit Schüssler-Salzen",
            # OOREP Homöopathie - 2432 klassische Einzelmittel
            "oorep_homeopathy_multiplex": "oorep_homeopathy_multiplex",
        }
        if group in db_category_map:
            db_labels = _load_remedy_labels_from_db(db_category_map[group])
            if db_labels:
                labels = db_labels
                logger.info(f"Loaded {len(labels)} labels from DB for {group}")

    if not labels:
        # Verwende Platzhalter - Labels werden später mit Copen-Rate ergänzt
        # Dies markiert Items ohne echte semantische Labels
        labels = ["PROCEDURAL_ITEM"] * max(k, 200)
        logger.warning(f"Using procedural labels for group '{group}' - will add Copen-Rate info")
    base_off = _base_offset_for_group(group)

    out: List[Dict] = []
    for i in range(k):
        label = labels[i % len(labels)]
        if group == "chakren_full":
            freq_map = {
                "Wurzelchakra": 194.18,
                "Sakralchakra": 210.42,
                "Solarplexus": 126.22,
                "Herzchakra": 341.3,
                "Kehlchakra": 384.0,
                "Stirnchakra": 432.0,
                "Kronenchakra": 963.0,
            }
            if label in freq_map:
                r0 = _rate_from_freq(freq_map[label])
                r_pair = [float((r0) % 100.0), float((r0 + 7.0) % 100.0)]
            else:
                near = {
                    "Thymuschakra": "Herzchakra",
                    "Hara": "Sakralchakra",
                    "Handchakra links": "Herzchakra",
                    "Handchakra rechts": "Herzchakra",
                    "Fußchakra links": "Wurzelchakra",
                    "Fußchakra rechts": "Wurzelchakra",
                    "Milzchakra": "Solarplexus",
                    "Nabelchakra": "Solarplexus",
                }
                base_name = near.get(label, "Solarplexus")
                r0 = _rate_from_freq(freq_map[base_name])
                r_pair = [float((r0 + 3.0) % 100.0), float((r0 + 9.0) % 100.0)]
            out.append({"label": label, "rates": r_pair})
            continue
        if group == "tcm_full":
            mer = ""
            if label.startswith("Ren"):
                mer = "Ren"
            elif label.startswith("Du"):
                mer = "Du"
            else:
                mer = label[:2]
            mer_off = {
                "LU": 0.0, "LI": 0.5, "ST": 1.0, "SP": 1.5, "HT": 2.0, "SI": 2.5,
                "BL": 3.0, "KI": 3.5, "PC": 4.0, "TE": 4.5, "GB": 5.0, "LV": 5.5,
                "Ren": 6.0, "Du": 6.5,
            }.get(mer, 0.0)
            u0 = _u01(f"{seed}|{group}|{label}|n")
            u1 = _u01(f"{seed}|{group}|{label}|m")
            n = int(round(u0 * 72)) - 36
            m = int(round(u1 * 12)) - 6
            r1 = (_musical_rate(n) + base_off + mer_off) % 100.0
            r2 = (_phi_rate(m) + base_off + mer_off) % 100.0
            basev = (r1 + r2) / 2.0
            off = int(round(_u01(f"{seed}|{group}|{label}|off") * 20))
            r_pair = [float(basev % 100.0), float((basev + off) % 100.0)]
            desc = _TCM_DESC.get(label, "")
            out.append({"label": label, "rates": r_pair, "description": desc})
            continue
        u0 = _u01(f"{seed}|{group}|{label}|n")
        u1 = _u01(f"{seed}|{group}|{label}|m")
        n = int(round(u0 * 72)) - 36
        m = int(round(u1 * 12)) - 6
        r1 = (_musical_rate(n) + base_off) % 100.0
        r2 = (_phi_rate(m) + base_off) % 100.0
        base = (r1 + r2) / 2.0
        off = int(round(_u01(f"{seed}|{group}|{label}|off") * 20))
        r_pair = [float(base % 100.0), float((base + off) % 100.0)]
        
        # Erstelle aussagekräftiges Label für prozedurale Items
        if label == "PROCEDURAL_ITEM":
            # Berechne Copen-Rate aus den Raten
            avg_rate = (r_pair[0] + r_pair[1]) / 2.0
            copen_rate = int(avg_rate * 100000)  # Approximation
            copen_mhz = copen_rate / 1_000_000.0
            
            # Kategorisiere nach Gruppe
            if "psyche_stress" in group:
                category = "Stress-Resonanz"
            elif "psyche_depression" in group:
                category = "Depressions-Resonanz"
            elif "psyche_angst" in group:
                category = "Angst-Resonanz"
            elif "psyche_emotion" in group:
                category = "Emotions-Resonanz"
            elif "psyche_trauma" in group:
                category = "Trauma-Resonanz"
            elif "endokrin" in group:
                category = "Hormon-Resonanz"
            elif "nervensystem" in group:
                category = "Neuro-Resonanz"
            elif "nebenniere" in group:
                category = "Nebennieren-Resonanz"
            elif "schlafstoerungen" in group:
                category = "Schlaf-Resonanz"
            else:
                category = group.replace("_", " ").title() + "-Resonanz"
            
            label = f"{category} @ {copen_mhz:.2f}M"
        
        item = {"label": label, "rates": r_pair}
        pv = PERSONAL_FAMILY_VECTORS.get(group)
        if pv is not None:
            item["personal_vector"] = pv
        out.append(item)
    if not out:
        logger.warning("Gruppe '%s' hat 0 Kandidaten erzeugt", group)
    return out


def generate_fullbody_candidates(groups: List[str], seed: str, k_total: int = 64) -> List[Dict]:
    if not groups:
        groups = list(_GROUP_LABELS.keys())
    g_count = max(1, len(groups))
    per = max(1, k_total // g_count)
    remainder = max(0, k_total - per * g_count)
    all_items: List[Dict] = []
    for idx, g in enumerate(groups):
        extra = 1 if idx < remainder else 0
        items = generate_candidates_for_group(g, seed, k=per + extra)
        for it in items:
            d = dict(it)
            d["group"] = g
            all_items.append(d)
    return all_items[:k_total]

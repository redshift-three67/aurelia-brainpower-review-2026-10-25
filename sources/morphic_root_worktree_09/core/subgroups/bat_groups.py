"""
B.A.T. Akutprogramm Gruppen-Loader für Morphic Engine V1

Lädt die importierten B.A.T.-Gruppen und macht sie als System-Gruppen verfügbar.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional

# Pfad zu den importierten BAT-Gruppen
BAT_GROUPS_PATH = Path("data/generated_groups/BAT_Akutprogramme")

# Cache für geladene Gruppen
_BAT_GROUPS_CACHE: Dict[str, Dict] = {}


def list_bat_groups() -> List[str]:
    """Listet alle verfügbaren B.A.T.-Gruppen."""
    if not BAT_GROUPS_PATH.exists():
        return []
    
    groups = []
    for f in BAT_GROUPS_PATH.glob("*.json"):
        if not f.name.startswith("_"):  # Skip _index.json
            # Konvertiere Dateiname zu Gruppenname
            name = f.stem.lower()
            groups.append(f"bat_{name}")
    
    return sorted(groups)


def load_bat_group(group_name: str) -> Optional[Dict]:
    """
    Lädt eine B.A.T.-Gruppe.
    
    Args:
        group_name: Name der Gruppe (z.B. "bat_a01_bakterien_abwehr_organunspezifisch")
    
    Returns:
        Gruppen-Dict mit Items oder None
    """
    # Prüfe Cache
    if group_name in _BAT_GROUPS_CACHE:
        return _BAT_GROUPS_CACHE[group_name]
    
    if not BAT_GROUPS_PATH.exists():
        return None
    
    # Entferne "bat_" Präfix für Dateisuche
    search_name = group_name.replace("bat_", "", 1) if group_name.startswith("bat_") else group_name
    
    # Suche Datei (case-insensitive, auch mit Underscores)
    for f in BAT_GROUPS_PATH.glob("*.json"):
        file_stem_lower = f.stem.lower()
        # Direkter Match oder mit Underscores normalisiert
        if file_stem_lower == search_name.lower():
            try:
                with open(f, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    _BAT_GROUPS_CACHE[group_name] = data
                    return data
            except Exception:
                return None
        # Auch: A01_Bakterien... -> a01_bakterien...
        if file_stem_lower.replace(' ', '_').replace('-', '_') == search_name.lower().replace(' ', '_').replace('-', '_'):
            try:
                with open(f, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    _BAT_GROUPS_CACHE[group_name] = data
                    return data
            except Exception:
                return None
    
    return None


def get_bat_items(group_name: str) -> List[Dict]:
    """
    Gibt Items einer B.A.T.-Gruppe zurück im Morphic Engine Format.
    
    Returns:
        Liste von Items mit 'label', 'group', 'category', 'value'
    """
    data = load_bat_group(group_name)
    if not data:
        return []
    
    items = []
    group_display_name = data.get('name', group_name)
    
    for item in data.get('items', []):
        items.append({
            'label': item.get('multiplex_label', item.get('label', '')),
            'group': group_display_name,
            'category': 'bat_akut',
            'value': item.get('frequency_value', 0),
            'frequency': item.get('frequency', ''),
            'harmonization': item.get('harmonization_label', ''),
            'original_label': item.get('label', '')
        })
    
    return items


# Kategorie-Mappings für Profile
BAT_CATEGORY_GROUPS = {
    'bat_bakterien': [
        'bat_a01_bakterien_abwehr_organunspezifisch',
        'bat_a02_bakterien_abwehr_augen____bindehaut',
        'bat_a03_bakterien_abwehr_bindegewebe__gekapselt',
        'bat_a04_bakterien_abwehr_blinddarm',
        'bat_a05_bakterien_abwehr_borreliose',
        'bat_a06_bakterien_abwehr_geb_rmutter',
        'bat_a07_bakterien_abwehr_gerstenkorn',
        'bat_a08_bakterien_abwehr_harnleiter___nieren___blase',
        'bat_a09_bakterien_abwehr_herzkranzgef__e',
        'bat_a10_bakterien_abwehr_kehlkopf___stimmb_nder',
        'bat_a11_bakterien_abwehr_keuchhusten',
        'bat_a12_bakterien_abwehr_lunge',
        'bat_a13_bakterien_abwehr_magen___darmtrakt',
        'bat_a14_bakterien_abwehr_nase___rachen___bronchien',
        'bat_a15_bakterien_abwehr_nervensystem',
        'bat_a16_bakterien_abwehr_ohren',
        'bat_a17_bakterien_abwehr_z_hne___zahnhalteapparat',
    ],
    'bat_viren': [
        'bat_a21_viren_abwehr_organunspezifisch',
        'bat_a22_viren_abwehr_borna',
        'bat_a23_viren_abwehr_chikungunya',
        'bat_a24_viren_abwehr_hepatitis',
        'bat_a25_viren_abwehr_hpv_geb_rmutterhals',
        'bat_a26_viren_abwehr_kopf___muskulatur___bindegewebe',
        'bat_a27_viren_abwehr_lunge',
        'bat_a28_viren_abwehr_magen___darmtrakt',
        'bat_a29_viren_abwehr_mumps___masern',
        'bat_a30_viren_abwehr_nase___rachen___bronchien',
        'bat_a31_viren_abwehr_pankreas__diabetes_mellitus_',
        'bat_a32_viren_abwehr_perk',
        'bat_a33_viren_abwehr_psoriasis',
        'bat_a34_viren_abwehr_warzenbeseitigung',
        'bat_a35_viren_abwehr_fsme__dengue__gelbfieber',
        'bat_a36_viren_abwehr_r_teln___ringelr_teln',
    ],
    'bat_herpes': [
        'bat_a41_herpes_viren_abwehr_allgemein__magen___darm_',
        'bat_a42_herpes_viren_abwehr_augen____bindehaut',
        'bat_a43_herpes_viren_abwehr_genitalis',
        'bat_a44_herpes_viren_abwehr_g_rtelrose',
        'bat_a45_herpes_viren_abwehr_pfeiffersches_dr_senfieber',
        'bat_a46_herpes_viren_abwehr_windpocken',
        'bat_a47_herpes_viren_abwehr_zytomegalie',
    ],
    'bat_pilze': [
        'bat_a51_dermatophyten_abwehr_hautspezifisch',
        'bat_a52_dermatophyten_abwehr_nagelmykose',
        'bat_a53_dermatophyten_abwehr_unterleib',
        'bat_a54_hefepilz_abwehr_candida__darmtrakt_',
        'bat_a55_milben_abwehr__schwarze_milbe_',
    ],
    'bat_parasiten': [
        'bat_a56_parasiten_abwehr_darmtrakt',
        'bat_a57_parasiten_abwehr_harnleiter___blase',
        'bat_a58_parasiten_abwehr_leishmaniasen',
        'bat_a59_protozoen_abwehr__u_a__toxoplasmose_',
    ],
    'bat_verletzung': [
        'bat_a60_b_nderdehnung____riss',
        'bat_a61_bluterguss___prellung',
        'bat_a62_brustentz_ndung___milchstau',
        'bat_a63_mittelhirnsyndrom___gehirnersch_tterung',
        'bat_a64_gelenkkapselreizung____entz_ndung',
        'bat_a65_h_morrhoiden',
        'bat_a66_karpaltunnel_syndrom',
        'bat_a67_knochenbruch__akut___nachsorge',
        'bat_a68_kopfschmerzen___migr_ne',
        'bat_a69_leistenbruch__akut___op_nachsorge',
        'bat_a70_muskelzerrung____verh_rtung____verspannung',
        'bat_a71_neurodermitis',
        'bat_a72_wundheilung__innere____u_ere',
        'bat_a73_prostata_beschwerden',
        'bat_a74_schleimbeutelreizung____entz_ndung',
        'bat_a75_sehnenscheidenreizung____entz_ndung',
        'bat_a76_zahnbildung__babys___schulkinder_',
    ],
    'bat_spezial': [
        'bat_a77_toxische_belastungen___insektengifte',
        'bat_a78_schmerztherapie',
    ],
    'bat_regulation': [
        'bat_a80_vitalstoffe_gesamt__vitamine__mineralstoffe__s',
        'bat_a81_allergiel_schung',
        'bat_a82_energieversorgung',
        'bat_a83_gewebereinigung___entgiftung',
        'bat_a84_hb_werte_stabilisierung_und_blutqualit_t',
        'bat_a85_hormon_regulation__w_',
        'bat_a86_kreislaufregulation____stabilisierung',
        'bat_a87_psychosomatische_dysbalance___depressionen',
        'bat_a88_schlafregulation____f_rderung',
        'bat_a89_hormon_regulation__m_',
        'bat_a90_ausrichtung_der_polarit_ten_von_material',
        'bat_a91_raucherentw_hnung',
        'bat_a92_mikrozirkulation_blutgef__e',
        'bat_a93_leberreinigung',
    ],
}


def get_bat_profile_groups(profile_name: str) -> List[str]:
    """
    Gibt Gruppen für ein B.A.T.-Profil zurück.
    
    Args:
        profile_name: z.B. 'bat_bakterien', 'bat_viren', 'bat_akut' (alle)
    
    Returns:
        Liste von Gruppennamen
    """
    if profile_name == 'bat_akut':
        # Alle BAT-Gruppen
        all_groups = []
        for groups in BAT_CATEGORY_GROUPS.values():
            all_groups.extend(groups)
        return all_groups
    
    return BAT_CATEGORY_GROUPS.get(profile_name, [])


def is_bat_group(group_name: str) -> bool:
    """Prüft ob ein Gruppenname eine B.A.T.-Gruppe ist."""
    return group_name.startswith('bat_a') or group_name.startswith('bat_')

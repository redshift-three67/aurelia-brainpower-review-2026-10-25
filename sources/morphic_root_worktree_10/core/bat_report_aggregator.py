"""
B.A.T. Report Aggregator für Morphic Engine V1

Aggregiert BAT-Scan-Ergebnisse nach Subgruppen und ermittelt passende Remedies.
"""

from typing import Dict, List, Optional, Tuple
from collections import defaultdict


def beautify_bat_group_name(technical_name: str) -> str:
    """
    Wandelt technischen Gruppennamen in schönen Namen um.
    
    z.B. "bat_a47_herpes_viren_abwehr_zytomegalie" 
      -> "A47 - Herpes Viren-Abwehr Zytomegalie"
    """
    if not technical_name or not technical_name.startswith('bat_'):
        return technical_name
    
    # Entferne "bat_" Präfix
    name = technical_name[4:]  # z.B. "a47_herpes_viren_abwehr_zytomegalie"
    
    # === UMLAUT-REPARATUR ===
    # Korrigiere bekannte Encoding-Fehler aus PDF-Import
    umlaut_fixes = {
        'geb_rmutter': 'gebärmutter',
        'herzkranzgef__e': 'herzkranzgefäße',
        'stimmb_nder': 'stimmbänder',
        'z_hne': 'zähne',
        'r_teln': 'röteln',
        'ringelr_teln': 'ringelröteln',
        'g_rtelrose': 'gürtelrose',
        'dr_senfieber': 'drüsenfieber',
        'sch_dlinge': 'schädlinge',
        'polarit_ten': 'polaritäten',
        'augen____bindehaut': 'augen_bindehaut',
        'harnleiter___nieren___blase': 'harnleiter_nieren_blase',
        'kehlkopf___stimmb_nder': 'kehlkopf_stimmbänder',
        'magen___darmtrakt': 'magen_darmtrakt',
        'nase___rachen___bronchien': 'nase_rachen_bronchien',
        'kopf___muskulatur___bindegewebe': 'kopf_muskulatur_bindegewebe',
        'hpv_geb_rmutterhals': 'hpv_gebärmutterhals',
        'mumps___masern': 'mumps_masern',
        'pfeiffersches_dr_senfieber': 'pfeiffersches_drüsenfieber',
        '__': '_',  # Mehrfache Unterstriche zu einem
    }
    
    for broken, fixed in umlaut_fixes.items():
        name = name.replace(broken, fixed)
    
    # Extrahiere Code (A01, A47, etc.) - wird nicht mehr angezeigt
    parts = name.split('_', 1)
    if len(parts) < 2:
        return technical_name
    
    # code = parts[0].upper()  # "A47" - nicht mehr benötigt
    rest = parts[1]  # "herpes_viren_abwehr_zytomegalie"
    
    # Bereinige Rest: Underscores zu Leerzeichen, Title Case
    words = rest.replace('_', ' ').split()
    
    # Spezialwörter die Großgeschrieben bleiben
    keep_upper = {'hpv', 'fsme', 'mrsa', 'hla', 'ada', 'dna', 'rna', 'tcm'}
    
    formatted_words = []
    for word in words:
        if word.lower() in keep_upper:
            formatted_words.append(word.upper())
        else:
            formatted_words.append(word.capitalize())
    
    readable_name = ' '.join(formatted_words)
    
    # Ersetze doppelte Leerzeichen
    readable_name = ' '.join(readable_name.split())
    
    return readable_name


def aggregate_by_subgroup(
    scores: List[Dict],
    top_subgroups: int = 5,
    top_items_per_group: int = 3
) -> List[Dict]:
    """
    Aggregiert Scan-Ergebnisse nach Subgruppen.
    
    Args:
        scores: Liste der Score-Dicts (mit 'label', 'score', 'group', etc.)
        top_subgroups: Anzahl der Top-Subgruppen
        top_items_per_group: Anzahl der Top-Items pro Subgruppe
    
    Returns:
        Liste der aggregierten Subgruppen mit Top-Items
    """
    # Nach Gruppe aggregieren
    group_items: Dict[str, List[Dict]] = defaultdict(list)
    
    for entry in scores:
        group = entry.get('group', 'Unbekannt')
        if not group:
            group = 'Unbekannt'
        group_items[group].append(entry)
    
    # Pro Gruppe nach Score sortieren
    group_stats = []
    for group_name, items in group_items.items():
        sorted_items = sorted(items, key=lambda x: x.get('score', 0), reverse=True)
        top_items = sorted_items[:top_items_per_group]
        
        # Durchschnittlichen Score berechnen
        avg_score = sum(it.get('score', 0) for it in top_items) / len(top_items) if top_items else 0
        max_score = top_items[0].get('score', 0) if top_items else 0
        
        group_stats.append({
            'group_name': group_name,
            'avg_score': avg_score,
            'max_score': max_score,
            'item_count': len(items),
            'top_items': top_items,
        })
    
    # Nach durchschnittlichem Score sortieren
    group_stats.sort(key=lambda x: x['avg_score'], reverse=True)
    
    return group_stats[:top_subgroups]


# Remedy-Mapping für BAT-Kategorien
BAT_REMEDY_MAP = {
    # Bakterien
    'bakterien': [
        ('Echinacea D6', 'Immunstärkung'),
        ('Propolis C30', 'Antibakteriell'),
        ('Silicea D12', 'Gewebeunterstützung'),
    ],
    'borreliose': [
        ('Ledum C200', 'Klassisches Borreliose-Mittel'),
        ('Aurum arsenicum D30', 'Chronische Infektion'),
        ('Borrelia Nosode D30', 'Isopathie'),
    ],
    'streptokokken': [
        ('Streptococcinum D30', 'Nosode'),
        ('Belladonna C30', 'Akute Entzündung'),
        ('Hepar sulfuris D12', 'Eiterung'),
    ],
    
    # Viren
    'viren': [
        ('Oscillococcinum C200', 'Virale Infekte'),
        ('Influenzinum C30', 'Grippe-Prophylaxe'),
        ('Engystol N', 'Komplex-Immunmodulation'),
    ],
    'herpes': [
        ('Rhus toxicodendron C30', 'Bläschen, Brennen'),
        ('Natrium muriaticum C200', 'Konstitutionell'),
        ('Herpes simplex Nosode D30', 'Isopathie'),
    ],
    'hepatitis': [
        ('Chelidonium D6', 'Leberstützung'),
        ('Lycopodium C30', 'Leberfunktion'),
        ('Carduus marianus D6', 'Leberschutz'),
    ],
    
    # Pilze
    'pilze': [
        ('Candida albicans D30', 'Nosode'),
        ('Sulfur D12', 'Hautpilze'),
        ('Thuja C30', 'Mykosen'),
    ],
    'candida': [
        ('Candida albicans D30', 'Nosode'),
        ('Okoubaka D3', 'Darm-Dysbiose'),
        ('Borax D12', 'Mundpilz'),
    ],
    
    # Parasiten
    'parasiten': [
        ('Cina D30', 'Klassisches Wurmmittel'),
        ('Spigelia D12', 'Darmparasiten'),
        ('Filix mas D6', 'Bandwürmer'),
    ],
    
    # Akut/Verletzung
    'schmerz': [
        ('Arnica C200', 'Trauma, Verletzung'),
        ('Hypericum C30', 'Nervenschmerz'),
        ('Bryonia D12', 'Bewegungsschmerz'),
    ],
    'entzuendung': [
        ('Apis D12', 'Schwellung'),
        ('Belladonna C30', 'Akute Entzündung'),
        ('Mercurius D12', 'Eitriger Prozess'),
    ],
    'verletzung': [
        ('Arnica C200', 'Trauma'),
        ('Symphytum D6', 'Knochenbruch'),
        ('Calendula D6', 'Wundheilung'),
    ],
    
    # Regulation
    'entgiftung': [
        ('Nux vomica D12', 'Leberentlastung'),
        ('Berberis D6', 'Nierenausscheidung'),
        ('Lymphomyosot N', 'Lymphdrainage'),
    ],
    'hormone': [
        ('Sepia C30', 'Weibliche Hormone'),
        ('Agnus castus D6', 'Hormonstörungen'),
        ('Thyreoidinum D12', 'Schilddrüse'),
    ],
    'psyche': [
        ('Ignatia C30', 'Emotionale Belastung'),
        ('Phosphorus C30', 'Erschöpfung'),
        ('Aurum D30', 'Depression'),
    ],
    'schlaf': [
        ('Coffea C30', 'Schlaflosigkeit'),
        ('Passiflora D6', 'Unruhe'),
        ('Valeriana D6', 'Einschlafstörung'),
    ],
}


def find_remedies_for_group(group_name: str, max_remedies: int = 3) -> List[Tuple[str, str]]:
    """
    Findet passende Remedies für eine BAT-Gruppe.
    
    AUTOMATISCHE INTEGRATION via Remedy-Datenbank:
    - Nutzt Keyword-basierte Zuordnung
    - Neue Remedies werden automatisch erkannt
    - Keine Nacharbeit bei neuen Gruppen nötig
    
    Args:
        group_name: Name der Gruppe (z.B. "A05 - Bakterien-Abwehr Borreliose")
        max_remedies: Maximale Anzahl Remedies
    
    Returns:
        Liste von Tuples (Remedy-Name, Indikation)
    """
    # Verwende Remedy-Service für automatische Zuordnung
    try:
        from services.remedy_service import find_remedies_for_group as db_find_remedies
        
        remedies = db_find_remedies(group_name, max_remedies)
        
        if remedies:
            return remedies
    
    except ImportError:
        pass  # Fallback auf hardcoded Map
    except Exception as e:
        print(f"Warnung: Remedy-DB-Fehler: {e}")
    
    # Fallback: Hardcoded Map (für Kompatibilität)
    group_lower = group_name.lower()
    
    # Direktes Keyword-Matching
    for keyword, remedies in BAT_REMEDY_MAP.items():
        if keyword in group_lower:
            return remedies[:max_remedies]
    
    # Fallback: Allgemeine Kategorien
    if 'bakterien' in group_lower:
        return BAT_REMEDY_MAP['bakterien'][:max_remedies]
    elif 'viren' in group_lower:
        return BAT_REMEDY_MAP['viren'][:max_remedies]
    elif 'pilz' in group_lower or 'dermatophyt' in group_lower or 'hefepilz' in group_lower:
        return BAT_REMEDY_MAP['pilze'][:max_remedies]
    elif 'parasit' in group_lower or 'protozoen' in group_lower:
        return BAT_REMEDY_MAP['parasiten'][:max_remedies]
    elif 'herpes' in group_lower:
        return BAT_REMEDY_MAP['herpes'][:max_remedies]
    elif 'schmerz' in group_lower or 'migr' in group_lower:
        return BAT_REMEDY_MAP['schmerz'][:max_remedies]
    elif any(x in group_lower for x in ['prellung', 'bruch', 'dehnung', 'zerrung', 'wundheil']):
        return BAT_REMEDY_MAP['verletzung'][:max_remedies]
    elif any(x in group_lower for x in ['entgiftung', 'reinigung', 'leber']):
        return BAT_REMEDY_MAP['entgiftung'][:max_remedies]
    elif 'hormon' in group_lower:
        return BAT_REMEDY_MAP['hormone'][:max_remedies]
    elif 'psycho' in group_lower or 'depress' in group_lower:
        return BAT_REMEDY_MAP['psyche'][:max_remedies]
    elif 'schlaf' in group_lower:
        return BAT_REMEDY_MAP['schlaf'][:max_remedies]
    
    # Kein Match: Allgemeines Immun-Stützungs-Remedy
    return [
        ('Echinacea D6', 'Allgemeine Immunstärkung'),
        ('Lymphomyosot N', 'Lymphatische Unterstützung'),
    ][:max_remedies]


def format_subgroup_report(
    aggregated_groups: List[Dict],
    include_remedies: bool = True
) -> str:
    """
    Formatiert den Subgruppen-Report als Text.
    
    Args:
        aggregated_groups: Aggregierte Gruppenstatistiken
        include_remedies: Remedies einschließen
    
    Returns:
        Formatierter Report-String
    """
    lines = []
    lines.append("")
    lines.append("=" * 70)
    lines.append("B.A.T. SUBGRUPPEN-ANALYSE (Top 5)")
    lines.append("=" * 70)
    
    for i, group in enumerate(aggregated_groups, 1):
        group_name_raw = group['group_name']
        group_name = beautify_bat_group_name(group_name_raw)
        avg_score = group['avg_score']
        item_count = group['item_count']
        
        lines.append("")
        lines.append(f"#{i} {group_name}")
        lines.append(f"    Score: {avg_score:.4f} (Durchschnitt) | {item_count} Items")
        lines.append("")
        lines.append("    Top Items:")
        
        for item in group['top_items']:
            label = item.get('label', 'Unbekannt')
            score = item.get('score', 0)
            lines.append(f"      • {label}: {score:.4f}")
        
        if include_remedies:
            remedies = find_remedies_for_group(group_name_raw)
            if remedies:
                lines.append("")
                lines.append("    Empfohlene Remedies:")
                for remedy, desc in remedies:
                    lines.append(f"      💊 {remedy} – {desc}")
    
    lines.append("")
    lines.append("=" * 70)
    
    return "\n".join(lines)


def generate_subgroup_json(
    aggregated_groups: List[Dict],
    include_remedies: bool = True
) -> List[Dict]:
    """
    Generiert JSON-Struktur für Subgruppen.
    
    Returns:
        Liste von Subgruppen-Dicts für JSON-Export
    """
    result = []
    
    for group in aggregated_groups:
        group_name_raw = group['group_name']
        group_name = beautify_bat_group_name(group_name_raw)
        
        subgroup_data = {
            'name': group_name,
            'technical_name': group_name_raw,
            'avg_score': group['avg_score'],
            'max_score': group['max_score'],
            'item_count': group['item_count'],
            'top_items': [
                {
                    'label': it.get('label', ''),
                    'score': it.get('score', 0),
                    'frequency': it.get('frequency', ''),
                }
                for it in group['top_items']
            ],
        }
        
        if include_remedies:
            remedies = find_remedies_for_group(group_name_raw)
            subgroup_data['remedies'] = [
                {'name': r[0], 'indication': r[1]}
                for r in remedies
            ]
        
        result.append(subgroup_data)
    
    return result

"""
Label Converter - Konvertiert alte -item* Labels in neue aussagekräftige Labels
"""
import re


def convert_legacy_label(label: str, copen_rate: float = None) -> str:
    """
    Konvertiert alte -item* Labels in neue aussagekräftige Labels.
    
    Args:
        label: Altes Label (z.B. "psyche_stress_fein-item178")
        copen_rate: Optional die Copen-Rate für genauere Bezeichnung
        
    Returns:
        Neues aussagekräftiges Label
    """
    # Spezielle Behandlung für sehr kurze/unklare Abkürzungen
    if len(label) <= 4 and label.isupper():
        # Wahrscheinlich Abkürzung aus Datenbank (z.B. "tNL", "BL41", "ST25")
        if copen_rate and copen_rate > 0:
            copen_mhz = copen_rate / 1_000_000.0
            return f"{label} (Resonanz @ {copen_mhz:.2f}M)"
        else:
            return f"{label} (Spezifische Resonanz)"
    
    # Prüfe ob es ein -item* Label ist
    pattern = r"^(.+)[-_]item(\d+)$"
    match = re.match(pattern, label)
    
    if not match:
        # Kein -item Label, gib Original zurück
        return label
    
    group = match.group(1)
    item_num = match.group(2)
    
    # Kategorisiere nach Gruppe und erstelle aussagekräftige Namen
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
    elif "nervensystem" in group or "neurotransmitter" in group:
        category = "Neuro-Resonanz"
    elif "nebenniere" in group:
        category = "Nebennieren-Resonanz"
    elif "schlafstoerungen" in group or "schlaf" in group:
        category = "Schlaf-Resonanz"
    elif "dental" in group or "odontone" in group or "zahn" in group or "kiefergelenk" in group:
        category = "Dental-Resonanz"
    elif "nico" in group or "fdok" in group:
        category = "Kieferherd-Resonanz"
    elif "wirbel" in group or "vertebrae" in group or "hws" in group or "bws" in group or "lws" in group:
        category = "Wirbelsäulen-Resonanz"
    elif "organ" in group:
        category = "Organ-Resonanz"
    elif "immun" in group:
        category = "Immun-Resonanz"
    elif "verdauung" in group or "darm" in group:
        category = "Verdauungs-Resonanz"
    elif "toxin" in group or "vergiftung" in group:
        category = "Toxin-Resonanz"
    elif "pathogen" in group or "bakterien" in group or "viren" in group:
        category = "Pathogen-Resonanz"
    elif "allergie" in group:
        category = "Allergie-Resonanz"
    elif "meridian" in group:
        category = "Meridian-Resonanz"
    elif "chakra" in group or "chakren" in group:
        category = "Chakra-Resonanz"
    elif "bewegungsapparat_gelenke" in group:
        category = "Gelenk-Resonanz"
    elif "bewegungsapparat_muskeln" in group:
        category = "Muskel-Resonanz"
    elif "bewegungsapparat_knochen" in group:
        category = "Knochen-Resonanz"
    elif "bewegungsapparat" in group:
        category = "Bewegungsapparat-Resonanz"
    elif "haut_symptome" in group:
        category = "Hautsymptom-Resonanz"
    elif "haut" in group:
        category = "Haut-Resonanz"
    elif "fuß" in group or "fuss" in group:
        category = "Fuß-Resonanz"
    else:
        # Universeller Fallback
        category = group.replace("_", " ").title() + "-Resonanz"
    
    # Wenn Copen-Rate vorhanden, nutze sie für die Bezeichnung (IMMER bevorzugt!)
    if copen_rate and copen_rate > 0:
        copen_mhz = copen_rate / 1_000_000.0
        # Prüfe ob es ein _fein Item ist (prozedurell generiert)
        if "_fein" in group or "_multiplex" in group:
            # Zeige Frequenz + Spektralbereich für bessere Verständlichkeit
            if copen_mhz < 1.0:
                freq_desc = f"{copen_mhz*1000:.1f}k"
                band = "ULF"  # Ultra Low Frequency
            elif copen_mhz < 10.0:
                freq_desc = f"{copen_mhz:.2f}M"
                band = "HF"  # High Frequency
            elif copen_mhz < 100.0:
                freq_desc = f"{copen_mhz:.1f}M"
                band = "VHF"  # Very High Frequency
            else:
                freq_desc = f"{copen_mhz:.0f}M"
                band = "UHF"  # Ultra High Frequency
            
            return f"{category} {freq_desc} ({band})"
        else:
            # Normale Gruppen: Nur Frequenz
            return f"{category} @ {copen_mhz:.2f}M"
    else:
        # Fallback ohne Copen-Rate (sollte bei _fein Items nie vorkommen)
        if "_fein" in group or "_multiplex" in group:
            return f"{category} (Prozedurale Resonanz #{item_num})"
        else:
            return f"{category} #{item_num}"


def convert_scan_data_labels(scan_data: dict) -> dict:
    """
    Konvertiert alle Labels in Scan-Daten rekursiv.
    
    Args:
        scan_data: Dict mit Scan-Ergebnissen
        
    Returns:
        Modifiziertes Dict mit konvertierten Labels
    """
    if isinstance(scan_data, dict):
        for key, value in scan_data.items():
            if key == "label" and isinstance(value, str):
                # Hole Copen-Rate wenn verfügbar
                copen_rate = scan_data.get("copen_rate", None)
                scan_data[key] = convert_legacy_label(value, copen_rate)
            elif isinstance(value, (dict, list)):
                scan_data[key] = convert_scan_data_labels(value)
    elif isinstance(scan_data, list):
        scan_data = [convert_scan_data_labels(item) for item in scan_data]
    
    return scan_data

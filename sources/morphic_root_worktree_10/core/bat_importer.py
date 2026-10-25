"""
B.A.T. Akutprogramm Importer für Morphic Engine V1

Spezialisierter Importer für B.A.T.-Format PDFs.
Format-Konvertierung:
- "20,1 - Bakterien-Abwehr Strepto-/Enterokokken" 
  -> Label: "Streptokokken", Frequenz: "20.10 Hertz"
"""

import re
import json
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field

try:
    import fitz
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False


@dataclass
class BATItem:
    original_text: str
    label: str
    frequency_hz: str
    frequency_value: float
    multiplex_label: str
    harmonization_label: str
    category: str = "pathogen"


@dataclass
class BATGroup:
    code: str
    name: str
    full_name: str
    items: List[BATItem] = field(default_factory=list)
    category: str = "pathogen"


@dataclass
class BATImportResult:
    source_file: str
    imported_at: str
    main_group: str = "BAT Akutprogramme"
    subgroups: List[BATGroup] = field(default_factory=list)
    total_items: int = 0


LABEL_CLEANUP = [
    r'^Bakterien-Abwehr\s+',
    r'^Viren-Abwehr\s+',
    r'^Parasiten-Abwehr\s+',
    r'^Pilz-Abwehr\s+',
]


def extract_short_label(full_text: str) -> str:
    label = full_text.strip()
    for pattern in LABEL_CLEANUP:
        label = re.sub(pattern, '', label, flags=re.IGNORECASE)
    label = label.replace('Pseudo monas', 'Pseudomonas')
    if label.lower().startswith('strepto'):
        label = re.sub(r'^Strepto-?\s*/?\s*', '', label)
        if not label:
            label = 'Streptokokken'
    return label.strip()


def format_frequency(code: str) -> Tuple[str, float]:
    code_clean = code.replace(',', '.')
    try:
        value = float(code_clean)
    except ValueError:
        return (f"{code} Hertz", 0.0)
    
    if '.' in code_clean:
        parts = code_clean.split('.')
        decimals = parts[1] if len(parts) > 1 else '00'
        if len(decimals) == 1:
            decimals += '0'
        formatted = f"{parts[0]}.{decimals}"
    else:
        formatted = f"{int(value)}.00"
    
    return (f"{formatted} Hertz", value)


def import_bat_pdf(pdf_path: str) -> BATImportResult:
    if not PYMUPDF_AVAILABLE:
        raise ImportError("PyMuPDF nicht installiert")
    
    result = BATImportResult(
        source_file=pdf_path,
        imported_at=datetime.now().isoformat()
    )
    
    doc = fitz.open(pdf_path)
    current_group = None
    
    group_pattern = re.compile(r'^([A-Z]\d+)\s*[-–]\s*(.+)$')
    item_pattern = re.compile(r'^(\d+[,\.]?\d*)\s*[-–]\s*(.+)$')
    
    for page in doc:
        for line in page.get_text().split('\n'):
            line = line.strip()
            if not line or 'Stand:' in line or 'Seite' in line or 'Zusammensetzung' in line:
                continue
            
            group_match = group_pattern.match(line)
            if group_match:
                if current_group and current_group.items:
                    result.subgroups.append(current_group)
                current_group = BATGroup(
                    code=group_match.group(1),
                    name=group_match.group(2).strip(),
                    full_name=f"{group_match.group(1)} - {group_match.group(2).strip()}"
                )
                continue
            
            item_match = item_pattern.match(line)
            if item_match and current_group:
                freq_str, freq_val = format_frequency(item_match.group(1))
                short_label = extract_short_label(item_match.group(2))
                
                item = BATItem(
                    original_text=line,
                    label=short_label,
                    frequency_hz=freq_str,
                    frequency_value=freq_val,
                    multiplex_label=f"{short_label} mit {freq_str}",
                    harmonization_label=f"Kohaerente Harmonisierung {short_label} mit {freq_str}"
                )
                current_group.items.append(item)
                result.total_items += 1
    
    if current_group and current_group.items:
        result.subgroups.append(current_group)
    
    doc.close()
    return result


def export_to_morphic_groups(result: BATImportResult, output_folder: Path) -> List[Path]:
    bat_folder = Path(output_folder) / "BAT_Akutprogramme"
    bat_folder.mkdir(parents=True, exist_ok=True)
    created = []
    
    for group in result.subgroups:
        safe_name = re.sub(r'[^a-zA-Z0-9_]', '_', f"{group.code}_{group.name}")[:50]
        morphic_group = {
            'name': group.full_name,
            'code': group.code,
            'parent_group': result.main_group,
            'items': [
                {
                    'label': i.label,
                    'multiplex_label': i.multiplex_label,
                    'harmonization_label': i.harmonization_label,
                    'frequency': i.frequency_hz,
                    'frequency_value': i.frequency_value
                }
                for i in group.items
            ]
        }
        filepath = bat_folder / f"{safe_name}.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(morphic_group, f, indent=2, ensure_ascii=False)
        created.append(filepath)
    
    return created

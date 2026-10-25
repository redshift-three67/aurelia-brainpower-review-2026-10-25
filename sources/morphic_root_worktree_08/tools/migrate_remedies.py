"""
Remedy-Migrations-Skript

Migriert hardcoded Remedies aus bat_report_aggregator.py in die Remedy-Datenbank.
"""

import sys
from pathlib import Path

# Füge Parent-Verzeichnis zum Path hinzu
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.remedy_service import add_remedy, get_remedy_stats


# Remedy-Daten aus bat_report_aggregator.py
REMEDY_DATA = {
    # Bakterien
    'bakterien': [
        ('Echinacea D6', 'D6', 'bakterien', 'Immunstärkung', ['bakterien', 'immun', 'abwehr']),
        ('Propolis C30', 'C30', 'bakterien', 'Antibakteriell', ['bakterien', 'antibakteriell', 'propolis']),
        ('Silicea D12', 'D12', 'bakterien', 'Gewebeunterstützung', ['bakterien', 'gewebe', 'silicea']),
    ],
    'borreliose': [
        ('Ledum C200', 'C200', 'bakterien', 'Klassisches Borreliose-Mittel', ['borreliose', 'borrelia', 'zecken', 'ledum']),
        ('Aurum arsenicum D30', 'D30', 'bakterien', 'Chronische Infektion', ['borreliose', 'chronisch', 'aurum']),
        ('Borrelia Nosode D30', 'D30', 'bakterien', 'Isopathie', ['borreliose', 'borrelia', 'nosode']),
    ],
    'streptokokken': [
        ('Streptococcinum D30', 'D30', 'bakterien', 'Nosode', ['streptokokken', 'streptococcus', 'nosode']),
        ('Belladonna C30', 'C30', 'bakterien', 'Akute Entzündung', ['streptokokken', 'entzündung', 'akut', 'belladonna']),
        ('Hepar sulfuris D12', 'D12', 'bakterien', 'Eiterung', ['streptokokken', 'eiterung', 'hepar']),
    ],
    
    # Viren
    'viren': [
        ('Oscillococcinum C200', 'C200', 'viren', 'Virale Infekte', ['viren', 'virus', 'infekt', 'oscillococcinum']),
        ('Influenzinum C30', 'C30', 'viren', 'Grippe-Prophylaxe', ['viren', 'grippe', 'influenza', 'prophylaxe']),
        ('Engystol N', 'N', 'viren', 'Komplex-Immunmodulation', ['viren', 'immun', 'engystol']),
    ],
    'herpes': [
        ('Rhus toxicodendron C30', 'C30', 'viren', 'Bläschen, Brennen', ['herpes', 'bläschen', 'brennen', 'rhus']),
        ('Natrium muriaticum C200', 'C200', 'viren', 'Konstitutionell', ['herpes', 'konstitution', 'natrium']),
        ('Herpes simplex Nosode D30', 'D30', 'viren', 'Isopathie', ['herpes', 'simplex', 'nosode']),
    ],
    'hepatitis': [
        ('Chelidonium D6', 'D6', 'viren', 'Leberstützung', ['hepatitis', 'leber', 'chelidonium']),
        ('Lycopodium C30', 'C30', 'viren', 'Leberfunktion', ['hepatitis', 'leber', 'lycopodium']),
        ('Carduus marianus D6', 'D6', 'viren', 'Leberschutz', ['hepatitis', 'leber', 'carduus', 'mariendistel']),
    ],
    
    # Pilze
    'pilze': [
        ('Candida albicans D30', 'D30', 'pilze', 'Nosode', ['pilze', 'candida', 'nosode']),
        ('Sulfur D12', 'D12', 'pilze', 'Hautpilze', ['pilze', 'haut', 'dermatophyt', 'sulfur']),
        ('Thuja C30', 'C30', 'pilze', 'Mykosen', ['pilze', 'mykose', 'thuja']),
    ],
    'candida': [
        ('Candida albicans D30', 'D30', 'pilze', 'Nosode', ['candida', 'pilze', 'nosode']),
        ('Okoubaka D3', 'D3', 'pilze', 'Darm-Dysbiose', ['candida', 'darm', 'dysbiose', 'okoubaka']),
        ('Borax D12', 'D12', 'pilze', 'Mundpilz', ['candida', 'mund', 'borax']),
    ],
    
    # Parasiten
    'parasiten': [
        ('Cina D30', 'D30', 'parasiten', 'Klassisches Wurmmittel', ['parasiten', 'würmer', 'wurm', 'cina']),
        ('Spigelia D12', 'D12', 'parasiten', 'Darmparasiten', ['parasiten', 'darm', 'spigelia']),
        ('Filix mas D6', 'D6', 'parasiten', 'Bandwürmer', ['parasiten', 'bandwurm', 'filix']),
    ],
    
    # Akut/Verletzung
    'schmerz': [
        ('Arnica C200', 'C200', 'schmerz', 'Trauma, Verletzung', ['schmerz', 'trauma', 'verletzung', 'arnica']),
        ('Hypericum C30', 'C30', 'schmerz', 'Nervenschmerz', ['schmerz', 'nerv', 'hypericum']),
        ('Bryonia D12', 'D12', 'schmerz', 'Bewegungsschmerz', ['schmerz', 'bewegung', 'bryonia']),
    ],
    'entzuendung': [
        ('Apis D12', 'D12', 'verletzung', 'Schwellung', ['entzündung', 'schwellung', 'apis']),
        ('Belladonna C30', 'C30', 'verletzung', 'Akute Entzündung', ['entzündung', 'akut', 'belladonna']),
        ('Mercurius D12', 'D12', 'verletzung', 'Eitriger Prozess', ['entzündung', 'eiterung', 'mercurius']),
    ],
    'verletzung': [
        ('Arnica C200', 'C200', 'verletzung', 'Trauma', ['verletzung', 'trauma', 'prellung', 'arnica']),
        ('Symphytum D6', 'D6', 'verletzung', 'Knochenbruch', ['verletzung', 'knochen', 'bruch', 'symphytum']),
        ('Calendula D6', 'D6', 'verletzung', 'Wundheilung', ['verletzung', 'wunde', 'heilung', 'calendula']),
    ],
    
    # Regulation
    'entgiftung': [
        ('Nux vomica D12', 'D12', 'entgiftung', 'Leberentlastung', ['entgiftung', 'leber', 'nux', 'vomica']),
        ('Berberis D6', 'D6', 'entgiftung', 'Nierenausscheidung', ['entgiftung', 'niere', 'berberis']),
        ('Lymphomyosot N', 'N', 'entgiftung', 'Lymphdrainage', ['entgiftung', 'lymphe', 'lymphomyosot']),
    ],
    'hormone': [
        ('Sepia C30', 'C30', 'hormone', 'Weibliche Hormone', ['hormone', 'weiblich', 'sepia']),
        ('Agnus castus D6', 'D6', 'hormone', 'Hormonstörungen', ['hormone', 'agnus', 'castus', 'mönchspfeffer']),
        ('Thyreoidinum D12', 'D12', 'hormone', 'Schilddrüse', ['hormone', 'schilddrüse', 'thyreoidinum']),
    ],
    'psyche': [
        ('Ignatia C30', 'C30', 'psyche', 'Emotionale Belastung', ['psyche', 'emotion', 'stress', 'ignatia']),
        ('Phosphorus C30', 'C30', 'psyche', 'Erschöpfung', ['psyche', 'erschöpfung', 'phosphorus']),
        ('Aurum D30', 'D30', 'psyche', 'Depression', ['psyche', 'depression', 'aurum']),
    ],
    'schlaf': [
        ('Coffea C30', 'C30', 'psyche', 'Schlaflosigkeit', ['schlaf', 'schlaflosigkeit', 'coffea']),
        ('Passiflora D6', 'D6', 'psyche', 'Unruhe', ['schlaf', 'unruhe', 'passiflora']),
        ('Valeriana D6', 'D6', 'psyche', 'Einschlafstörung', ['schlaf', 'einschlafen', 'valeriana', 'baldrian']),
    ],
}


def migrate_all_remedies():
    """Migriert alle Remedies in die Datenbank."""
    
    print("=" * 70)
    print("REMEDY-MIGRATION")
    print("=" * 70)
    print("")
    
    # Zeige Statistiken vor Migration
    stats_before = get_remedy_stats()
    print(f"Vor Migration: {stats_before['total']} Remedies in DB")
    print("")
    
    # Migriere alle Kategorien
    total_added = 0
    
    for category, remedies in REMEDY_DATA.items():
        print(f"Kategorie: {category}")
        
        for remedy_data in remedies:
            name, potency, cat, indication, keywords = remedy_data
            
            try:
                remedy_id = add_remedy(
                    name=name,
                    potency=potency,
                    category=cat,
                    indication=indication,
                    keywords=keywords
                )
                
                print(f"  ✅ {name}")
                total_added += 1
            
            except Exception as e:
                print(f"  ❌ {name}: {e}")
        
        print("")
    
    # Zeige Statistiken nach Migration
    stats_after = get_remedy_stats()
    
    print("=" * 70)
    print("MIGRATION ABGESCHLOSSEN")
    print("=" * 70)
    print(f"Remedies hinzugefügt: {total_added}")
    print(f"Gesamt in DB: {stats_after['total']}")
    print("")
    
    if stats_after['by_category']:
        print("Nach Kategorie:")
        for cat, count in stats_after['by_category'].items():
            print(f"  {cat}: {count}")
    
    print("=" * 70)


if __name__ == "__main__":
    migrate_all_remedies()

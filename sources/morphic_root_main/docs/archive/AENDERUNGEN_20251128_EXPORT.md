# ÄNDERUNGEN: Vollständige Scan-Parameter im Export & HTML-Report

**Datum:** 28.11.2025  
**Backup:** `_backups\20251128_profile_fix\main.py.bak_20251128_export_fix`

---

## ✅ IMPLEMENTIERTE ÄNDERUNGEN

### 1. **JSON-Export erweitert** (`apps/cli/main.py`)

Folgende Parameter werden jetzt im JSON-Export gespeichert:

```json
{
  "profile": "gehirn_detailliert",
  "profile_groups_count": 71,
  "intention": "healing",
  "planet_type": "Mars",
  "focus_weighting": true,
  "personal_profile_values": {
    "emotion": 0.2,
    "physisch": 0.9,
    "mental": 0.3,
    "astral": 0.2
  },
  "entropy_mode": "enhanced",
  "use_hybrid_entropy": false
}
```

### 2. **HTML-Report erweitert**

Der HTML-Report zeigt jetzt ALLE Eingabeparameter:

```
Profil: gehirn_detailliert (71 Gruppen definiert)
Fokus: Gehirn, Nerven (Gewichtung aktiv)
Geburtsplanet: Mars | Intention: healing
Personalprofil: Emotion=0.20, Physisch=0.90, Mental=0.30, Astral=0.20
Entropie-Modus: enhanced
```

---

## 📊 NEUE FELDER IM EXPORT

| Feld | Typ | Beschreibung | Beispiel |
|------|-----|--------------|----------|
| `profile` | string | Profil-Name | "gehirn_detailliert" |
| `profile_groups_count` | int | Anzahl definierter Gruppen | 71 |
| `intention` | string/null | Gewählte Intention | "healing" |
| `planet_type` | string/null | Geburtsplanet | "Mars" |
| `focus_weighting` | boolean | Fokus-Gewichtung aktiv | true |
| `personal_profile_values` | object | Personalprofil-Werte | {"emotion": 0.2, "physisch": 0.9, ...} |
| `entropy_mode` | string | Entropie-Modus | "enhanced" oder "legacy" |
| `use_hybrid_entropy` | boolean | Hybrid-Entropy aktiv | false |

---

## 🎯 VORTEILE

1. **Vollständige Nachvollziehbarkeit** - Alle Eingaben sind dokumentiert
2. **Vergleichbarkeit** - Scans können später verglichen werden
3. **Reproduzierbarkeit** - Scans können mit gleichen Parametern wiederholt werden
4. **Transparenz** - Klient sieht alle verwendeten Parameter

---

## 🧪 TESTEN

```powershell
.\Run-MultiplexScan.ps1
```

Dann HTML-Datei öffnen und prüfen, ob alle Parameter angezeigt werden.

---

## 📝 GEÄNDERTE DATEIEN

- `apps/cli/main.py` (Zeilen 6610-6626, 2846-2888)

---

## ✅ STATUS

- [x] JSON-Export erweitert
- [x] HTML-Report erweitert
- [x] Alle Eingabeparameter dokumentiert
- [x] Backup erstellt
- [ ] Getestet (durch Nutzer)

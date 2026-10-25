# Kernel-ABI v1

Vorhandene radionische Prototypen werden **gewrapped**, nicht neu erfunden.

## Vertrag

| Feld | Bedeutung |
|---|---|
| `id` | Stabiler Name |
| `version` | SemVer |
| `hash` | SHA-256 des Artefakts; steht im Passport |
| `input_schema` / `output_schema` | JSON Schema |
| `class` | `cpu` \| `cuda` \| `quantum` |
| `repro` | `strict` \| `seeded` \| `stochastic` |
| `budget` | `vram_mb`, `cpu_ms_est`, `max_batch` |
| `entry` | Python-Modul oder WASM; keine versteckten Netzaufrufe |
| `copy` | Jeder menschenlesbare String durch CopyGuard, bevor UI/PDF |

## Kanonisches Sextett

Laufzeit Full: Radi144 → RadiWorks → RadiMorphic → RadiBlohm → RadiThoms → RadiCopen.
Migration: Morphic zuerst (`/opt/Prototypen/Radimorphic` @ `217dcf9`, read-only).
Nicht aus `/opt/radiquant4` kopieren.

## Regeln

- Alte Sitzungen bleiben über die damalige Kernel-Version interpretierbar.
- Was den Ausweis nicht erfüllen kann, bleibt Labor-Mandant.
- Praktiker-Kommentar ist Autorentext, nicht Modelloutput.
- Harmonisierung startet nur nach Promote aus der Zwischenablage (D18), nicht aus dem Rohscan.
- Kozyrev-DSP sind Kernel-IDs hinter derselben ABI. Katalog: [22-kozyrev-labor.md](22-kozyrev-labor.md).
  Gesetzt: `kozyrev.padic.haar.v1` (Default an), optional `kozyrev.reg.v1`, `p3/p5`, `lab.*`.
  Gesperrt: 3-Tier, Heilmittel, PPS-als-c2 — **keine** IDs.
- Jeder gesetzte Kozyrev-Eintrag hat einen administrativen Schalter (D23):
  Platform AND Mandant AND Sitzung, fehlendes Flag = aus, Audit.
  Admit prüft das Flag vor VRAM. UI fallbackt nicht.

## Labor vs. Produktion

Ein Labor-Mandant darf Prototypen ausführen, ohne Produktionsarchive zu
vermischen. Freigabe in Produktion ist ein Admin-Akt (Kernel-Registry).

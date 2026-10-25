# LLM-Handoff

## Vor dem ersten Diff

1. `AGENTS.project.md`
2. `docs/project-control/README.md`
3. `docs/STATUS.md`
4. `docs/superpowers/specs/2026-08-25-aurelia-ground-zero-server-design.md`
5. `docs/26-wiedervorlage.md`
6. `docs/20-freigabe.md`
7. `docs/10-decisions.md`

Schreibziel: **nur** `redshift-three67/aurelia`.

Die Phase-1-Schale einschließlich Authentifizierung, Datenbank und Mandantenbasis
ist technisch vorhanden. Verarbeitet werden ausschließlich synthetische Daten;
weitere Produktarbeit bleibt bis zum dokumentiert bestandenen `G0-SRV-12`
pausiert. Keine Klientenakten, kein CUDA, kein USB und kein Art.-9-Klartext.
Zielsystem ist Ubuntu Server 24.04.4 LTS amd64 plus minimales GNOME. Ältere
Betriebssystemprofile sind historisch und nicht ausführbar.

## Sofort stoppen bei

- `/opt/radiquant4` oder GitHub `redshift-three67/radiquant4` als Ziel
- Video und WebRTC sind vollständig ausgeschlossen (D10); Phase 9 nicht anlegen
- X-IDs implementieren oder still löschen
- Lovable-Supabase ausbauen
- Echte Klienten / Art.-9-Klartext in dieser Vorschau
- CopyGuard auf VRAM, 20 CUDA-Occupancies, MIG auf der Ada
- NVMe löschen oder reinstallieren, solange `G0-SRV-0` nicht als bestanden
  protokolliert ist
- lokale `source/`-Ordner externer Analysen nach GitHub oder an Reviewer geben

## Wiedervorlage nicht vergessen

WV01 Backup/Restore ab Ground Zero und erneut vor Art. 9 · WV02 Preise · WV03 Passkeys auf Ubuntu · WV06 Codecs.

## Wenn der Mensch „Phase 2“ sagt

Klienten, Einwilligungen, Zwischenablage. Vor dem ersten Art.-9: WV01.

# Phasenplan

Qualität vor Menge. Nächste Phase nur bei ehrlicher Abnahme der vorigen.

| Phase | Name | Inhalt | Abnahme |
|---|---|---|---|
| 0 | Konzept | Verfassung, C gesetzt, X-Katalog | **abgenommen** 2026-08-23/24 |
| G0-SRV | Server Ground Zero | Externes Backup/Restore, Ubuntu Server 24.04.4, RAID1/LUKS2/LVM, Härtung, isoliertes GNOME/Codex, NVIDIA-Baseline ohne CUDA | `G0-SRV-0` bis `G0-SRV-12` grün; **Vorbereitung läuft** |
| 1 | Gehäuse | Mandant, Rollen, Anmeldung, leere App-Schale | Isolationstest zwei Mandanten — **pausiert bis G0-SRV** |
| 2 | Praxisorganisation | Klienten, Gruppen, Dienste, Einwilligungen, Zwischenablage. **WV01 Backup-Ort vor erstem Art. 9.** | Art.-9-Einwilligungspfad |
| 3 | Kernel-ABI + Raten | Registry, gewrappte Prototypen im Labor | Schema + Hash |
| 4 | Analyse strikt | CPU-Referenz, dann CUDA-Scheduler, Passport | Replay-Test + Cross-Tenant-GPU-Test |
| 5 | Harmonisierung | Timerd, parallele Kanäle, Spur-Zustände | Tick-Lücke im Ausweis |
| 6 | Archiv / Trend / Report | Continuous Aggregates, PDF. **WV06 Codecs.** | Auskunft = derselbe Export |
| 7 | GPU-Härtung | VRAM-Allocator, Attestation, Queue-Policy | Kein Overcommit |
| 8 | Quantum opt-in | cuQuantum hinter ABI | Getrennter Modus |
| 9 | ~~WebRTC + Medien~~ | **Gestrichen (D10, O08: keine Videos).** | — |
| 10 | Betrieb | Abos scharf. **WV02 Preise. WV05 Mini-VPS nur auf Wunsch. WV03 Passkeys auf Ubuntu.** | Restore-Test |

X-Katalog akzeptiert 2026-08-24. Phase 1 Startwort 2026-08-24.

Ground Zero ersetzt keine Produktphase. Es ist ein vorgeschaltetes
Infrastruktur-Gate. AUDIT-02 und Phase 1 werden erst nach seiner dokumentierten
Abnahme fortgesetzt. Reale Klientendaten, CUDA und USB bleiben gesperrt.

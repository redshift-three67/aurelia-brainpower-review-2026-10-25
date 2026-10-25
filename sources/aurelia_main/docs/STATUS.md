# Status

```yaml
date: 2026-08-25
phase: 1
phase_name: Gehäuse
status: phase-1-paused-for-g0-server-ground-zero
infrastructure_gate: G0-SRV-GROUND-ZERO
auth: on
database: on
data_class: synthetic
github: redshift-three67/aurelia
hardware: GPU Server M G1
target_os: Ubuntu Server 24.04.4 LTS amd64 plus minimal GNOME
server_write_state: not-started
next_required_evidence: external-backup-and-restore-proof
x_katalog: akzeptiert
video: nein
```

## 24. August 2026

- X-Katalog akzeptiert (nicht umsetzbar / nicht relevant)
- O08 / D10: keine Videos, Phase 9 gestrichen
- Startwort Phase 1: Anmeldung, Mandant, Rolle — keine Klientenakten, keine CUDA, kein USB
- D08 gesetzt (Ubuntu-Passkeys; Vorschau E-Mail/Passwort)
- D12 gesetzt
- Wiedervorlage WV01–WV06 an den Phasen

## 25. August 2026

- Entwickleranalysen V1, V2 und V3 getrennt archiviert und verifiziert
- V3-Serverbefunde als Abnahmekriterien übernommen; kein unkritisches
  Zurückspielen der Altinstallation
- Betreiber bestätigte die acht Root-Passwortanmeldungen vom 19. und
  21. August als eigene autorisierte Einrichtungszugriffe
- Ground-Zero-Neuinstallation grundsätzlich freigegeben
- Zielsystem festgelegt: Ubuntu Server 24.04.4 LTS amd64, danach minimales
  GNOME/XWayland für einen isolierten Codex-Entwicklungsnutzer
- IPMI/BMC mit Remote-KVM und Virtual Media vom Betreiber bestätigt
- Anbieter-USV, separates Backupsystem und DDoS-Schutz bestätigt
- Noch keine Löschung oder Serveränderung; `G0-SRV-0` verlangt zuerst den
  dokumentierten Backup- und Restore-Nachweis
- Hardwarekorrektur: tatsächlich 2× 2 TB WD_BLACK SN850X; aktiver ECC-Schutz
  der vorhandenen 128 GB ist noch nicht bewiesen
- AUDIT-02 pausiert bis zur grünen Ground-Zero-Serverabnahme

## Gesetzt

C01–C12. X01–X20. D01–D08, D10, D12–D24. K1–K5. H1–H3.

## Wiedervorlage

WV01 Backup/Restore ab Ground Zero und erneut vor Art. 9 · WV02 Preise Betrieb · WV03 Passkeys auf Ubuntu · WV04 Lovable optional · WV05 H4 optional · WV06 Codecs Archiv

## Bewusst nicht in Phase 1

- CUDA-Demo, USB, echte Klienten, Art.-9-Klartext
- WebRTC / Video
- Lovable ausbauen
- `/opt/radiquant4` schreiben
- NVMe löschen, partitionieren oder reinstallieren, solange `G0-SRV-0` nicht
  ausdrücklich als bestanden protokolliert ist

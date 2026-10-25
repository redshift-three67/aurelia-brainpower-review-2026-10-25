# Sekundärer EFI-Boot bestätigt

Betreiber führte angekündigten Neustart aus und meldete Login/root. Lesende SSH-Prüfung20.09.2026 17:40:58UTC:

| Kriterium | Beobachtung |
|---|---|
| Neue Boot-ID | f58c59d4-41c2-48fd-8da1-24ac8085c808; vorher2d811cdf-f770-4fa0-bb3c-f6ec54666fed |
| Tatsächlicher Bootpfad | BootCurrent0004 Ubuntu-secondary, GPT20b45555-f9c3-4df1-ae39-e4e02a8fae2d; kein Fallback zu0000 |
| Bootreihenfolge | 0000,0004,0002,0003,0001 unverändert; BootNext nicht mehr vorhanden |
| RAID | md0/md1 beide [2/2][UU] |
| Verschlüsselte Datenpfade | md1 crypto_LUKS → LVM, Root/Home/Logs/Postgres/Aurelia/Build und Swap verfügbar |
| Management/Sicherheit | SSH/WireGuard/GDM/Firewall/AppArmor/auditd/chrony active; keine failedUnits; NTP synchron |
| Health nach Neustart |17:39:00UTC healthy=true/errors[]/failed_units[], beideRAIDdegraded0, SMARTpassed/keineMedienfehler; UnitResultsuccess/Exit0 |
| NVIDIA | Geladenes Kernelmodul580.173.02; anschließende Root-KVM-Abfrage per Betreiber-Screenshot bestätigt RTX4000SFFAdaGeneration, Treiber580.173.02, Speicherbelegung0MiB, display_activeDisabled. NVML als klaus999 bleibt verweigert; keine Rechteänderung. |

Health-Bericht lokal artifacts/health-postboot20-report.json, maschinell geprüft; SHA2560769c341923498f8393e132a9e161c230741a86bd9c5fafd67bca44704af733c.

Dass /boot/efi weiterhin nvme1n1p1 mountet, widerspricht BootCurrent0004 nicht: EFI-Startquelle und der spätere Linux-Mount sind getrennte Fakten. Der vorherige laufende Boot über0000 sowie der jetzige über0004 belegen beide EFI-Auswahlen bei vorhandenen beiden NVMe. Kein physischer Einzellaufwerksausfall, kein Virtual-Media-Recoveryboot und kein Headerrestore getestet. Für die Rückkehr zur normalen BootOrder ist kein weiterer Neustart erforderlich.

Durchgeführte kurze Root-KVM-Prüfung für Treiberbasis:
`nvidia-smi --query-gpu=name,driver_version,memory.used,display_active --format=csv,noheader`
Nur gelesen, keine Berechtigungs-/Treiber-/CUDA-Änderung. Root-Ausgabe vom Betreiber per Screenshot bild_10.JPG geliefert; kein separat exportierter maschineller NVML-Bericht. Version stimmt mit der zuvor per SSH gelesenen Kernelmodulversion überein. Root-NVML vor und nach Neustart sowie aktuell keine gemeldete VRAM-Belegung/Displayaktivität belegt. Kein CUDA-Toolkit-/Kernel-/Lastnachweis und keine zukünftige Belegungsgarantie. Die unprivilegierte NVML-Verweigerung ist kein Defektbeweis. Keine weitere Eingabe oder Wiederholung für diesen Teilnachweis nötig; keine Gesamt-G0-Freigabe daraus.

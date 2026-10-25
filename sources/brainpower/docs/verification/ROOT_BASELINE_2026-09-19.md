# Lesende Root-Baseline ausgewertet

Quelle: `/var/tmp/aurelia-baseline-fbebe9d10e294179b7660eb762069d76.json`, Beobachtungszeit 19.09.2026 19:45:50 UTC. Durch Betreiber in Root-KVM ausgeführt, anschließend vollständig per SSH gelesen. Keine Konfigurationsänderung. Alle 16 erfassten Befehle Rückgabecode 0; dies bedeutet erfolgreiche Beobachtung, nicht Bestehen aller Sicherheitskriterien.

| Prüfung | Beleg | Grenze |
|---|---|---|
| SSH | Syntax gültig; Defaults und fester WG-Admin-Kontext: Rootlogin, Passwort, KbdInteractive, leere Passwörter und X11 aus; Publickey an | Nicht alle denkbaren Match-Kontexte geprüft |
| sudo | Syntax gültig; klaus999 hat ALL-Kommandomarker, keinen NOPASSWD-Marker; aurelia-dev keine Kommandomarker | Begrenzte Auswertung von sudo -ll, kein vollständiger Berechtigungsbeweis aller Identitäten |
| Firewall | Aktive Basischains input/forward drop, output accept; explizite Portfreigaben 22 und 51820 ohne weitere Bedingungen; DHCP-Regeln bedingt | Kein externer Erreichbarkeitstest; IP-unabhängiges SSH bleibt bestehender Betreiberentscheid, Abweichung vom alten VPN-only-Design |
| LUKS | cryptsetup isLuks --type luks2 /dev/md1 erfolgreich | Kein Recoverykey-/Header- oder Ausfalltest |
| Secure Boot | disabled, Setup Mode | Zielkriterium nicht erfüllt; Änderung braucht vorbereiteten Recoverypfad |
| EFI | Fünf Einträge, zwei mit Ubuntu-Bezeichnung | Anzahl beweist nicht Bootfähigkeit beider NVMe |
| RAM | DMI meldet Error Correction Type: None | Aktives ECC nicht belegt; keine belastbare Hardware-/Beschaffungsentscheidung aus DMI allein |
| GPU | Root-NVML-Abfrage erfolgreich: RTX 4000 SFF Ada, Treiber 580.173.02, 20475 MiB gesamt, 0 MiB genutzt, display_active Disabled | Momentaufnahme; kein CUDA-Toolkit-/Kerneltest, kein umfassender GPU-Lasttest. Frühere Permission-Meldung als klaus999 kein NVML-Defekt |
| dev-Zugriff | Negative Tests auf shadow, bekannten Backupkey und /srv/aurelia erfolgreich | Einzelpfade; kein vollständiger Isolationstest der gesamten Entwicklungsumgebung |

Nächste Priorität: Recovery-Nachweise und Iststandentscheidungen konkretisieren, dann Schnittstellenvertrag. Keine pauschale G0-Freigabe, kein Einschalten von Secure Boot, keine Firewalländerung, kein CUDA-Toolkit und keine Produktübertragung aus diesem Ergebnis ableiten.

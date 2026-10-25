# Aurelia REST-Integrationsprofil – Entscheidungsvorschlag

Status: Vertragsrichtung am 19.09.2026 vom Betreiber angenommen; technische Ausgestaltung bleibt Entwurf, nicht implementiert oder kanonisch übernommen. Ergänzt die bestehende Kernel-ABI; ersetzt keine Freigaben. Keine Produktdateien verändert, keine Modellübertragung oder Netzwerkabfrage an einen Modulserver.

## Entscheidung und Alternativen

Empfohlen: ein explizites, versioniertes REST-Integrationsprofil neben dem bestehenden Python-/WASM-Profil. Aurelias zentrale Zulassungsprüfung bleibt für beide verbindlich. Der Transport wird aus einem freigegebenen Profil bestimmt, niemals aus beliebigen Manifest-URLs oder einem stillen Fallback.

Alternativen: (1) REST-Prototypen auf direkten Python-entry umbauen; dafür wären neue Kompatibilitäts- und Regressionstests nötig. (2) REST stillschweigend als bestehende ABI behandeln; verworfen, weil Aufruf- und Sicherheitsannahmen unklar blieben. Die empfohlene Ergänzung wahrt bestehende Aufrufwege und macht Abweichungen prüfbar.

## Vorhandener Stand und vorgeschlagene Regeln

| Thema | Quellenbefund | Vorgeschlagene verbindliche Regel |
|---|---|---|
| Profilwahl | Aurelia ABI nennt Python/WASM-entry; Modulvertrag verlangt REST v1, entry deprecated | Registry führt explizit gewähltes Transportprofil. REST nutzt abi_surface=rest, abi_version=v1 und freigegebene operations. Keine Auflösung oder Ausführung des veralteten entry im REST-Profil. Python/WASM bleibt separat bestehen. |
| Manifest | RadiWorks manifest.py enthält input_schema, output_schema, copy, Hash, Budget, Operations | Pflichtfelder und operationseigene Schemas gegen freigegebene Vertragsrevision prüfen. Fehlende/inkonsistente Felder sperren die Aufnahme. Beispiele in Markdown sind keine Laufzeitmanifeste. |
| Zielbindung | apiBase ist konfigurierbar | Nur administrativ konfigurierte interne Modulziele; Manifest darf keine Zieladresse bestimmen. Keine automatischen Redirects oder fremden Schema-Downloads. Zieländerungen benötigen erneute Prüfung. |
| Artefaktidentität | Aktueller Hash umfasst Python-Quellen | Hash weiterhin exakt nach dokumentiertem Verfahren prüfen. Separater Releasebeleg bindet Abhängigkeiten, Konfiguration und weitere laufzeitrelevante Artefakte; Codehash nicht als vollständiger Deploymentnachweis darstellen. Drift sperrt Ausführung bis erneute Prüfung/Freigabe. |
| Berechtigung | Lokaler Prototyp ohne Auth; tenant_id/client_id nullable | Produktive Identität kommt aus geprüfter Aurelia-Sitzung/Dienstidentität. Clientwerte sind nicht vertrauenswürdig. Mandantenbindung muss für Lesen, Schreiben, Drafts, WebSocket, Cache und Hintergrundjobs gelten. Fehlender/widersprüchlicher Scope wird abgewiesen. Nullable Altprototyp bleibt ausschließlich in getrenntem synthetischem Labor. |
| Servicezugriff | Same-Site-Einbettung vorgesehen | Same-Site/CORS ersetzt keine Authentifizierung. Modulzugriff über kontrollierte Dienstidentität; direkte öffentliche Umgehung der Plattformprüfung verhindern. Konkretes Transportauth-Verfahren vor Implementierung festlegen und testen. |
| Ergebnisse | Passport v2 enthält kernel_hash, input_hash, seed und signatur_status=unsigned | Quelle und Version explizit erhalten. unsigned niemals als kryptografisch signiert oder attestiert anzeigen. Späterer Signaturvertrag ist getrennte Entscheidung; Vertrauensniveau muss zur jeweiligen freigegebenen Nutzung passen. |
| Nebenwirkungen | D18 sieht Draft → Review → Ready → Promote vor | Analyse darf keine Harmonisierung/Hardware starten. Promote nur mit aktueller Berechtigung, CopyGuard und erforderlichem Step-up. D18 ist als „zur Bestätigung“ markiert: Übergänge und Auth-Anforderungen ausdrücklich abstimmen. |
| WebSocket | Bootkennung, Event-ID und Replay-Gap bereits dokumentiert | Autorisierung beim Verbindungsaufbau und Ereignisabruf, Mandantentrennung, Reconnect/Replay-Gap testen; bei Lücken Zustand autorisiert neu laden. Keine Annahme vollständiger Zustellung allein aus Event-ID. |
| Fehler/Wiederholung | Einheitliches Fehlerobjekt beschrieben | Timeout, Abbruch und unbekanntes Ergebnis getrennt behandeln. Mutierende Befehle nicht automatisch wiederholen; erst nach definierter serverseitiger Idempotenz. Request-/Antwortgrößen, Fristen und Parallelität vor Laufzeittests pro Profil begrenzen. |
| Ressourcen/Hardware | Budget vorhanden; RadiWorks CPU, isHardwareActivatable=false | Budget zentral erzwingen; Manifestwerte allein sind keine Durchsetzung. Kein CUDA-/Emitter-/USB-GO durch REST-Zulassung. |
| Freigabe | S4 nicht zertifiziert, S5 offen | Vertragsannahme, bestandene Tests, S4-Bewertung, Registryaufnahme und Produktionsfreigabe sind getrennte Nachweise. Keine automatische Modulwahl. |

## Abnahme vor erster Integration

1. Gültiges Manifest annehmen; unbekannte Version, fehlendes Schema, unzulässiges Ziel oder Hashdrift verlässlich sperren.
2. Synthetischen positiven Analysepfad mit geprüftem Request/Response, Passport und Draft auf Ubuntu wiederholbar testen.
3. Unangemeldeten, fehlenden oder fremden Mandantenscope auch bei Ergebnisabruf, Drafts, WebSockets und Hintergrundjobs abweisen. Keine Tests mit realen Klientendaten.
4. CopyGuard-Block, unzulässiges Promote, fehlendes Step-up, doppelte Kommandos, Timeout und Replay-Gap prüfen; keine ungewollte Nebenwirkung.
5. Versions-/Artefaktbindung, Dienststart, begrenzte Ressourcen, isolierte Rücknahme und Betriebsanleitung belegen. Separate Recovery-/Infrastrukturgates bleiben erhalten.

Keine Tests dieses neuen Profils ausgeführt: dies ist die Spezifikation ihrer späteren Abnahme. Transportauth-Verfahren, Registry-Vertragsrevision und numerische Limits sind im [technischen Zusatz](AURELIA_REST_PROFIL_DETAILS_2026-09-19.md) konkret vorgeschlagen. Diese Details sind keine aktivierten Defaults.

## Umfang der angefragten Entscheidung

Zustimmung bedeutet ausschließlich: REST als separates versioniertes Integrationsprofil unter den beschriebenen Grenzen weiter konkretisieren. Sie ist kein Implementierungs-GO für externe Produktrepositories, keine Registryfreigabe, keine Auswahl von RadiWorks als Erstmodul und kein Produktions-/CUDA-/Hardware-GO.

## Quellenbindung

- Aurelia/docs/06-kernel-abi.md und Modul_Templates/standards/API_CONTRACT.md: Hashes im Wiederaufnahmebericht vom 19.09.
- Radiworks/radiworks_port/engine/src/radiworks/manifest.py: SHA256 2107016ecfb77cada017e428a22ff12bda785b2df8fbe92eb49a1efa2adfa00a.
- Aurelia/docs/07-identity.md: SHA256 f6668318b2de4a2212a45ea29f6075390fb07029347e4a7b563a9b42fc0fe2f5.
- Aurelia/docs/18-clipboard.md: SHA256 c78653cd5b4b743a900d58f440ed45c7dea29e0570b5e8b87976be3f2fe03c5c.

Quellen lesend geprüft. Manifestquellcode wurde nicht importiert oder ausgeführt; daraus folgt noch kein HTTP-/Linux-Laufzeitnachweis.

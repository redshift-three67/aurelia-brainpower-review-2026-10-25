# Hermes-Route B als zuschaltbare Variante

> Umsetzung des ausdrücklich gewählten Designs. Die neue Route ist ein eigener, manuell gestarteter Beratungs- und Planungsweg. Sie ersetzt keine bestehende Terra-/Supervisor-Konfiguration und schaltet keine automatischen Reviews ein.

**Ziel:** Umfangsbezogener Review und Matrixplan mit Sol 6/xhigh als Leiter, Luna 6/max als unabhängig begrenztem Prüfer und Astra 6/medium bei erkannten kritischen Entscheidungen, wesentlichen Widersprüchen oder expliziter Betreiberwahl. Kandidaten bleiben an frische Quellen und bestehende Planfreigaben gebunden.

**Grenzen:** Keine Produktdateiänderung, kein neues Projekt-GO, kein Serverzugriff. Vorhandene Aufträge/Jobs behalten ihr altes Routing. Die automatische Eskalation verwendet strukturierte Risikosignale von Sol und Luna; sie ist kein vollständiger Sicherheitsdetektor. Kritische Prüfungen können ausdrücklich erzwungen werden. Keine 10-%-Obergrenze.

- [x] B-Routingvertrag mit exakt erlaubten Modell/Effort-Paaren und eigenem Snapshot ergänzen; Altvertrag unverändert halten.
- [x] Isolierte B-Funktion für Review und deskriptiven Matrixplan mit striktem Schema, unabhängigem Luna-Review und bedingtem Astra-Review implementieren. Unsichere oder fehlgeschlagene Berichte blockieren; kein Fallback.
- [x] Neue Aktionen nur für ausdrücklich gewählte Projekt-/Gruppenumfänge mit bestehenden Versandfreigaben, Frischeprüfung, Tokenbelegen und optionalem Betreiberflag verbinden.
- [x] Neue UI-Aktionen und optionale Astra-Anforderung ergänzen; laufende Altwege nicht umstellen.
- [x] Negative Sicherheits-/Drift- und positive Transporttests, alte Routing-/Hermes-Regression, JS-/UI-Prüfung und Dokumentation durchführen. Echte Modellqualität und umfassende Produktabnahme bleiben getrennte Nachweise.

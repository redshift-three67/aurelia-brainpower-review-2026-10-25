# RadiWorks GV-Verlauf: Sitzungsbindung — Umsetzungsplan

**Ziel:** Im isolierten Kandidaten erhalten geeignete freigegebene Draft-Raten einen unveränderlichen, serverseitig geprüften Fall-/Sitzungsbezug bis zu Queue- und Resonanzereignissen.

**Architektur:** Ein reiner Validator bindet ausschließlich eine eindeutig gespeicherte Sitzung an ihren Draft, Revision, vollständigen Analysehash und ursprünglichen Ratenindex. Der vorhandene prozessgebundene HMAC-Fallverweis vermeidet zusätzliche rohe Fallnamen. Fehlende oder veraltete Bindungen schließen nur die spätere GV-Beobachtung aus; die bestätigten Broadcast-Wege bleiben erhalten. Keine Timer oder zusätzlichen Entropieziehungen in diesem Schritt.

**Technik:** Bestehende Python-/FastAPI-Engine, gefrorene Dataclass, SHA-256 und Pytest. Kandidat: `runtime/rw-gv-binding-20261003`; keine Änderungen an Dauerinstanzen 8103–8109 oder der produktiven RadiWorks-Quelle.

## Schritte

- [x] Aktuelle Quelle einschließlich Tests/Webapp hashgeprüft in den Kandidaten kopieren; `BASELINE.json` festhalten.
- [x] Luna: `core/observation_binding.py` und `tests/test_observation_binding.py`. Rote Tests für Scope, fehlende/mehrdeutige Sitzung, Revision, Draft-ID, Payload und doppelte Ratenbezeichnungen; dann minimaler unveränderlicher Validator.
- [x] Sol: `tests/test_broadcast_observation_binding.py` zuerst. Erwartung: Bindung entspricht originalem Ratenindex trotz Sortierung; Fallwechsel/veraltete Sitzung erhalten Broadcast-Funktion ohne Bindung; direkte und Auto-Wege erhalten keine erfundene Bindung; Queue-Batch verwirft fehlerhafte Metadaten vor Teilannahme.
- [x] Sol: `core/draft.py` verwendet beim Sortieren `(original_index, rate)`; optionale Bindungen gelangen nur bei passendem Draft-/Analysehash in Entries. `api/routes.py` prüft den gespeicherten Fall unter bestehender Stick-Pad-Transaktions-/Promotionssperre. `core/broadcast.py` trägt eine validierte gefrorene Bindung in Elementen, Queue, Fortschritts- und Resonanzereignissen weiter.
- [x] Zieltests ausführen, danach vollständige Kandidaten-Engine-Suite. Testdaten bleiben synthetisch; keine neue Datenbank oder realen Falldaten versenden.
- [x] Astra/medium prüft die Scope-/Nebenwirkungsgrenze unabhängig. Fundstellen korrigieren und betroffene Tests wiederholen.
- [x] Quell-/Kandidaten-Diff und unveränderte Dauerinstanzen prüfen; Nachweis und Fortsetzung aktualisieren. Keine Übernahme in laufende Engines in diesem Block.

## Prüfbefehle

Mit vorhandener RadiWorks-venv, `PYTHONDONTWRITEBYTECODE=1` und `PYTHONPATH` auf den Kandidaten:

```powershell
python -m pytest runtime/rw-gv-binding-20261003/engine/tests/test_observation_binding.py runtime/rw-gv-binding-20261003/engine/tests/test_broadcast_observation_binding.py -q -p no:cacheprovider --basetemp runtime/pytest-gv-binding-targeted
python -m pytest runtime/rw-gv-binding-20261003/engine/tests -q -p no:cacheprovider --basetemp runtime/pytest-gv-binding-full
```

Vor Implementierung müssen die neuen Verhaltenstests wegen fehlender Bindung scheitern; nach Implementierung müssen sie und die vorhandenen Originalwege bestehen. Unveränderte Dauerinstanzen werden anhand ihrer Listener-Prozess-IDs geprüft, nicht neu gestartet.

## Nachfolgender Block

Erst auf dieser geprüften Grundlage: separater Entropiestrom, Fake-Clock-Intervall 1260 Sekunden, Stop-/Ende-/Neustartgrenzen, additive persistierte Sitzungsverläufe, numerische Trendklassen und UI. Keine medizinische Wirksamkeitsaussage aus zufallsbasierten GV-Verläufen. Der Gesamtblock bleibt bis zu dessen eigener Prüfung offen.

## Verifizierter Abschluss

Der finale isolierte Kandidat besteht 360 Engine-Tests (zwei Windows-Symlink-Skips) und 22 Browser-PASS-Abschnitte. Der unabhängige Herkunftsvergleich schließt kopierte Sitzungen in anderen Fällen aus; beschädigte optionale Falldaten blockieren keine reguläre Promotion. Astra-Funde einschließlich des Löschpfads sind korrigiert und regressionsgeprüft. Die 134 Originalquelldateien und sieben Live-Prozesse blieben unverändert. Nachweis: `docs/verification/RADIWORKS_GV_BINDUNG_2026-10-03.md`.

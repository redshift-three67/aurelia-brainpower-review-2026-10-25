
"""Record bounded verified VF2-A checkpoint; never read runtime homes or keys."""
from pathlib import Path
import json, hashlib, shutil, xml.etree.ElementTree as ET
from datetime import datetime
ROOT=Path(__file__).resolve().parents[1]
CANDIDATE=ROOT/'runtime/rw-vf2-20261004'
REPORT=ROOT/'docs/verification/RADIWORKS_VF2_A_ABSCHLUSS_2026-10-04.md'
PLAN=ROOT/'docs/verification/RADIWORKS_VF2_UMSETZUNGSPLAN_2026-10-04.md'
def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def load(path): return json.loads(path.read_text(encoding='utf-8-sig'))
def write(path,data): path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
verified=load(CANDIDATE/'FINAL_VERIFY.json')
assert verified['engine']=={'total':471,'passed':468,'skipped':3,'failures':0,'errors':0}
manifest=load(CANDIDATE/'PRODUCT_MANIFEST.json')
assert len(manifest['files'])==105
for e in manifest['files']: assert digest(CANDIDATE/e['path'])==e['sha256'],e['path']
browser=(CANDIDATE/'vf2-browser-verified.log').read_text(encoding='utf-8-sig')
assert sum(line.startswith('PASS ') for line in browser.splitlines())==22
assert 'CLEANUP isolated browser and runtime home' in browser
listeners=load(CANDIDATE/'LIVE_LISTENERS.json')
expected={8103:11408,8104:17880,8105:17752,8106:17904,8107:17760,8108:17500,8109:17912,8110:23288}
assert len(listeners)==8
assert {e['LocalPort']:e['OwningProcess'] for e in listeners}==expected
assert all(e['LocalAddress']=='127.0.0.1' for e in listeners)
verified.update({'browserSectionsPassed':22,'livePidsUnchanged':True,'liveListeners':listeners})
write(CANDIDATE/'FINAL_VERIFY.json',verified)
review={'reviewer':'GPT-6 Astra/medium','scope':'VF2-A backend source/contract review, no independent full-suite execution',
 'closedFindings':['rename identity/path preservation','raw session context replacement/removal','null personal context','forged clone provenance','legacy context enrichment','planned GV entropy checkpoint argument','direct GV helper inheritance','direct clone GV inheritance'],
 'remainingConcreteP1P2':[],'releaseGranted':False,
 'workers':{'GPT-6 Luna/max':'bounded read-only contract audit','root':'implementation and test execution'}}
write(CANDIDATE/'REVIEW.json',review)
stamp=datetime.now().astimezone()
name='RadiWorks-VF2-A-'+stamp.strftime('%Y%m%d-%H%M%S')
CHECKPOINT=ROOT/'checkpoints'/name
assert not CHECKPOINT.exists()
CHECKPOINT.mkdir(parents=True)
cp_rel=CHECKPOINT.relative_to(ROOT).as_posix()
report=f"""# RadiWorks VF2-A: Backend-Kontext und Auftragsbindung

Stand: {stamp.isoformat(timespec='seconds')}. **100 % des abgegrenzten Backend-Pakets**, keine vollständige VF-2-/Modul-/Integrationsfreigabe.

## Ergebnis und Nutzerwirkung
- Getrennte persönliche Angaben im Backend: Vorname, Nachname, Geburtsdatum, Ort; bestehende Fallbezeichnung, Beschreibung und Fokus bleiben erhalten. Strenge Typ-, Längen-, Unicode- und Datumsprüfung; persönliche Angaben werden nicht aus alten Dateinamen abgeleitet.
- Feste serverseitige Fall-ID und steigende Kontextversion. Explizites Umbenennen hält Datei, ID und bestehenden Fallverweis; eine vollständige Fallkopie erhält eine neue ID und unveränderte historische Herkunft.
- Neue fallgebundene Analysen speichern den damaligen Kontext getrennt in Sitzung und Draft. Spätere Falländerungen ändern diesen Stand nicht. GV-Folgesitzungen erben den exakten Elternstand, auch bei Fallkopien.
- Beim ausdrücklichen Promote erhält die virtuelle Queue ausschließlich eine unveränderliche Kontextreferenz, keine vollständigen persönlichen Daten. Bestehende Signatur-/Zeit-/Zahlenberechnung unverändert.
- Alte Sitzungen bleiben historisch ungebunden. Schreibversuche, ihren Kontext nachträglich zu ergänzen, zu ersetzen oder zu entfernen, werden abgewiesen.
- Der bereits vorhandene direkte GV-Helfer wurde angeglichen. Die ältere falsche Argumentposition im geplanten GV-Fork ist durch einen Gegenbeispieltest korrigiert: Entropiecheckpoint statt unbeabsichtigter Draft-ID.

## Verifikation
| Prüfung | Nachweis |
|---|---|
| Ganze Engine, endgültiger Stand |468 bestanden,3 bekannte Windows-Symlink-Skips,0 Fehler/Fehlschläge;471 erfasst|
| Neues Kontext-Testmodul |37 bestandene synthetische Fälle einschließlich Negativ-, Legacy-, Kopie-, Versions-, GV- und Promote-Prüfungen|
| Abschließende Playwright-Browserregression |22/22 Abschnitte auf zugewiesenem temporären Loopback-Port; keine JS-Seitenfehler|
| Gepinnter GV-2-Elternkandidat |103/103 Hashes unverändert|
| VF2-Kandidat |105 Dateien gepinnt;5 bestehende Engine-Dateien geändert,2 neue Dateien|
| Webapp und Rechenkerne |23/23 Webapp-Dateien und5 explizit geprüfte Zahlen-/Entropiekerne unverändert; gleicher Original-Seed trotz geändertem persönlichen Kontext getestet|
| Dauerinstanzen und Pilot |8103–8109 sowie8110 weiterhin Loopback, gleicher PID und pong; keine Starts/Stops/Taskänderungen|
| Referenzquellen |Gepinnte Aurelia-/Template-/Radi144-Referenzen erneut bytegleich; keine kanonische Übernahme|
| Unabhängiger Review |Astra: aufgeführte Befunde geschlossen, keine weiteren konkretenP1/P2 im abgegrenzten Umfang; Gesamtsuite vom Root ausgeführt|

Belege unter `runtime/rw-vf2-20261004/`: `vf2-engine-verified.xml/log`, `vf2-browser-verified.log`, `vf2-clone-fork-green.xml/log`, ursprüngliche RED/GREEN-Gegenbeispiele, `FINAL_VERIFY.json`, `REVIEW.json`, `PRODUCT_MANIFEST.json` und `PRODUCT_DIFF.patch`.
Die Starlette/httpx-Deprecation-Warnung bleibt. Kein neuer Linux-/Windows10-/Hardware-/Kamera-/bezahlter Hermes-Modelllauf.

## Grenzen
- Kein Originalalgorithmus nutzt diese persönlichen Metadaten als zusätzliche numerische Gewichtung. Eine solche Wirkung wird nicht behauptet; EXP-1 ist separat.
- Bild unterstützt hier nur validierte Referenzmetadaten (SHA256, Typ, Byteanzahl). Noch kein Bild-Upload, sichere Bilddecodierung oder Browserfeld. Dateiendung/Hash beweist keinen Bildinhalt.
- Auto-, direkte und Bild-Broadcasts sind ohne separat implementierte Herkunft weiterhin ungebunden; kein stillschweigendes Zuordnen zum aktuellen Fall.
- Die lokale SHA256-Prüfung dient Integrität/Provenienz, nicht als Signatur gegen einen Angreifer mit Vollzugriff auf Dateien. Validierte API-Schreibpfade erhalten die Historie.
- Legacy-Verweise verwenden weiterhin den pro Prozess erzeugten HMAC-Schlüssel. Die neue Fall-ID ist dauerhaft; der alte HMAC-Link wird dadurch nicht restartfest.
- Neue Felder sind **noch nicht in8110 oder8103–8109 sichtbar**. Browserstand unverändert; keine Migration realer Falldaten, Keys oder laufender Jobs.
- Originalbefunde, Testalgorithmen und GV-Verläufe belegen keine medizinische Wirkung.

## Phasenstand und nächste Schritte
| Paket | Stand |
|---|---|
| VF2-A Kontext-/Identitäts-/Auftragsvertrag Backend |100 % des geprüften Pakets|
| VF2-B persönliche Browserfelder und sicheres optionales Fokusbild |0 % Umsetzung; nächster Block|
| VF3 erklärbare heuristische Datenbankvorschläge |0 % Umsetzung, genehmigt|
| EXP1 separat wählbare Radi144-Heuristik |0 % Umsetzung, genehmigt|
| Weitere Echtzeit-Trend-, Kamera-/Recovery-, Area-/Peggotty- und Bedienabnahme |offen; frühere Einzelbelege gelten nur für ihren Quellstand|
| Kanonische RadiWorks-/Modul_Templates-Abstimmung |Delta vorbereitet, Übernahme offen|
| Windows10 Standalone mit bis5 isolierten Instanzen |noch nicht gebaut; nach integrierbarem Prototyp und Abnahme|
| Vollständige Governors/Aurelia/Module/Konfigurationen/Sessionhistorien-Sicherung aufF: |noch nicht aktualisiert; nach Paketprüfung und konsistentem Export|
| AureliaS4.8 |0 % Freigabe|

Die Prozentwerte gelten für die genannten begrenzten Pakete, nicht für eine Gesamtproduktionsreife.
Nächster Block VF2-B: explizite zugängliche Felder, originaler Falltext erhalten, sicheres optionales lokales Bild, verständliche Validierung und Neustart-/Browserprüfungen. Orientierung etwa1–2Stunden, bei Befunden länger; kein Zeitlimit.
Danach VF3 → EXP1 → Restprüfungen/Betreiberabnahme → Quellen/Templates → versioniertes Win10-Testpaket → vollständige zeitgestempelte Sicherung mit Wiederherstellungsprobe → Radi144. S4.8 separat.

## Modelle
Gewählte Chatleitung Sol6.1/high; Root implementierte und führte Prüfungen aus. Tatsächlich verwendet: Luna6/max für begrenzten lesenden Vertragsabgleich, Astra6/medium für unabhängige kritische Grenzprüfung. Keine gemessene Token-/Kosteneinsparung. Dies ändert keine Governors/Hermes-Anwendungsroute.

## Begrenzter Wiederherstellungspunkt
`{cp_rel}`:105 Kandidatendateien, Nachweise, Bericht/Plan/aktueller Einstieg und Hilfswerkzeuge mitSHA256-Manifest. Keine realen/synthetischen Homes, Keys, Tokens, venv, Caches oder temporären Testdaten. Kein Ersatz für die noch geplante vollständigeF:-Sicherung. Wiederherstellung zunächst ausschließlich in neues isoliertes Verzeichnis; keine automatische Übernahme in Dauerinstanzen.
"""
REPORT.write_text(report,encoding='utf-8')
plan=PLAN.read_text(encoding='utf-8-sig')
plan=plan.replace('- [ ]','- [x]')
plan += "\n## Verifizierter VF2-A-Abschluss\n468 Engine-PASS/3 Windows-Skips,37 neue Kontextfälle,22/22 Browserabschnitte; Astra-Befunde geschlossen.103 Elternhashes/23 Webappdateien unverändert.105 Kandidatendateien gepinnt. Backend abgeschlossen; VF2-B nicht begonnen. Einzelbelege und Grenzen: [VF2-A-Abschluss](RADIWORKS_VF2_A_ABSCHLUSS_2026-10-04.md).\n"
PLAN.write_text(plan,encoding='utf-8')
entry=f"""## Aktuelle Fortsetzung,04.10.2026 — RadiWorks VF2-A Backend abgeschlossen

Maßgeblich: [VF2-A-Abschluss](docs/verification/RADIWORKS_VF2_A_ABSCHLUSS_2026-10-04.md), [Umsetzungsplan](docs/verification/RADIWORKS_VF2_UMSETZUNGSPLAN_2026-10-04.md). Kandidat `runtime/rw-vf2-20261004`:105 gepinnte Dateien, neue persönliche Metadaten/ID/Version, unveränderlicher Sitzung-/Draftkontext und referenzierte Promote-Queue.468 Engine-PASS/3 bekannte Windows-Skips;37 neue Kontextfälle;22/22 finaler isolierter Browserlauf. Namensänderung, Fallkopie, Legacy-Historie, API-Manipulation und beide GV-Helfer geprüft. Astra-Befunde geschlossen. Originalalgorithmen/23 Webappdateien und103/103 GV2-Elterndateien unverändert.8103–8109/8110 gleicherPID/pong; keine Task-/Live-/Keymutation.

**Nächster Block VF2-B:** zugängliche persönliche Browserfelder und sicherer optionaler Bildpfad, mit synthetischer Browser-/Restartprobe außerhalb8103–8110. Erst danachVF3/EXP1. VF2-A=100% begrenztesBackend, VF2-B=0%; neue Felder noch nicht live. Keine automatische numerische Kontextgewichtung. Langzeittrend/Kamera/Recovery/Area/Peggotty und Gesamtbedienabnahme noch offen.

**Abschlussfolge vom Nutzer genehmigt:** Restprüfungen und integrierbarerPrototyp → kanonische Quellen/Modul_Templates → versioniertesWindows10-Standalonepaket mit bis5 isolierten Instanzen/Test → vollständigeGovernors/Gedächtnis/Aurelia/Module/Configs/erreichbareCodexhistorien-Sicherung mit Zeitstempel und Wiederherstellungsprüfung → Radi144. EchteKeys/Secrets nur gesondert sicher; kein Export in Testpaket. F:-Gesamtsicherung noch nicht erneuert; S4.8=0%Freigabe. Qualität vorZeit, bestehende bestätigte Funktionen erhalten.

Begrenzter lokaler Checkpoint: [{name}]({cp_rel}/RESTORE.md),105 Produktdateien plusBelege/Planung. KeineHomes/Keys/venv/Testtemp; keine vollständigeF:-Sicherung. Chatleitung gemäßAuswahlSol6.1/high; tatsächlichLuna6/max Vertragsaudit undAstra6/medium unabhängigerReview. Rootimplementierung/-tests. Hermes-Anwendungsroute unverändert. Historische Einträge unten nicht als aktuellerUmsetzungsstand lesen.

"""
wied=ROOT/'WIEDERAUFNAHME.md'
wied.write_text(entry+wied.read_text(encoding='utf-8-sig'),encoding='utf-8')
restore=f"""# Begrenzter VF2-A-Wiederherstellungspunkt
Erstellt:{stamp.isoformat(timespec='seconds')}.
105 Produktdateien des isolierten Kandidaten plus Nachweise, Plan und Wiedereinstieg.
Nicht enthalten: Fall-/Pilot-/Testhomes, Keys/Seeds, Tokens, Codex-/CC-Switch-/Serverconfigs, venv, Caches, F:-Gesamtarchiv.
Dieser Punkt sichert den VF2-A-Code-/Prüfstand; keine Wiederherstellung realer Livefalldaten.

1. Zuerst jede inMANIFEST.json genannte Datei gegenSHA256 prüfen; VERIFY.json protokolliert die Prüfung beim Erstellen.
2. Produktbaum unter runtime/rw-vf2-20261004 in ein neues isoliertes Verzeichnis kopieren. Bestehende8110/8103–8109 und Originalquellen nicht überschreiben.
3. Engine-Abhängigkeiten gemäßengine/pyproject.toml separat bereitstellen; lokalevenv nicht enthalten. Dann synthetische Engine-/Browserprüfung vor jedem Einsatz.
4. WIEDERAUFNAHME.md und VF2-A-Bericht lesen. VF2-B/VF3/EXP1 nicht umgesetzt; keine numerische Zusatzgewichtung/Liveübernahme.
5. Historische einmalige Patchskripte absichtlich nicht aufgenommen: nicht als Migrationswerkzeug ausführen.
6. Reale Recovery-Schlüssel und Homes separat erhalten. Keine automatische Rekonstruktion/Start alter Broadcasts, keine Integrations-/Betriebsfreigabe.

Die geplante vollständige Governors-/Aurelia-/Modul-/Konfigurations-/Historien-Sicherung aufF: bleibt ein späterer gesonderter Schritt.
"""
(CHECKPOINT/'RESTORE.md').write_text(restore,encoding='utf-8')
sources=[CANDIDATE/e['path'] for e in manifest['files']]
sources += [CANDIDATE/n for n in ['BASELINE.json','PARENT_PRODUCT_MANIFEST.json','PARENT_REFERENCE_SOURCES.json','PRODUCT_MANIFEST.json','PRODUCT_DIFF.patch','FINAL_VERIFY.json','LIVE_LISTENERS.json','REVIEW.json','browser_regression.mjs']]
sources += sorted(CANDIDATE.glob('vf2-*.xml'))+sorted(CANDIDATE.glob('vf2-*.log'))
sources += [REPORT,PLAN,wied,ROOT/'tools/prepare_radiworks_vf2_candidate.py',ROOT/'tools/verify_radiworks_vf2.py',Path(__file__)]
for source in sources:
 rel=source.resolve().relative_to(ROOT.resolve())
 target=CHECKPOINT/rel
 assert target.resolve().is_relative_to(CHECKPOINT.resolve())
 target.parent.mkdir(parents=True,exist_ok=True)
 shutil.copyfile(source,target)
files=[{'path':p.relative_to(CHECKPOINT).as_posix(),'sha256':digest(p)} for p in sorted(CHECKPOINT.rglob('*')) if p.is_file()]
write(CHECKPOINT/'MANIFEST.json',{'createdAt':stamp.isoformat(),'algorithm':'SHA256','files':files})
for e in files: assert digest(CHECKPOINT/e['path'])==e['sha256'],e['path']
write(CHECKPOINT/'VERIFY.json',{'verified':True,'files':len(files),'algorithm':'SHA256','scope':'bounded VF2-A product and evidence checkpoint','excludedLiveHomesAndKeys':True})
print(json.dumps({'checkpoint':str(CHECKPOINT),'verifiedFiles':len(files),'productFiles':105,'report':str(REPORT)}))


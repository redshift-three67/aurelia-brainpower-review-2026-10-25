# RadiWorks CP2A – SQLite-Kandidat im CI vorbereiten

**Goal:** Den bereits quellengeprüften SQLite3.54.1-Kandidaten als begrenztes CI-Build-/Loader-/Featurepaket vorbereiten, lokal ohne Linux-Produktlauf prüfen und unabhängig reviewen.

**Architecture:** Betreiberentscheidung25.10.2026: CodexCLI/Desktop steuert, privatesGitHubCI baut/prueft, LinuxPilotserver nimmt spaeter genau gebundene Artefakte fuer Browser-/Workflowtests auf. CloudB1/B2 und ImportI bleiben zurueckgestellt. Ausschliesslich neue Kandidaten unter runtime/rw-ci-cp2a-prep-20261025; keine Produkt-/Governorimplementierung oder Git-Worktree-Kopie des uebergeordneten Benutzerrepositories. Diese vorhandene additive Ablageisolation wahrt unveraenderte externe Produktquellen und unbeteiligtesWIP; kein Commit/Push aus Vorbereitung.

**Tech Stack:** PythonStandardbibliothek, gebundene offizielle SQLiteVollquelle, festerBookwormBuilderdigest, vorhandenes Runtimebasisimage und34Wheels, manuellesUbuntuCI. Kein lokalerDocker-/WSL-/Linux-Produktlauf.

- [x] Neue Strategieentscheidung und Stilllegung der Cloudvergleichsfortsetzung festhalten; alte Belege unveraendert erhalten.
- [x] Materialbindung vorbereitet: 204 kanonische Quellen erneut gehasht; unveraenderter Source-Lock, feste SQLite-Quelle mit SHA256/SHA3 und gebundener Builderdigest in MATERIALS.json; Flags und 58 Baselineoptionen konsistent. Native Toolchain-/Build-/Loaderbelege weiterhin offen.
- [x] sqlite_probe.py und test_sqlite_probe.py: zuerst negativeTests fuer falscheVersion/sourceid, falschen gemapptenPfad/Dateihash, Pythonextensiondrift und fehlende/geaenderteCompileoptionen. NativeCLI sammelt nur eigenenProzess-/Bibliotheknachweis und :memory:FeatureSQL. Kein Produktimport oder persistenteDB. Optionendeltas bleiben Pruefluecken, Compilerkennung separat; keine stillen Freigaben.
- [x] build-sqlite.sh: festerWerkzeugsatz/Versionen vorCompile; read-onlyQuellen; SourceZIP erst hashgebunden entpacken; Parser mit UPDATE_DELETE_LIMIT aus Vollquelle erzeugen, maximal1Compilercontainer/1CPU/2GiB/keinSwap/256PIDs/900s/netzlos. Keinapt/Hostcompiler/Toolrepair. Privatprefix und Herkunfts-/Hashbelege; altenSystemSQLitebestand erhalten.
- [x] CP2A-CIworkflow vorbereiten: nurmanuell/privateRepo/contentsread/fixeCheckoutSHA,30Minuten; zwei festeImagepulls plus34Wheels, boundedSourceDownload; OriginalRuntimeDockerfile unveraendert, zusaetzliches KandidatenDockerfile nurSQLitebibliothek/Herkunft unter /opt/radiworks-sqlite/lib. Baselineextension/Python hashpruefen; Kandidat in neuem isoliertenProzess mit eigenemLD_LIBRARY_PATH; actualmaps/version/sourceid/options/FeatureSQL. KeinProduktserver, keine optionalenTorchdownloads, keinRegistrypush/Artefaktupload/SSH oder automatischerRetry. NichtbeherrschteOptionendeltas stoppen vor Produktregression.
- [x] LokaleTests/Script-/Workflowpruefung und unabhaengigerAstra/mediumReview. Nur nativeBuild-/Loaderbelege nach eigenemCI-Lauf, keine simuliertenErgebnisse als nativeAbnahme ausgeben.
- [x] Konkreter Einmalumfang und Kosten vorbereitet: APPROVAL_SCOPE.json, PACKAGE_MANIFEST.json, COSTS.json, APPROVAL_REQUEST.txt; abschliessender Astra/medium-Review ohne konkrete P0/P1-Blocker. Noch keine Veroeffentlichungs-/Lauffreigabe.

**Acceptance:** UnveraendertegebundeneQuellen; negativeValidierungsfaelle belegt; keine gefaehrlichenFallbacks; klareTrennung Vorbereitung/nativeCI/Pilot-/Produktfreigabe. AktuelleSQLitequellen inklusiveWALfix sind einQuellbeleg, kein Laufzeitnachweis. Compiler-/Loader-/Featureabweichungen werden im begrenztenCI sichtbar und sperren eine spaetereUebernahme.

**Pause vor Codex-Neustart, 25.10.2026:** Kandidatenhelfer/CI-Skripte vorhanden; 58 lokale Hilfstests und beide Shell-Syntaxprüfungen erfolgreich, unabhängiger Delta-Review ohne verbleibenden konkreten Blocker. Obige Gesamt-Checkboxen bleiben bewusst offen, soweit finale Bindung bzw. native Nachweise fehlen. Kosten-/Freigabeumfang und operatives Paketmanifest noch nicht finalisiert. [Wiederanlaufspunkt](../../../checkpoints/Aurelia-CP2A-Pause-20261025T115626Z/PAUSE.json).

- [ ] Neue konkrete Betreiberfreigabe fuer Veroeffentlichung und genau einen30min-CI-Job; vor Ausfuehrung frisches Kontingent und Remote-/Pfad-/Commitabgleich.
- [ ] Native CP2A-Compile-/Loader-/Options-/Featurepruefung. Erst danach eigene CP2B-/Artefakt-/Pilotgates; kein nativer Erfolg aus Vorbereitung ableiten.

**Fortsetzung 25.10.2026:** Vorbereitungsabschluss siehe runtime/rw-ci-cp2a-prep-20261025/STATE.json. Alle12 operativen Dateien unveraendert zum getesteten Stand. Ein Fehler des zusaetzlichen lokalen AST-Belegabgleichs wurde ohne Helfer-/Produktcodeaenderung korrigiert, strukturell positiv/negativ nachgeprueft und als PREPARATION_CHECK_INCIDENT.json erhalten. Keine neue externe Ausfuehrung.

**Nativer Verlauf25.10.2026:** Einzellauf40196634387 mit exaktfreigegebenemCommit ausgefuehrt und anCRLF/Shelloptionen vorDocker abgebrochen. Kein Build-/Loadernachweis, keinRetry. NeuerseparaterLF-Kandidat mit65lokalenTests/Astra-Review vorbereitet; eigeneZwei-Dateien-/EinmalCI-Freigabeoffen. AktuellerEinstieg: docs/SERVER_AKTUELL.md.

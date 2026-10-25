# RadiWorks Audio-Diagnose und vereinfachte Oberfläche

Stand 2026-10-08T08:58:02.929913+02:00. Kandidat `runtime/rw-audio-diagnosis-20261008`; nachfolgend Nutzer-Hörabnahme und R6-Dauerübernahme bestätigt (siehe RADIWORKS_R6_DAUERINSTANZEN_2026-10-08.md). Start5 bleibt separat offen.

## Befund und Änderungen

Der Nutzer bestätigt inzwischen feste Frequenzen und Solfeggio hörbar, alle Rosa-Rauschen-Profile bislang unhörbar. Eine vorherige Liveprüfung zeigte Original-Ereignistöne bei ausgeschalteter Original-Toneinstellung. Das erklärt diese konkrete Zuordnung, nicht die spätere Rauschstille. Browseraktivierung allein bestätigt keine physische Signalwiedergabe.

Rauschkette: bisher konstant begrenzter Worker plus Voicegain1/8 plus Master0..0.2. Nur Pink-Wiedergabegain nun2 statt1/8 (+24.08dB). Rauschkern, Spektrum, Pulsprofile/Phi-/Fibonacci-Zeiten, Seeds, gespeicherte Profilschemata/Digests, Original-/persönliche Analyse und alle Enginebytes unverändert. Fixed-/Originalton-Gain weiterhin1/8, Standardmaster10%, Maximum20%. Keine adaptive Verstärkung, kein Limiter, keine zusätzlichen Analyseziehungen.

Maximal2 Pink-Stimmen und8 Gesamtstimmen einschließlich initialisierender/ausblendender Stimmen. Validiertes PCMabs<=1. Konservativer Kanalpeak (2*2+6/8)*0.2=0.95. Dies ist eine digitale Grenze, keine Aussage zum Schalldruck am Gerät. Zusätzlicher ausdrücklich gestarteter Testton432Hz/2s, ohne Fall-/Broadcastauftrag; gleiche Stimmengrenze, kein Stapeln, Stopp-/Sichtbarkeitsregeln erhalten.

Profilzuordnung, ausgeschaltete Originaltöne und abgelaufene Einmalfolgen erscheinen verständlich. Jede Broadcastkarte benennt ihr eingefrorenes Profil. Profiländerungen gelten weiterhin ausschließlich für neue Broadcasts.

Zusätzlicher Original-/Experimentalvergleich aus HTML, Analyze-Import/Init/Sichtbarkeit entfernt; gespeicherte Vergleichsbelege und Backend bleiben erhalten. Original und Persönliche Heuristik mit beiden Zufallsmodi bleiben vorhanden. Queue-/Resonated-Rates-Spalten jetzt gleich breit; GV bleibt unter Resonated Rates.

## Prüfungen

- RED/GREEN: expliziter Testton, Profilzuordnung, Pink-Gain und Summengrenze.100/100 JS-Tests nach letzter Pegeländerung bestanden. Testdeckel bei Initialisierung/Softstop erhalten.
- Echter Chrome/WebAudio mit physisch stummer Testausgabe:432Hz-Testton, AudioContext48000Hz/running, Stopclosed. Original+seeded/stochastic und Personal+seeded/stochastic je3 synthetische Katalograten erfolgreich. Keine Pageerrors und keine Experimentalvergleichs-API-Aufrufe.1440px Queue/Resonated beide530.708px;390px ohne horizontalen Seitenüberlauf.
- Tatsächlich gerendertes OfflineAudioContext-PCM: PinkRMS0.002846709, Peak0.014858882; Pulse/Phi/FibonacciRMS0.00216..0.00237. Künstlicher Worstcase2 konstante Pinkquellen+6Mono432Hz-Töne bei Master20% Peak0.949999630, kein digitales Clipping. Nicht als reale Hörprobe ausgeben.
- Keine neuen Backendänderungen; Enginebytegleichheit gegen altes198Dateien-Manifest geprüft. Vorherige Backendprüfungen weiterhin Referenz, nicht als heute erneut ausgeführt darstellen.

## Grenzen / Abnahme

Aktuelles Benutzer-IAB-Audiogerät konnte automatisiert wegen Windows-Sandbox-ACL nicht inspiziert werden. Nutzer hört feste/Solfeggio-Töne; Pink-Hörprobe nach Bereitstellung vom Betreiber erfolgreich bestätigt. Betreiberfreigabe zum Beenden von Auto/Broadcasts und Neustart erteilt.8112 sauber beendet (alterPID51856), Fallsicherung `checkpoints/RadiWorks-Audio-8112-Fallsicherung-20261008-091751`:498verifizierte Dateien,492statische Homefiles und2SQLite-Backups. Neuer tatsächlicherPID12192;200Produktdateien/digestgebunden. Nach Neustart alle492statischen Dateien und logischer Inhalt beider SQLite-Datenbanken identisch. Ping200, ausgeliefertes HTML/Player bestätigt, AutoOFF, Queueleer.

Route: Nutzergewählte GPT6.1Sol/high-Leitung; tatsächlich Luna6/max für unabhängige Pegeldiagnose, Astra6/medium für Maximalpegel-/Lebenszyklusreview eingesetzt. Astra ohne statischen Blocker, ergänzt Reservierungs-/Softstop- und echten Rendernachweis; erfüllt. Review ist keine Freigabe.

Dauerinstanzen8103–8109 nach erfolgreicher Nutzerabnahme übernommen; Modul_Templates-/Quellordnerübernahme und neuesStart5 bleiben nächste R6-Teilpakete. Kein Wechsel der Originalalgorithmen oder Datenbankstruktur in diesem Paket.

Zusätzliche Regression: synthetische5Animationsbilder, Reihenfolge/Save/Reload, alte eingefrorene Broadcastbelege, Festtöne und normaler Pink-Worker (11Chunks) im Chrome-Browser bestanden. Ein ergänzendes Puls-Skript setzte zuerst eine5Bild-Testfixture voraus, die in diesem frischen Test-Home nicht vorhanden war;0!=5 war ein Fixturefehler vor dem Signaltest. Die Fixture wird ausdrücklich hergestellt, nicht der Produktcode hierfür geändert.

Ergänzender Puls-Test mit ausdrücklich hergestellter5Bild-Fixture erfolgreich: gleichmäßig/Phi/Fibonacci je6s reale WebWorker-Wiedergabe, jeweils10PCM-Chunks,48kHz, Depth70, Legacy-Downgrade/Reload/390px geprüft; keinePageerrors/HTTPfehler. Physisch stumm.

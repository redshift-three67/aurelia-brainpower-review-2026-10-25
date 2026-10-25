# 11 - Mermaid-Strukturen

Dieses Dokument bündelt die wichtigsten Systembilder. Die Diagramme beschreiben den aktuellen Code, sofern sie als **Ist** gekennzeichnet sind. **Ziel**-Diagramme sind Empfehlungen, keine bereits vorhandene Implementierung.

## 1. Systemkontext - Ist

```mermaid
flowchart TB
    USER[Benutzer oder Praxis] --> WEB[Browserworkflow]
    USER --> PS[PowerShell-Wizard]
    USER --> CLI[Python-CLI]
    WEB -->|HTTP und WebSocket| API[FastAPI]
    PS --> CLI
    CLI --> CORE[Resonanzengine]
    API --> CORE
    CORE --> REFS[Bio-, Paletten-, Amplifier- und DB-Referenzen]
    API --> RUNTIME[Runtime-JSON]
    CLI --> RUNTIME
    API --> ART[PDF und Artefakte]
    CLI --> ART
    WEB --> LOCAL[Browser-LocalStorage und Downloads]
    CLI -. optional .-> BUS[(SQLite-Interchange-Bus)]
    DEPLOY[systemd-Deployment] --> API
```

## 2. Komponenten - Ist

```mermaid
flowchart TB
    subgraph Presentation[Präsentation]
        HTML[user_workflow.html]
        JS[user_workflow.js]
        PWSH[generate_matrix.ps1]
        DEVCLI[dev_cli.py]
        TK[Tkinter und Winsound]
        PWSH --> DEVCLI
        DEVCLI --> TK
    end

    subgraph Application[Anwendung]
        MAIN[main.py]
        RESAPI[api/resonance.py]
        CLIENTAPI[api/clients.py]
        MAIN --> RESAPI
        MAIN --> CLIENTAPI
    end

    subgraph Domain[Algorithmen]
        ENG[ResonanceMatrixEngine]
        SIG[ClientSignatureGenerator]
        EMF[EMFCompensator]
        AMP[AmplifierVectorGenerator]
        ENG --> SIG
        ENG --> EMF
        ENG --> AMP
    end

    subgraph Services[Dienste]
        REG[ClientRegistryService]
        SES[SessionArchiveService]
        MAN[ReportManifestService]
        ERASE[ErasureService]
        AUD[AuditService]
        JSON[JsonStore]
        REG --> JSON
        SES --> JSON
        MAN --> JSON
        ERASE --> REG
        ERASE --> SES
        ERASE --> MAN
        ERASE --> AUD
    end

    subgraph Interchange[Interchange]
        CONS[Radi144BusConsumer]
        STORE[BusConsumerStore]
        SQLITE[(SQLite)]
        CONS --> STORE
        STORE --> SQLITE
    end

    HTML --> JS
    JS --> MAIN
    RESAPI --> ENG
    RESAPI --> REG
    RESAPI --> SES
    RESAPI --> MAN
    CLIENTAPI --> ERASE
    DEVCLI --> ENG
    DEVCLI --> REG
    DEVCLI --> SES
    DEVCLI --> MAN
    DEVCLI -. optional .-> CONS
```

## 3. Einzelanalyse - Ist

```mermaid
sequenceDiagram
    actor U as Benutzer
    participant UI as UI oder CLI
    participant API as Analyse-API
    participant S as Signaturgenerator
    participant E as Engine
    participant J as JSON-Services

    U->>UI: Klient, Fokus, Modus und Optionen
    UI->>API: POST analyze-matrix
    API->>API: Eingabemodus auswählen
    API->>S: Signatur oder Vorabsignatur
    S-->>API: Frequenz und Komponenten
    API->>E: calculate_resonance
    E->>E: MD5-seedete Vektoren
    E->>E: Zufallsmatrizen erzeugen
    E->>E: Zufallsprojektion und Cosinusähnlichkeit
    E->>E: Top-10 auswählen
    E->>E: optional Symmetrie und Farbe
    E-->>API: Resultat
    API->>J: Client laden oder anlegen
    API->>J: Session anhängen
    J-->>API: IDs
    API-->>UI: JSON und X-Client-/X-Session-ID
    UI-->>U: Matrix, Score, Details und Export
```

## 4. Mehrfachfokus im Browser - Ist

```mermaid
sequenceDiagram
    actor U as Benutzer
    participant B as Browser
    participant A as API
    participant D as Sessionarchiv

    U->>B: Fokus 1; Fokus 2; Fokus 3
    loop je Fokus
        B->>A: einzelne analyze-matrix-Anfrage
        A->>D: eigene Session speichern
        A-->>B: einzelnes Resultat
    end
    Note over B,D: Kein gemeinsamer Batch, kein Rollback, kein Resume
```

## 5. Algorithmischer Datenfluss - Ist

```mermaid
flowchart LR
    ID[Name, Geburt, Ort, Zeit] --> HF[skalare Heuristik]
    IMG[Bild] --> HF
    GEO[Geo] --> HF
    GROUP[Gruppe] --> HF
    DB[DB-Teilstringsuche] --> HF
    HF --> CV[MD5-Seed zu Zufallsvektor]
    FOCUS[Fokustext] --> FV[MD5-Seed zu Zufallsvektor]
    BIO[Chakra oder Meridian] --> BV[MD5-Seed zu Zufallsvektor]
    FV --> TARGET[Zielvektor]
    BV --> TARGET
    CV --> TARGET
    RNG[Zufallsmatrizen 0 bis 9] --> PROJ[zufällige Projektion]
    TARGET --> SCORE[Cosinusähnlichkeit]
    PROJ --> SCORE
    SCORE --> TOP[Top-10]
    TOP --> SYM[optionale Symmetrie]
    SYM --> COLOR[Farbmatrix]
    COLOR --> OUT[Resultat]
```

## 6. EMF-Profil - Ist

```mermaid
flowchart LR
    RNG[os.urandom Statistik] --> IDX[Composite-Index]
    JITTER[CPU-Timing-Jitter] --> IDX
    LOAD[CPU- und RAM-Last] --> IDX
    GPU[GPU-Laufzeit und Drift] --> IDX
    SDR[optionales SDR] -. optional .-> IDX
    IDX --> COMP[zufallsbasierter Kompensationsvektor]
    IDX --> COUNTER[Counter-Frequencies]
    COMP --> TARGET[Client- und Fokusvektor]
    SENSOR[Remote GPS, HRV, Audio] --> GLOBAL[globaler Remote-Sensorzustand]
    GLOBAL -. derzeit nicht in profile_environment .-> IDX
```

## 7. Datenlebenszyklus - Ist

```mermaid
flowchart TD
    INPUT[Klient und Fokus] --> LS[Browser LocalStorage]
    INPUT --> ANALYSIS[Analyse]
    ANALYSIS --> CLIENTS[clients.json]
    ANALYSIS --> SESSIONS[sessions.json]
    ANALYSIS --> RESULT[Resultat im Browser oder CLI]
    RESULT --> PDF[PDF]
    RESULT --> XLSX[XLSX oder CSV]
    RESULT --> AUDIO[WAV oder WebM]
    RESULT --> LOG[Logs und Zwischenablage]
    PDF -. teilweise .-> ART[artifacts.json]
    XLSX -. teilweise .-> ART
    AUDIO -. meist nicht .-> ART
    SESSIONS --> TEMPLATE[PowerShell- und Legacy-Templates]
```

## 8. Löschung und verbleibende Kopien - Ist

```mermaid
flowchart TD
    REQ[Löschrequest] --> TOKEN[Gate-Token]
    TOKEN --> C[Client entfernen]
    C --> S[Sessions entfernen]
    S --> A[Artefaktmetadaten entfernen]
    A --> F[registrierte Dateien best effort]
    F --> D[passende Analyseordner best effort]
    D --> AUDIT[Audit best effort]

    LS[LocalStorage] -. nicht erreicht .-> REST[verbleibende Kopien]
    DL[Downloads] -. nicht erreicht .-> REST
    LEG[Legacy-/Fokusdateien] -. nicht vollständig .-> REST
    LOGS[Logs] -. nicht vollständig .-> REST
    BACK[Backups und RestorePoints] -. nicht erreicht .-> REST
    GIT[Git-Historie] -. nicht erreicht .-> REST
    BUS[Busdatenbank] -. nicht erreicht .-> REST
```

## 9. Lost Update - Ist-Risiko

```mermaid
sequenceDiagram
    participant W1 as Uvicorn Worker 1
    participant W2 as Uvicorn Worker 2
    participant F as sessions.json
    W1->>F: Version N lesen
    W2->>F: Version N lesen
    W1->>W1: Session A ergänzen
    W2->>W2: Session B ergänzen
    W1->>F: N plus A atomar ersetzen
    W2->>F: N plus B atomar ersetzen
    Note over F: atomare Datei, aber Session A verloren
```

## 10. Trust Boundaries - Ist

```mermaid
flowchart TB
    subgraph Untrusted[Nicht vertrauenswürdig]
        NET[Netzclients]
        INPUT[Nutzertexte und Pfade]
        TPL[LocalStorage-Templates]
        DBTEXT[DB-Textdateien]
        BUSMSG[Bus-Envelopes]
    end

    subgraph Boundary[Systemgrenzen]
        HTTP[HTTP-Middleware]
        WS[WebSockets ohne eigenes Gate]
        DOM[Browser-DOM]
        PS[PowerShell Invoke-Expression]
        FILE[Dateipfadauflösung]
        VERIFY[Bus SHA-Check]
    end

    subgraph Trusted[Schutzwerte]
        PII[PII und Gesundheitsfokus]
        FS[Serverdateisystem]
        ENGINE[CPU/GPU/Engine]
        STORES[Runtime-Stores]
    end

    NET --> HTTP
    NET --> WS
    INPUT --> DOM
    INPUT --> PS
    INPUT --> FILE
    TPL --> DOM
    DBTEXT --> ENGINE
    BUSMSG --> VERIFY
    HTTP --> PII
    HTTP --> ENGINE
    WS --> ENGINE
    DOM --> PII
    PS --> FS
    FILE --> FS
    VERIFY --> STORES
```

## 11. Deployment - Ist

```mermaid
flowchart LR
    DEV[beliebiger Entwicklerarbeitsbaum] --> RSYNC[rsync mit Denylist]
    RSYNC --> OPT["/opt/resonance-engine"]
    OPT --> VENV[neues venv]
    VENV --> TORCH[Torch aus CUDA-Index]
    TORCH --> REQ[offene requirements]
    REQ --> UNIT[systemd-Unit]
    ENV[ignorierte server.env] --> UNIT
    UNIT --> UV[Uvicorn mehrere Worker]
    UV --> JSON[gemeinsame JSON-Dateien]
    UV --> GPU[gemeinsame GPU]
```

## 12. Risikokopplung - Ist

```mermaid
flowchart TD
    OPEN[Offenes Binding plus kein API-Key] --> READ[Dateilesen]
    OPEN --> WRITE[Dateischreiben]
    OPEN --> DELETE[Löschung]
    OPEN --> DOS[DoS]
    OPEN --> WS[Sensor-WebSockets]
    MULTI[Mehrere Worker] --> LOST[Lost Updates]
    MULTI --> GPU[GPU-Druck und Zustandsdrift]
    CLAIM[Medizinische Claims] --> RANDOM[Nicht validierter Zufallsscore]
    RANDOM --> LIABILITY[Haftung und Regulierung]
    PII[Klartext-PII] --> RET[Keine Retention]
    PII --> BACK[Unvollständiges Backup und Löschen]
    RET --> PRIV[Datenschutzrisiko]
    BACK --> PRIV
```

## 13. Zielarchitektur - Empfehlung

```mermaid
flowchart TB
    subgraph Edge[Zugriffsgrenze]
        PROXY[TLS Reverse Proxy]
        AUTH[Benutzer, Rollen, Mandanten]
        LIMIT[Rate, Body und Origin Limits]
        PROXY --> AUTH
        AUTH --> LIMIT
    end

    subgraph App[Anwendung]
        API[zustandsarme API]
        JOB[Analyse-Jobservice]
        PRIV[Datenschutz- und Löschservice]
        LIMIT --> API
        API --> JOB
        API --> PRIV
    end

    subgraph Compute[Rechenebene]
        QUEUE[(Jobqueue)]
        WORKER[kontrollierter CPU/GPU-Worker]
        CORE[versionierter Core ohne globalen Requestzustand]
        JOB --> QUEUE
        QUEUE --> WORKER
        WORKER --> CORE
    end

    subgraph Storage[Datenebene]
        DB[(transaktionale Datenbank)]
        ARTS[gesandboxter Artefaktspeicher]
        REFD[versioniertes Referenzdatenmanifest]
        API --> DB
        JOB --> DB
        WORKER --> DB
        WORKER --> ARTS
        CORE --> REFD
        PRIV --> DB
        PRIV --> ARTS
    end

    subgraph Ops[Betrieb]
        HEALTH[Health und Readiness]
        OBS[Logs, Metriken, Tracing, Alerts]
        BACKUP[verschlüsselte Backups und Restoretests]
        HEALTH --> OBS
        DB --> BACKUP
        ARTS --> BACKUP
    end
```

## 14. Ziel-Releasefluss - Empfehlung

```mermaid
flowchart LR
    COMMIT[sauberer Commit] --> CI[CI: Lint, Typing, Tests]
    CI --> SEC[Security, Lizenz, SBOM]
    SEC --> BUILD[versioniertes Artefakt]
    BUILD --> SIGN[Prüfsumme und Signatur]
    SIGN --> STAGE[Staging-Install]
    STAGE --> MIG[Migration und Restoretest]
    MIG --> E2E[E2E, Last, Security, GPU]
    E2E --> RELEASE[Release-Tag]
    RELEASE --> DEPLOY[atomarer Deploy]
    DEPLOY --> READY[Readiness]
    READY --> TRAFFIC[Trafficfreigabe]
    DEPLOY -. Fehler .-> ROLLBACK[Rollback]
```

# Schnellstart-Anleitung: Resonanzmatrix-Workflow nach Neustart

## Voraussetzungen
- Python muss installiert sein (Python 3.10+)
- Alle Projektdateien liegen in `c:\Users\Administrator\Documents\12x12\`

---

## Schritt-für-Schritt nach Rechner-Neustart

### 1. Terminal öffnen (PowerShell)
- **Win + X** → **Windows Terminal** oder **PowerShell** öffnen

### 2. FastAPI-Backend starten
```powershell
cd c:\Users\Administrator\Documents\12x12
python main.py
```
- Warten bis `Uvicorn running on http://0.0.0.0:8000` erscheint
- **Dieses Fenster offen lassen!**

### 3. Zweites Terminal öffnen — Dateiserver starten
```powershell
cd c:\Users\Administrator\Documents\12x12
python -m http.server 8090
```
- Warten bis `Serving HTTP on :: port 8090` erscheint
- **Auch dieses Fenster offen lassen!**

### 4. Browser öffnen
```
http://localhost:8090/user_workflow.html
```

### 5. Fertig!
- Ihre **letzte Session** (Klientendaten, Fokus, Konfiguration) wird automatisch aus dem Browser-Speicher wiederhergestellt
- Ihre **gespeicherten Templates** und **Fokus-History** sind ebenfalls noch da
- Der grüne Status „Server verbunden" oben rechts bestätigt die Verbindung

---

## Wichtige Hinweise

| Thema | Details |
|---|---|
| **Beide Terminals** müssen laufen | Backend (Port 8000) + Dateiserver (Port 8090) |
| **Browser-Daten** | Session, Templates und Fokus-History sind im Browser gespeichert (localStorage) — bleiben nach Neustart erhalten, solange Sie nicht den Browser-Cache löschen |
| **Cache löschen vermeiden** | „Browserdaten löschen" in Chrome/Edge löscht auch Ihre gespeicherten Sessions und Templates |
| **Reihenfolge** | Immer zuerst Backend (main.py), dann Dateiserver, dann Browser |
| **Port belegt?** | Falls Port 8090 belegt ist: andere Nummer verwenden, z.B. `python -m http.server 8091` und dann `localhost:8091` im Browser |

---

## Schnelltest: Läuft alles?

1. Seite laden → **grüner Punkt** im Header = Backend OK
2. Felder vorausgefüllt? → **Session-Restore** funktioniert
3. Step 1 → „Templates verwalten" klicken → Ihre Templates sind da

---

## Herunterfahren (sauber beenden)

1. Im Browser: nichts nötig (Session wird automatisch gespeichert)
2. Terminal 1 (Dateiserver): **Strg + C**
3. Terminal 2 (Backend): **Strg + C**
4. Rechner herunterfahren

# FC Zürich Stats Dashboard

Eine Web-Applikation zur Anzeige von FC Zürich Statistiken aus der Swiss Super League.

![FC Zürich](https://img.shields.io/badge/Team-FC%20Z%C3%BCrich-0066b3)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED)
![Python](https://img.shields.io/badge/Python-3.11-3776AB)

## Features

- 📊 **Tabellenposition** - Aktuelle Platzierung in der Swiss Super League
- ⚽ **Saisonstatistiken** - Siege, Unentschieden, Niederlagen
- 🥅 **Torstatistiken** - Geschossene und kassierte Tore, Tordifferenz
- 📅 **Nächstes Spiel** - Datum, Gegner und Spielort
- 📈 **Komplette Tabelle** - Übersicht aller Teams in der Liga
- 📱 **Responsive Design** - Optimiert für Desktop und Mobile

## Schnellstart mit Docker

### Option 1: Docker Compose (Empfohlen)

```bash
# Repository klonen
git clone https://github.com/noahzuerii/fcz_stats.git
cd fcz_stats

# Mit Docker Compose starten
docker-compose up -d

# App öffnen
open http://localhost:5000
```

### Option 2: Docker direkt

```bash
# Image bauen
docker build -t fcz-stats .

# Container starten
docker run -d -p 5000:5000 --name fcz-stats-app fcz-stats

# App öffnen
open http://localhost:5000
```

## Konfiguration

### API Key (Optional)

Für Live-Daten von API-Football können Sie einen kostenlosen API-Key verwenden:

1. Registrieren Sie sich auf [API-Football](https://www.api-football.com/) (100 Anfragen/Tag gratis)
2. Erstellen Sie eine `.env` Datei:
   ```bash
   cp .env.example .env
   ```
3. Fügen Sie Ihren API-Key hinzu:
   ```
   FOOTBALL_API_KEY=your_api_key_here
   ```

Ohne API-Key werden Demo-Daten angezeigt.

## Lokale Entwicklung

```bash
# Python Virtual Environment erstellen
python3 -m venv venv
source venv/bin/activate

# Dependencies installieren
pip install -r requirements.txt

# App starten
python app.py

# App öffnen
open http://localhost:5000
```

## Projektstruktur

```
fcz_stats/
├── app.py              # Flask Hauptanwendung
├── requirements.txt    # Python Dependencies
├── Dockerfile          # Docker Image Definition
├── docker-compose.yml  # Docker Compose Konfiguration
├── templates/
│   └── index.html      # HTML Template
└── static/
    └── css/
        └── style.css   # CSS Styles
```

## Technologie-Stack

- **Backend:** Python 3.11, Flask 3.0
- **Frontend:** HTML5, CSS3 (Vanilla)
- **Deployment:** Docker, Gunicorn
- **Daten:** API-Football (api-football.com) - Swiss Super League wird unterstützt

## Erreichbarkeit von überall

Nach dem Docker-Deployment ist die App auf Port 5000 erreichbar. Um sie von überall zu erreichen:

1. **Port-Weiterleitung:** Konfigurieren Sie Ihren Router, Port 5000 an Ihren Server weiterzuleiten
2. **Cloud-Deployment:** Deployen Sie auf einem Cloud-Server (AWS, DigitalOcean, etc.)
3. **Reverse Proxy:** Verwenden Sie nginx oder Traefik für HTTPS und eigene Domain

### Beispiel mit nginx Reverse Proxy:

```nginx
server {
    listen 80;
    server_name fcz-stats.example.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Lizenz

MIT License - Frei zur Verwendung und Modifikation.

---

**Hopp Züri! 💙⚪**
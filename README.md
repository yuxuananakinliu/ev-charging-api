# EV Charging Stations — REST API + Map UI

[![FastAPI](https://img.shields.io/badge/API-FastAPI-009688)](#)
[![SQLite](https://img.shields.io/badge/DB-SQLite-003B57)](#)
[![Leaflet](https://img.shields.io/badge/Map-Leaflet-199900)](#)
[![Tests](https://img.shields.io/badge/Tests-Pytest-6C7A89)](#)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](#license)

A production-style **REST API** and **zero-build web UI** for exploring EV charging stations.  
Supports **geospatial search**, **connector filters** (CCS / Tesla-NACS / CHAdeMO / J1772), and a clean map with clustering.

> Built to showcase **API development**, **data ETL**, and **frontend UX** in one deployable project.

---

## Features

- **Open Data → SQLite**: ETL from U.S. DOE **AFDC** CSV to a normalized schema (`stations`, `connectors`)
- **FastAPI** backend:
  - `GET /stations` — nearby search with bounding box + Haversine distance
  - `GET /stations/{id}` — station details + connector types
  - OpenAPI docs at **`/docs`** (Swagger) and **`/openapi.json`**
- **Leaflet** web UI:
  - Filter panel (connector, radius, DC fast only)
  - “Search as I move” toggle, connector badges, Google Maps deeplink
  - Marker clustering for dense regions
- **Clean structure & deploy**:
  - Backend → Render (free)
  - Frontend → Netlify/Vercel (free)
  - Semantic versioning + `CHANGELOG.md`

---

## Project Structure

```text
restapi_evcharge/
├─ backend/
│  ├─ main.py            # FastAPI app (endpoints, models, CORS, docs)
│  ├─ etl.py             # CSV → SQLite loader
│  ├─ schema.sql         # DB schema (stations, connectors)
│  └─ __init__.py
├─ data/
│  ├─ afdc_stations.csv  # source CSV (commit this)
│  └─ ev.db              # SQLite DB (optional to commit; see Deploy)
├─ frontend/
│  └─ index.html         # zero-build Leaflet UI (CDN assets)
├─ requirements.txt
├─ CHANGELOG.md
├─ README.md
└─ .gitignore
```

> Note: the file is **`__init__.py`** (double underscores), not `init.py`.

---

## Data Model

- **Source:** U.S. DOE **AFDC** station locations CSV (filtered to `Fuel Type Code = ELEC`)
- **Schema (simplified):**
  - `stations(station_id, station_name, network, status, address, city, state, zip, latitude, longitude, access, level2_ports, dcfc_ports, ...)`
  - `connectors(station_id, type)` where `type ∈ {J1772, CCS, CHADEMO, TESLA/NACS}`
- API responses alias DB columns:
  - `station_id → id`
  - `station_name → name`

---

## Quickstart (Local)

```bash
# 1) Install dependencies
python -m pip install -r requirements.txt

# 2) Build the database (if you don't commit data/ev.db)
python backend/etl.py

# 3) Run the API (http://127.0.0.1:8000)
python -m uvicorn backend.main:app --reload

# 4) Serve the UI in another terminal (http://127.0.0.1:5500/index.html)
cd frontend
python -m http.server 5500
```

**Windows (CMD) helper:**
```bat
python -m uvicorn backend.main:app --reload
cd frontend && python -m http.server 5500
start "" http://127.0.0.1:5500/index.html
```

---

## API

### Docs
- Swagger UI: **`GET /docs`**
- OpenAPI JSON: **`GET /openapi.json`**

### Endpoints

#### `GET /stations` — Find nearby stations
**Query params**
- `lat` (float) — latitude
- `lon` (float) — longitude
- `radius_km` (float, default `10`, ≤ `200`)
- `state` (str, optional; e.g., `CA`)
- `dcfc_only` (bool, default `false`)
- `connector` (repeatable or comma-separated; e.g., `connector=CCS&connector=TESLA/NACS` or `connector=CCS,CHADEMO`)
- `limit` (int, default `100`, ≤ `500`)

**Response (example)**
```json
{
  "count": 3,
  "results": [
    {
      "id": 12345,
      "name": "Station Name",
      "network": "ChargePoint",
      "address": "123 Main St",
      "city": "San Francisco",
      "state": "CA",
      "latitude": 37.78,
      "longitude": -122.41,
      "level2_ports": 4,
      "dcfc_ports": 2,
      "distance_km": 1.23
    }
  ]
}
```

#### `GET /stations/{id}` — Station details
**Response (example)**
```json
{
  "station_id": 12345,
  "station_name": "Station Name",
  "connectors": ["CCS", "TESLA/NACS"],
  "address": "123 Main St",
  "city": "San Francisco",
  "state": "CA",
  "dcfc_ports": 2,
  "level2_ports": 4,
  "latitude": 37.78,
  "longitude": -122.41
}
```

**Examples**
```bash
# Nearby DC fast, CCS, 15 km around downtown SF
curl "http://127.0.0.1:8000/stations?lat=37.7749&lon=-122.4194&radius_km=15&dcfc_only=true&connector=CCS"

# Station details
curl "http://127.0.0.1:8000/stations/12345"
```

---

## Frontend

- Single `index.html` served statically (no build tools)
- **Leaflet** + **MarkerCluster** via CDN
- Sidebar with filters, “search as I move”, results list
- Connector badges fetched via `/stations/{id}`

**Point the UI to a deployed API** by editing this line in `frontend/index.html`:
```html
<code id="apiBase">https://YOUR-BACKEND-URL</code>
```

---

## ☁Deploy

### Backend (Render)
- **Build**: `pip install -r requirements.txt`
- **Start**: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
- **Auto-deploy**: enable redeploy on push

**Data options**
- **Option A (simple)** — commit `data/ev.db`
- **Option B (preferred)** — commit `data/afdc_stations.csv` and let the app **build DB on first boot**  
  (lifespan hook in `backend/main.py` can call `etl.build_db(...)` if `ev.db` is missing)

### Frontend (Netlify / Vercel)
- **Publish directory**: `frontend/`
- After deploy, set `<code id="apiBase">…</code>` to your backend URL and push → site redeploys.

---

## Testing (smoke)

Create `tests/test_api.py`:
```python
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_health():
    assert client.get("/health").status_code == 200

def test_stations_baseline():
    r = client.get("/stations", params={"lat":37.7749,"lon":-122.4194,"radius_km":5})
    assert r.status_code == 200
    assert "results" in r.json()
```

Run:
```bash
python -m pip install pytest
pytest -q
```

---

## Development Notes

- API: `python -m uvicorn backend.main:app --reload`
- UI:  `python -m http.server 5500 -d frontend`

**Common gotchas**
- Import error `code.main` → ensure folder is named `backend` (not `code`)
- DB mismatch → ensure ETL and API use the same `data/ev.db`
- CORS for prod → restrict `allow_origins` in `CORSMiddleware` to your frontend domain

---

## Contributing

Issues and PRs are welcome. Consider **Conventional Commits** (`feat:`, `fix:`, `docs:`) to keep history tidy.

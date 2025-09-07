# EV Charging Stations — REST API & Map UI

[![FastAPI](https://img.shields.io/badge/API-FastAPI-009688)](#)
[![SQLite](https://img.shields.io/badge/DB-SQLite-003B57)](#)
[![Leaflet](https://img.shields.io/badge/Map-Leaflet-199900)](#)
[![Tests](https://img.shields.io/badge/Tests-Pytest-6C7A89)](#)

A compact, production-style project that exposes a **FastAPI** REST service backed by **SQLite** and a zero-build **Leaflet** web UI. It supports nearby search, connector filtering (CCS / Tesla-NACS / CHAdeMO / J1772), and returns clean, documented JSON.

**Live API docs:** https://ev-charging-api-2djx.onrender.com/docs

---

## Tech Stack

- **Backend:** FastAPI, Uvicorn, SQLite
- **Data:** U.S. DOE AFDC open dataset (EV stations)
- **Frontend:** Static HTML + Leaflet (CDN), MarkerCluster
- **Hosting:** Render (API), Netlify/Vercel (static UI)

---

## Features

- Geospatial search by lat/lon + radius (km)
- Filters: DC fast only, connector type(s)
- Station detail with connector list
- OpenAPI/Swagger documentation
- Minimal footprint, no frontend build step

---

## API Reference

**Base URL:** https://ev-charging-api-2djx.onrender.com

### `GET /stations` — Nearby search
| Query | Type | Default | Notes |
|---|---|---:|---|
| `lat` | float | — | Latitude |
| `lon` | float | — | Longitude |
| `radius_km` | float | 10 | ≤ 200 |
| `state` | string | — | Optional (e.g. `CA`) |
| `dcfc_only` | bool | false | Only DC fast chargers |
| `connector` | string \| repeated | — | e.g. `CCS`, `TESLA/NACS`, `CHADEMO`, `J1772` |
| `limit` | int | 100 | ≤ 500 |

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

### `GET /stations/{id}` — Station detail

**Response (example)**
```json
{
  "id": 12345,
  "name": "Station Name",
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

---

## Projetc Structure

```text
restapi_evcharge/
├─ backend/
│  ├─ main.py            # FastAPI app (endpoints, models, CORS, docs)
│  ├─ etl.py             # CSV → SQLite loader
│  ├─ schema.sql         # DB schema (stations, connectors)
│  └─ __init__.py
├─ data/
│  ├─ afdc_stations.csv  # Source CSV (kept for ETL / bootstrapping)
│  └─ ev.db              # SQLite DB (bundled for deploy)
├─ frontend/
│  └─ index.html         # Zero-build Leaflet UI (CDN assets)
├─ requirements.txt
├─ CHANGELOG.md
├─ README.md
└─ .gitignore
```

---

## Live Map

**UI:** https://ev-charger-api.netlify.app

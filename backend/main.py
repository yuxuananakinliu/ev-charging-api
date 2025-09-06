# main.py — clean REST API (FastAPI + SQLite)
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
from pathlib import Path
import sqlite3, math
from pydantic import BaseModel


# ---- docs ----
class Station(BaseModel):
    id: int
    name: Optional[str] = None
    network: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip: Optional[str] = None
    latitude: float
    longitude: float
    access: Optional[str] = None
    level2_ports: Optional[int] = 0
    dcfc_ports: Optional[int] = 0
    distance_km: Optional[float] = None

class StationsResponse(BaseModel):
    count: int
    results: List[Station]


# ---- paths ----
CODE_DIR = Path(__file__).resolve().parent
ROOT_DIR = CODE_DIR.parent
DB_PATH  = ROOT_DIR / "data" / "ev.db"


# ---- app ----
app = FastAPI(title="EV Charging API", version="v1")

# CORS (open for dev; tighten in prod)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---- helpers ----
def db():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    return 2 * R * math.asin(math.sqrt(a))

def normalize_connector_params(connector_param):
    """Accept ?connector=CCS&connector=TESLA/NACS or ?connector=CCS,CHADEMO"""
    if not connector_param:
        return []
    items = []
    for item in connector_param:
        parts = [p.strip().upper() for p in item.split(",") if p.strip()]
        items.extend(parts)
    return sorted(set(items))


# ---- routes ----
@app.get("/health")
def health():
    return {"ok": True}

@app.get("/stations",
         response_model=StationsResponse,
         summary="Find nearby EV charging stations",
         tags=["stations"])
def stations(
    lat: float = Query(..., description="Your latitude"),
    lon: float = Query(..., description="Your longitude"),
    radius_km: float = Query(10, gt=0, le=200, description="Search radius in km"),
    limit: int = Query(100, gt=1, le=500),
    state: Optional[str] = None,
    connector: Optional[List[str]] = Query(None),   # ?connector=CCS&connector=TESLA/NACS or ?connector=CCS,CHADEMO
    dcfc_only: bool = False
):
    con = db()

    # quick bounding box prefilter (faster than full table scan)
    dlat = radius_km / 111.0
    dlon = radius_km / (111.0 * max(0.1, math.cos(math.radians(lat))))

    sql = (
        f"SELECT s.station_id, "
        f"       s.station_name, "
        f"       s.network, s.status, s.address, s.city, s.state, s.zip, "
        f"       s.latitude, s.longitude, s.access, s.level2_ports, s.dcfc_ports "
        f"FROM stations s "
        f"WHERE s.latitude BETWEEN ? AND ? AND s.longitude BETWEEN ? AND ?"
    )
    params: List[object] = [lat - dlat, lat + dlat, lon - dlon, lon + dlon]

    if state:
        sql += " AND s.state = ?"
        params.append(state.upper())

    if dcfc_only:
        sql += " AND s.dcfc_ports > 0"

    wanted = normalize_connector_params(connector)
    if wanted:
        placeholders = ",".join(["?"] * len(wanted))
        sql += (
            f" AND EXISTS (SELECT 1 FROM connectors c "
            f"            WHERE c.station_id = s.station_id"
            f"              AND c.type IN ({placeholders}))"
        )
        params.extend(wanted)

    rows = [dict(r) for r in con.execute(sql, params).fetchall()]

    # precise radius filter + sort + limit
    for r in rows:
        r["distance_km"] = round(haversine_km(lat, lon, r["latitude"], r["longitude"]), 2)
    rows = [r for r in rows if r["distance_km"] <= radius_km]
    rows.sort(key=lambda r: r["distance_km"])
    return {"count": min(len(rows), limit), "results": rows[:limit]}

@app.get("/stations/{sid}",
         response_model=Station,
         summary="Get a station by id",
         tags=["stations"],
         responses={404: {"description": "Not found"}})
def station_detail(sid: int):
    con = db()
    st = con.execute(f"SELECT * FROM stations WHERE station_id = ?", (sid,)).fetchone()
    if not st:
        raise HTTPException(status_code=404, detail="Not found")
    cons = con.execute("SELECT type FROM connectors WHERE station_id = ?", (sid,)).fetchall()
    out = dict(st)
    out["id"] = out.get('station_id', sid)
    out["name"] = out.get('station_name', out.get("name"))
    out["connectors"] = [c["type"] for c in cons]
    return out
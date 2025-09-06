import csv, sqlite3
from pathlib import Path


CODE_DIR = Path(__file__).resolve().parent
ROOT_DIR = CODE_DIR.parent
DB_PATH  = ROOT_DIR / "data" / "ev.db"
CSV_PATH = ROOT_DIR / "data" / "afdc_stations.csv"
SCHEMA   = ROOT_DIR / "schema.sql"


def connect_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def init_db(conn):
    sql = SCHEMA.read_text(encoding="utf-8")
    conn.executescript(sql)
    conn.commit()

def to_int(x):
    try:
        return int(x)
    except (TypeError, ValueError):
        return 0

CONNECTOR_MAP = {
    "J1772": "J1772",
    "J1772COMBO": "CCS",
    "CCS": "CCS",
    "CHADEMO": "CHADEMO",
    "TESLA": "TESLA/NACS",
    "NACS": "TESLA/NACS",
}

def parse_connectors(raw):
    if not raw:
        return []
    raw = raw.replace("|", ",").replace("/", ",")  # Standardize splits
    tokens = [t.strip().upper() for t in raw.split(",") if t.strip()]
    out = set()
    for t in tokens:
        for k, v in CONNECTOR_MAP.items():
            if k in t:
                out.add(v)
    return sorted(out)


def main():
    conn = connect_db()
    init_db(conn)

    with CSV_PATH.open(newline='', encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        cur = conn.cursor()
        rows_inserted = 0

        for row in reader:

            # 2) Map CSV
            station_name = row.get("Station Name")
            network = row.get("EV Network")
            status = row.get("Status Code")
            address = row.get("Street Address")
            city = row.get("City")
            state = (row.get("State") or "").upper()
            zipc = row.get("ZIP")

            access = row.get("Access Days Time")
            level2 = to_int(row.get("EV Level2 EVSE Num"))
            dcfc = to_int(row.get("EV DC Fast Count"))

            # Coordinates (skip rows with bad/missing lat/lon)
            try:
                lat = float(row.get("Latitude"))
                lon = float(row.get("Longitude"))
            except (TypeError, ValueError):
                continue

            # Insert station
            cur.execute("""
                INSERT INTO stations
                (station_name, network, status, address, city, state, zip, latitude, longitude, access, level2_ports, dcfc_ports)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
            """, (
                station_name, network, status, address, city, 
                state, zipc, lat, lon, access, level2, dcfc
            ))
            sid = cur.lastrowid

            # Insert connectors
            for c in parse_connectors(row.get("EV Connector Types")):
                cur.execute(
                    "INSERT INTO connectors (station_id, type) VALUES (?,?)", 
                    (sid, c)
                )

            rows_inserted += 1

        conn.commit()
        print(f"Inserted {rows_inserted} stations.")



if __name__ == "__main__":
    main()
CREATE TABLE IF NOT EXISTS stations (
  station_id INTEGER PRIMARY KEY AUTOINCREMENT,
  station_name TEXT,
  network TEXT,
  status TEXT,
  address TEXT,
  city TEXT,
  state TEXT,
  zip TEXT,
  latitude REAL,
  longitude REAL,
  access TEXT,
  level2_ports INTEGER,
  dcfc_ports INTEGER
);

CREATE TABLE IF NOT EXISTS connectors (
  station_id INTEGER,
  type TEXT,
  FOREIGN KEY(station_id) REFERENCES stations(id)
);
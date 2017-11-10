CREATE TABLE IF NOT EXISTS tvshow (
  id      TEXT PRIMARY KEY,
  name    TEXT,
  quality TEXT
);


CREATE TABLE IF NOT EXISTS episode (
  tvshow_id          TEXT,
  season             INTEGER,
  number             INTEGER,
  title              TEXT,
  state              TEXT,
  link               TEXT,
  quality            TEXT,
  download_timestamp TEXT,

  FOREIGN KEY (tvshow_id) REFERENCES tvshow,

  PRIMARY KEY (tvshow_id, season, number)
);

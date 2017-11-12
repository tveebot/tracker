CREATE TABLE IF NOT EXISTS tvshow (
  id      TEXT PRIMARY KEY,
  name    TEXT,
  quality TEXT
);


CREATE TABLE IF NOT EXISTS episode (
  tvshow_id          TEXT,
  season             INTEGER,
  number             INTEGER,
  title              TEXT NOT NULL,
  state              TEXT,

  FOREIGN KEY (tvshow_id) REFERENCES tvshow,

  PRIMARY KEY (tvshow_id, season, number)
);


CREATE TABLE IF NOT EXISTS file (
  tvshow_id          TEXT NOT NULL,
  season             INTEGER NOT NULL,
  number             INTEGER NOT NULL,
  link               TEXT NOT NULL,
  quality            TEXT NOT NULL,
  download_timestamp TEXT,

  FOREIGN KEY (tvshow_id, season, number) REFERENCES episode,

  PRIMARY KEY (tvshow_id, season, number)
);


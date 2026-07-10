DROP TABLE IF EXISTS climate;

CREATE TABLE climate (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TIMESTAMP NOT NULL DEFAULT (datetime('now','localtime')),
    temperature REAL NOT NULL,
    humidity REAL NOT NULL
);
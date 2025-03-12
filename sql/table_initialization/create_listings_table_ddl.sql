CREATE TABLE IF NOT EXISTS listings (
    source VARCHAR(100),
    post_date DATETIME,
    post_url TEXT,
    indexed_on DATETIME DEFAULT CURRENT_TIMESTAMP,
    id INTEGER,
    status TEXT DEFAULT 'pending',
    PRIMARY KEY (source, post_date, post_url),
    FOREIGN KEY (id) REFERENCES jobs(id)
);
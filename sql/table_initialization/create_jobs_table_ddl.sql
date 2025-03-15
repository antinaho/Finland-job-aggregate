CREATE TABLE IF NOT EXISTS jobs (
    indexed_on DATETIME DEFAULT CURRENT_TIMESTAMP,

    source TEXT,
    post_date DATETIME,
    post_url TEXT,

    title TEXT,
    company TEXT,
    location TEXT,
    description TEXT,
    apply_url TEXT,

    PRIMARY KEY(source, post_date, post_url)
);
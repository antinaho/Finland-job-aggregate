INSERT OR IGNORE INTO jobs (
    source,
    post_date,
    title,
    company,
    location,
    description,
    apply_url
) VALUES (
    ?, ?, ?, ?, ?, ?, ?
);
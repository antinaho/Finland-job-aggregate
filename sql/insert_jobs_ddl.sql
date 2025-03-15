INSERT OR IGNORE INTO jobs (
    source,
    post_date,
    post_url,
    title,
    company,
    location,
    description,
    apply_url
) VALUES (
    ?, ?, ?, ?, ?, ?, ?, ?
);
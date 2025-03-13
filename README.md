# Finland Job Board scraper

This web scraper collects job postings from popular Finnish job sites and compiles them into a structured database.

## Usage

1. Clone the repository:
   ```sh
   git clone https://github.com/antinaho/Finland-job-aggregate.git
   cd Finland-job-aggregate
   ```

2. Build and run using Docker-compose, defaults to scraping the current day
    ```sh
    docker-compose build
    docker-compose up
    ```

    To scrape a custom date use the following command:
    ```sh
    DATE=2025-01-01 docker-compose up
    ```

3. Scraper closes once it has scraped the given day. You can shut it down early using
   ```sh
    docker-compose down
    ```

## Accessing scraped data

Results are stored in the SQLite3 database that gets created in the database-folder

You can access the database from the terminal by using:

```sh
sqlite3 database/app.db
```

Progrem inserts the data into a table called **jobs**

**jobs**: Stores the source of the job post and post date. Additionally stores title, company, location, apply link, etc.

## Using scraped data

You can find relevant jobs by querying important keywords from the database. For example you can find jobs where you would be using C++ by querying:

```sh
SELECT title, company, location, apply_url FROM jobs WHERE description LIKE '%C++%'
```

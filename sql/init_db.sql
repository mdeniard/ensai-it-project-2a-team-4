-- Database initialization script
-- Run it once on your own database (pgAdmin > Query Tool, or psql -f sql/init_db.sql)
-- Tables are created in the schema set by POSTGRES_SCHEMA in your .env

CREATE TABLE IF NOT EXISTS movie (
    id            SERIAL PRIMARY KEY,
    tmdb_id       INTEGER UNIQUE NOT NULL,
    title         VARCHAR(255) NOT NULL,
    description   TEXT,
    duration      SMALLINT,
    released_date DATE,
    rating        NUMERIC(4, 2),
    poster_url    VARCHAR(500)
);

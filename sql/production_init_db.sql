-- Database initialization script
-- Run it once on your own database (pgAdmin > Query Tool, or psql -f sql/init_db.sql)
-- Tables are created in the schema set by POSTGRES_SCHEMA in your .env

-- Movies
CREATE TABLE IF NOT EXISTS movies (
    id            SERIAL PRIMARY KEY,
    tmdb_id       INTEGER UNIQUE NOT NULL,
    title         VARCHAR(255) NOT NULL,
    description   TEXT,
    duration      SMALLINT,
    released_date DATE,
    rating        NUMERIC(4, 2),
    poster_url    VARCHAR(500)
);

INSERT INTO movies (tmdb_id, title, description, duration, released_date, duration, rating, poster_url) VALUES
;

-- Users
CREATE TABLE IF NOT EXISTS users (
    id            SERIAL PRIMARY KEY,
    username      TEXT NOT NULL UNIQUE,
    email         TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    salt          TEXT NOT NULL,
    first_name    TEXT,
    last_name     TEXT,
    is_admin      BOOLEAN NOT NULL DEFAULT FALSE
);

INSERT INTO users (username, email, password_hash, salt, first_name, last_name, is_admin) VALUES
;

-- Rooms
CREATE TABLE IF NOT EXISTS rooms (
    id          SERIAL PRIMARY KEY,
    room_number INT NOT NULL UNIQUE,
    capacity    INT NOT NULL CHECK (capacity > 0)
);

INSERT INTO rooms (room_number, capacity) VALUES
(1, 319),
(2, 196),
(3, 155),
(4, 122),
(5, 119),
(6, 80);

-- Screenings
CREATE TABLE IF NOT EXISTS screenings (
    id         SERIAL PRIMARY KEY,
    movie_id   INT NOT NULL REFERENCES movies(id) ON DELETE CASCADE,
    room_id    INT NOT NULL REFERENCES rooms(id)  ON DELETE CASCADE,
    start_time TIMESTAMPTZ NOT NULL,
    end_time   TIMESTAMPTZ NOT NULL,
    CHECK (end_time > start_time)
);

INSERT INTO screenings (movie_id, room_id, start_time, end_time) VALUES
;

-- Tickets

-- Reservations


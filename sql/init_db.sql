-- Database initialization script

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

-- Rooms
CREATE TABLE IF NOT EXISTS rooms (
    id          SERIAL PRIMARY KEY,
    room_number INT NOT NULL UNIQUE,
    capacity    INT NOT NULL CHECK (capacity > 0)
);

-- Screenings
CREATE TABLE IF NOT EXISTS screenings (
    id         SERIAL PRIMARY KEY,
    movie_id   INT NOT NULL REFERENCES movies(id) ON DELETE CASCADE,
    room_id    INT NOT NULL REFERENCES rooms(id)  ON DELETE CASCADE,
    start_time TIMESTAMPTZ NOT NULL,
    end_time   TIMESTAMPTZ NOT NULL,
    CHECK (end_time > start_time)
);

-- Ticket Types
CREATE TABLE IF NOT EXISTS ticket_types (
    id                  SERIAL PRIMARY KEY,
    name                TEXT NOT NULL UNIQUE,
    price_multiplier    NUMERIC(4, 2),
    active              BOOLEAN
);

-- Reservations
CREATE TABLE IF NOT EXISTS reservations (
    id               SERIAL PRIMARY KEY,
    customer_id      INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    screening_id     INT NOT NULL REFERENCES screenings(id)  ON DELETE CASCADE,
    ticket_type_id   INT NOT NULL REFERENCES ticket_types(id) ON DELETE CASCADE,
    reserved_at      TIMESTAMPTZ NOT NULL,
);
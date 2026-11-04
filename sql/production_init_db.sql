-- Production database initialization script (tables + demo data)
-- WARNING: when you change a table here, change it in test_init_db.sql too

CREATE SCHEMA IF NOT EXISTS production;
SET search_path TO production;

-- Movies ----------------------------------
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

INSERT INTO movies (tmdb_id, title, description, duration, released_date, rating, poster_url) VALUES
(1170608, 'Dune: Part Three',
 'Nearly two decades after he seized control of the Imperium, Paul Atreides is now a ruthless Emperor, and must face the consequences of his reign as old allies return, terrifying new threats emerge, and betrayal lurks in every shadow. Haunted by visions of Imperial collapse and the reappearance of his long-lost love, Paul is drawn into a sweeping conspiracy, with Chani at the heart of its unfolding mystery. As enemies close in, Paul must confront the true cost of power and the fate of those he loves the most.',
 150, '2026-12-15', 0, 'https://image.tmdb.org/t/p/w500/glt0v4I89rMWstDNCaFXc5SNyO1.jpg'),

(1567605, 'Ebenezer',
 'An elderly miser embarks on a supernatural journey after visits from the ghost of his former business partner and the Spirits of Christmas Past, Present, and Yet to Come force him to confront his past and fight for a second chance at happiness.',
 115, '2026-11-11', 0, 'https://image.tmdb.org/t/p/w500/6H2N59jJW1hZEzn2ZdrMvJw5vNI.jpg'),

(1003596, 'Avengers: Doomsday',
 'Beloved heroes from three distinct universes are set on a deadly collision course and face an existential threat unlike anything they''ve ever encountered.',
 165, '2026-12-16', 0, 'https://image.tmdb.org/t/p/w500/jzPwsojjFStf5lR5Nm07w2hH56G.jpg'),

(1255833, 'Whalefall',
 'Following the death of his father, Jay Gardiner goes diving off the central Coast of California in search of his remains, but is swallowed by a massive sperm whale. While trapped inside its belly with only one hour of oxygen left, Jay comes to realize that the hard-earned lessons his father imparted may be the key to his escape.',
 106, '2026-10-14', 6.56, 'https://image.tmdb.org/t/p/w500/vjTYUTgh9nO88i6HZ4YPRhiFL05.jpg'),

(1507877, 'Another Day',
 'Garance is a young actress, but not a star. She manages everything as best she can, valiant, cheerful, a soldier, and she finds in alcohol an unconditional fuel, a source of comfort. Garance changes her life and begins an eight-year journey of moves, work, encounters, parties and anxieties, joys and hardships… An intimate, friendly, and sexual revolution. But she consumes, more and more. Until the very possibility of death…',
 120, '2026-09-23', 7.01, 'https://image.tmdb.org/t/p/w500/xU8iyvhGQQIU9geuFxPbyNquhdX.jpg'),

(1263337, 'Heart of the Beast',
 'After a harrowing plane crash, Special Forces officer James Belmont and his combat dog, Odin, find themselves stranded deep in the Alaskan wilderness. Together, they are forced into a brutal fight for survival against the elements.',
 101, '2026-09-19', 7.31, 'https://image.tmdb.org/t/p/w500/1ApfSA8JTqeha3GTFEY8syV4auq.jpg'),

(1437925, 'Moulin',
 'In June 1943, Jean Moulin, leader of the French Resistance, is arrested while attempting to reunite the forces of the "Armée Secrète." Interrogated by Klaus Barbie, the head of the Gestapo in Lyon, Moulin is drawn into a relentless confrontation.',
 130, '2026-10-28', 6.16, 'https://image.tmdb.org/t/p/w500/f3yopLJXRBcPvgkfRji1jloDrxd.jpg'),

(1381071, 'Godzilla Minus Zero',
 'War reduced Japan to zero, and Godzilla plunged it into minus. Two years have passed since then, and the country has faced agonizing struggles to achieve recovery and finally reclaim its daily life. Just as humanity managed to cling to a hard-won peace, a new threat strikes, crushing hope in an instant. There is no third time. Everything ends here.',
 135, '2026-11-03', 9.50, 'https://image.tmdb.org/t/p/w500/hSmIJluOJmTWvJs4d7kHRxjc8s8.jpg'),

(1300968, 'The Hunger Games: Sunrise on the Reaping',
 'Return to the world of Panem 24 years before the events of The Hunger Games, starting on the morning of the reaping of the 50th Hunger Games, also known as the Second Quarter Quell.',
 159, '2026-11-18', 0, 'https://image.tmdb.org/t/p/w500/jNcZH8yplxttRlf0wwqfGGMKHxX.jpg'),

(1084728, 'Asterix: The Kingdom of Nubia',
 'The irreductible Gauls are turned into harmless children after a rare youth elixir accidentally ends up into the magic potion. To find the antidote and save the village from the Romans attack, Asterix and Obelix embark on a crazy journey to the far away Kingdom of Nubia.',
 86, '2026-12-02', 0, 'https://image.tmdb.org/t/p/w500/mxDsm7jKW1G7LNTtvp1C0ID9gN5.jpg')
ON CONFLICT (tmdb_id) DO NOTHING;

-- Users ----------------------------------
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
-- admin password : admin#26
('admin', 'admin@cinema.fr', '82a3977792e4fe40ddb6c4d5a4ecde3dbdc0d35fbcae4d0d1ddcf2386b92b28a', '541bb1e7f6f12049da3370719618d5a4e870f93b77cee0c4bbfd1cd3b028782c5cdb7d5f411bf4ba1b6503503ffecbaddf6f8a6b69cfd27735ae38f2c619319c4f2d6e9dc8ec712032aa29dbbf8e8f08c7a79d911a792c16d21474bb6a5924227a09a7bdb0569951f2f19b1436e7f941db5ac648c319b021b6c44f495f21a29f', 'Admin', 'Admin', TRUE),
-- john password : john_johnson&26
('john',   'john@example.com', '70db02744017929790964961873d51e58c26177fad30e10d21f57a998835848a', '63bc5656b9faa25ef42a299de3a97863d56bbaf9121aeb8382c58b411121623c7819ca7e99bdd0a0f019fa7d0f80abb3a879bd5411a6680daea5197507d3a8e95f688a6e0af83dfbe9aad6daab8d3e3a801f591934e55f4084ff22bdf909c0dc592c89ab6851f36f6a8d2679826c0793797cf93f6e4401dd1ecf5dd4af1b9bf3', 'John', 'Johnson', FALSE),
-- mary password : mary_smith&26
('mary',   'mary@example.com', 'd9bee6e496a4f21a1a3527a758be41efc7bce350cd1d9875ae46ebdbea66e7d8', '87b678d506af8c688194f7f3c792954fde0ce82678642ed0626bef3f687cce936f892af708f1e71141e33ee6a42d1e9676d16a79e1fec01014a23cab77671d045f006c2f5a1bc65af8c81b01a1f4fca23d54cc4d6818ad9fcd302984b3c15b6e4811a726e255bb2478762d8797ca43b815e5ee8b3ca565b5536dd66578dcfb77', 'Mary', 'Smith', FALSE)
ON CONFLICT (username) DO NOTHING;

-- Rooms ----------------------------------
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
(6, 80)
ON CONFLICT (room_number) DO NOTHING;

-- Screenings -----------------------------
CREATE TABLE IF NOT EXISTS screenings (
    id         SERIAL PRIMARY KEY,
    movie_id   INT NOT NULL REFERENCES movies(id) ON DELETE CASCADE,
    room_id    INT NOT NULL REFERENCES rooms(id)  ON DELETE CASCADE,
    start_time TIMESTAMPTZ NOT NULL,
    end_time   TIMESTAMPTZ NOT NULL,
    CHECK (end_time > start_time)
);

INSERT INTO screenings (movie_id, room_id, start_time, end_time)
SELECT m.id,
       r.id,
       (d.day + t.local_time) AT TIME ZONE 'Europe/Paris',
       (d.day + t.local_time) AT TIME ZONE 'Europe/Paris'
           + (m.duration + 20) * INTERVAL '1 minute'
FROM (VALUES
    -- room_number, tmdb_id, time zone (Paris)
    (1, 1381071, TIME '14:00'),  -- Godzilla Minus Zero
    (1, 1437925, TIME '17:00'),  -- Moulin
    (1, 1255833, TIME '20:00'),  -- Whalefall

    (2, 1507877, TIME '14:00'),  -- Another Day
    (2, 1263337, TIME '16:45'),  -- Heart of the Beast
    (2, 1381071, TIME '19:30'),  -- Godzilla Minus Zero

    (3, 1437925, TIME '15:00'),  -- Moulin
    (3, 1255833, TIME '18:00'),  -- Whalefall
    (3, 1507877, TIME '20:30'),  -- Another Day

    (4, 1263337, TIME '14:30'),  -- Heart of the Beast
    (4, 1381071, TIME '17:00'),  -- Godzilla Minus Zero
    (4, 1437925, TIME '20:00'),  -- Moulin

    (5, 1255833, TIME '16:00'),  -- Whalefall
    (5, 1507877, TIME '18:30'),  -- Another Day
    (5, 1263337, TIME '21:15'),  -- Heart of the Beast

    (6, 1263337, TIME '15:00'),  -- Heart of the Beast
    (6, 1255833, TIME '17:30'),  -- Whalefall
    (6, 1437925, TIME '20:00')   -- Moulin
) AS t(room_number, tmdb_id, local_time)
JOIN rooms  r ON r.room_number = t.room_number
JOIN movies m ON m.tmdb_id     = t.tmdb_id
CROSS JOIN (
    -- 7 days from November 5th
    SELECT (DATE '2026-11-05' + n) AS day FROM generate_series(0, 6) AS n
) d
WHERE NOT EXISTS (
    SELECT 1 FROM screenings s
    WHERE s.room_id = r.id
      AND s.start_time = (d.day + t.local_time) AT TIME ZONE 'Europe/Paris'
);

-- Ticket Types ---------------------------
CREATE TABLE IF NOT EXISTS ticket_types (
    id                  SERIAL PRIMARY KEY,
    name                TEXT NOT NULL UNIQUE,
    price_multiplier    NUMERIC(4, 2),
    active              BOOLEAN
);

INSERT INTO ticket_types (name, price_multiplier, active) VALUES
('Normal', 1.0, TRUE),
('Child', 0.6, TRUE),
('Student', 0.8, TRUE),
('Senior', 0.9, TRUE)
ON CONFLICT (name) DO NOTHING;


-- Reservations --------------------------
CREATE TABLE IF NOT EXISTS reservations (
    id               SERIAL PRIMARY KEY,
    customer_id      INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    screening_id     INT NOT NULL REFERENCES screenings(id)  ON DELETE CASCADE,
    ticket_type_id   INT NOT NULL REFERENCES ticket_types(id) ON DELETE CASCADE,
    reserved_at      TIMESTAMPTZ NOT NULL
);


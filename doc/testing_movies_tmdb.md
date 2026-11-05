# Testing the import of movies from TMDB on the `test` schema

This guide explains how to check by hand that the administrator can search movies on TMDB
and import them into our catalogue.
It uses the `test` schema, so the demo data of the `production` schema is never modified.

How it works:
1. `GET /movies/search` asks TMDB for the movies matching a title, so that the administrator can choose the right one.
2. `POST /movies/import/{tmdb_id}` gets the full details of the chosen movie from TMDB (title, duration, poster...)
   and saves it in our `movies` table.

## 1. Prepare the database and the application

1. Get a TMDB API key: create an account on https://www.themoviedb.org, then go to
   **Settings → API** and copy the **API Key** (not the long "Read Access Token").
2. In your `.env` file, set:
   ```
   POSTGRES_SCHEMA=test
   TMDB_API_KEY=your_key_here
   ```
   The `.env` file must **never** be committed (it contains your key).
3. In pgAdmin, run `sql/test_init_db.sql` (Query Tool → paste the script → ▶).
   If the `test` schema already exists, first run `DROP SCHEMA test CASCADE;`
4. In the terminal, from the project folder, run `pdm install`, then `pdm start`.
   If the server was already running, restart it so that it reads the new `.env`.
5. Open **http://localhost:8000/docs**.

## 2. Search a movie on TMDB

Open `GET /movies/search` → **Try it out** → fill the parameters → **Execute**.

| Parameters | Expected result |
|---|---|
| `title` = `Inception` | **200**, a list of movies. The first one has `"tmdb_id": 27205` and `"title": "Inception"` |
| `title` = `The Wild Robot`, `year` = `2024` | **200**, the list contains `"tmdb_id": 1184918` |
| `title` = `Dune`, without year, then with `year` = `2021` | **200**, the second list is shorter: the year reduces ambiguity |
| `title` = `xqzwvkjh` | **200** and an empty list `[]` (no movie found, this is not an error) |
| `title` = `   ` (only spaces) | **400** "The title must not be empty" |

Each movie of the list looks like this:

```json
{
  "tmdb_id": 27205,
  "title": "Inception",
  "release_date": "2010-07-15",
  "overview": "Cobb, a skilled thief who commits corporate espionage...",
  "poster_url": "https://image.tmdb.org/t/p/w500/...jpg"
}
```

Click on the `poster_url`: the poster of the movie opens in the browser.

## 3. Import a movie into our catalogue

Open `POST /movies/import/{tmdb_id}` → **Try it out** → fill `tmdb_id` → **Execute**.

| `tmdb_id` | Expected result |
|---|---|
| `27205` | **201**, the movie Inception, with `"id": 1` (its id in **our** database) and its `duration` in minutes |
| `1184918` | **201**, The Wild Robot, with `"id": 2` |
| `27205` again | **409** "Movie with tmdb_id [27205] is already in the catalogue" (no duplicate is created) |
| `999999999` | **404** "Movie with tmdb_id [999999999] not found on TMDB" |

Note the difference between the two ids:
- `tmdb_id` is the id of the movie **on TMDB** (27205 for Inception);
- `id` is the id of the movie **in our database** (1, 2, 3...). This is the one used to create screenings (`"movie_id": 1`).

## 4. Check that the movie is really saved

**In the Swagger:**
- `GET /movies/` → **200** and the list of the 2 imported movies.
- `GET /movies/{tmdb_id}` with `1` (despite its name, this parameter is the id of **our** database)
  → **200** and the movie Inception.

**In pgAdmin:**

```sql
SELECT id, tmdb_id, title, duration, released_date, rating FROM test.movies;
```

You should see exactly 2 rows (Inception and The Wild Robot): the duplicate import of step 3 was refused.

## 5. Check the error when the API key is wrong

1. In `.env`, change one character of `TMDB_API_KEY`, then restart the server.
2. `GET /movies/search` with `title` = `Inception`
   → **400** "Error while searching on TMDB: 401 Client Error: Unauthorized..."
3. Put the right key back and restart the server.

## 6. Unit tests (without internet and without database)

The tests replace TMDB and the database by fake objects (mocks), so they work without the API key:

```
pdm run pytest tests/DAO/test_MovieDBConnector.py tests/Service/test_MovieService.py -v
```

All the tests must pass (`passed`).

## Known limits

- The `/movies/search` and `/movies/import` routes are marked "Admin Only", but they do not check the token yet:
  anybody can call them.

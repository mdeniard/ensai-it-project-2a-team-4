# Testing the reservations (F2) on the `test` schema

This guide explains how to test the whole booking feature by hand, from an empty database to a full room,
including the price of the tickets.
It uses the `test` schema, so the demo data of the `production` schema is never modified.

## 1. Prepare the database and the application

1. In pgAdmin, run `sql/test_init_db.sql` (Query Tool → paste the script → ▶). It creates the `test` schema with empty tables.
   If the `test` schema already exists from an older version of the script, first run `DROP SCHEMA test CASCADE;`
   (`CREATE TABLE IF NOT EXISTS` does not add the new columns to an existing table).
2. In your `.env` file, set `POSTGRES_SCHEMA=test`.
3. In the terminal, from the project folder, run `pdm install`, then `pdm start`.
4. Open **http://localhost:8000/docs**.

## 2. Create the ticket types (pgAdmin)

There is no endpoint for the ticket types yet, so we add them with SQL:

```sql
INSERT INTO test.ticket_types (name, price_multiplier, active) VALUES
('Normal', 1.0, TRUE),
('Old', 0.5, FALSE),
('ENSAI Student', 0.8, TRUE);
```

Ticket types 1 and 3 are active, ticket type 2 is not.

The price of a ticket is: **base price of the screening × `price_multiplier` of the ticket type**.

## 3. Create the data (Swagger)

For each endpoint: **Try it out** → paste the JSON → **Execute**.

| Endpoint | JSON / parameter | Result |
|---|---|---|
| `POST /users` | `{"username": "alice", "email": "alice@test.fr", "password": "password123", "first_name": "Alice", "last_name": "Test"}` | user alice |
| `POST /users` | `{"username": "bob", "email": "bob@test.fr", "password": "password123", "first_name": "Bob", "last_name": "Test"}` | user bob |
| `POST /movies/import/{tmdb_id}` | `tmdb_id` = `1184918` | movie 1 (The Wild Robot) |
| `POST /rooms` | `{"room_number": 1, "capacity": 2}` | room 1, **2 seats only** (to test a full room easily) |
| `POST /screenings` | `{"movie_id": 1, "room_id": 1, "start_time": "2026-11-20T20:00:00", "base_price": 10}` | screening 1, **in the future** (choose a date after today), base price **10.00** |
| `POST /screenings` | `{"movie_id": 1, "room_id": 1, "start_time": "2026-11-01T20:00:00", "base_price": 10}` | screening 2, **in the past** (choose a date before today) |
| `POST /screenings` | `{"movie_id": 1, "room_id": 1, "start_time": "2026-11-21T20:00:00", "base_price": 9.5}` | screening 3, in the future, base price **9.50** |
| `POST /screenings` | `{"movie_id": 1, "room_id": 1, "start_time": "2026-11-22T20:00:00", "base_price": -5}` | **409** "The base price must be greater than 0" (nothing is created) |
| `POST /screenings` | `{"movie_id": 1, "room_id": 1, "start_time": "2026-11-23T20:00:00"}` | **422**: the base price is required (nothing is created) |

## 4. Log in

1. `POST /users/jwt` with `username` = `alice` and `password` = `password123`.
2. Copy the value of `access_token` (without the quotes).
3. Click **Authorize** 🔒 (top right), paste the token, then **Authorize** and **Close**.

The token expires after 10 minutes. If you get "Expired token", log in again.

## 5. Test the reservations of alice

With `POST /reservations`:

| JSON | Expected result | What it checks |
|---|---|---|
| `{"screening_id": 1, "ticket_type_id": 1}` | **201**, `"price_paid": 10.0` | A normal booking (seat 1/2), 10.00 × 1.0 |
| `{"screening_id": 2, "ticket_type_id": 1}` | **409** "has already started" | A past screening cannot be booked |
| `{"screening_id": 99, "ticket_type_id": 1}` | **404** "Screening not found" | The screening must exist |
| `{"screening_id": 1, "ticket_type_id": 2}` | **409** "is not available" | The ticket type must be active |
| `{"screening_id": 1, "ticket_type_id": 99}` | **404** "Ticket type not found" | The ticket type must exist |

Then `GET /reservations/me`: you should see **only one** reservation (refused bookings are never saved).

## 6. Check the prices

Still logged in as alice, with `POST /reservations`:

| JSON | Expected `price_paid` | Computation |
|---|---|---|
| `{"screening_id": 3, "ticket_type_id": 1}` | **9.5** | 9.50 × 1.0 |
| `{"screening_id": 3, "ticket_type_id": 3}` | **7.6** | 9.50 × 0.8 |

Then check that a change of price does not change the past sales:

1. In pgAdmin, change the student coefficient: `UPDATE test.ticket_types SET price_multiplier = 0.6 WHERE id = 3;`
2. `POST /reservations` with `{"screening_id": 3, "ticket_type_id": 3}` → `"price_paid": 5.7` (9.50 × 0.6).
3. `SELECT id, ticket_type_id, price_paid FROM test.reservations;` → the previous student reservation is **still 7.60**.

## 7. Fill the room with bob

Screening 1 now has 1 reservation out of 2 seats.

1. **Authorize** → **Logout**, then log in as bob (step 4) and paste his token.
2. `POST /reservations` with `{"screening_id": 1, "ticket_type_id": 1}` → **201** (seat 2/2).
3. The same request again → **409** "The screening is full".
4. `GET /reservations/1` → **404**: it is alice's reservation, bob cannot see it.
5. **Authorize** → **Logout**, then `POST /reservations` → **401**: you must be logged in to book.

## 8. Check and clean up (pgAdmin)

See the saved reservations (`reserved_at` and `price_paid` are filled in automatically):

```sql
SELECT * FROM test.reservations;
```

Empty the `test` schema to start again (the ids restart at 1, so this guide stays valid):

```sql
TRUNCATE test.reservations, test.screenings, test.ticket_types, test.rooms, test.movies, test.users
RESTART IDENTITY CASCADE;
```

## Known limitations

- A reservation corresponds to a single ticket.
- Ticket types cannot be created through the API yet (they are added with SQL in step 2).
- The login does not check the password yet.

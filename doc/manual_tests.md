# Manual test scenario – from the first account to the accounting

This scenario tests the whole application **through the API**, as a real user would.
It follows the life of the cinema in 6 parts: a customer creates an account, the administrator prepares
the programme, the customer books, the administrator checks the sales, customers write reviews,
and the customer manages their account.

At each part, we first send **wrong or strange data** and check that the application refuses it with a
clear error, then we do the normal action and check the result.

> Last full run: **20/11/2026** – all the steps gave the expected result.

---

## Before you start

1. **Reset the demo data**, so that everybody starts from the same state.
   In `.env`, set `POSTGRES_SCHEMA=production`, then run:

   ```bash
   pdm run python -m src.App.reset_database
   ```

   ⚠️ This erases all the data of the `production` schema.

2. **Start the API** with `pdm start` and open <http://localhost:8000/docs>.
3. **Check the `.env` file**: the TMDB API key is needed in part 2.

### How to log in in `/docs`

Call `POST /users/jwt` with a username and a password, copy the `access_token` of the answer,
click **Authorize** (top right) and paste it. To change user, click **Authorize** > **Logout**, then log in again.

### Accounts used

| Username | Password | Role |
|---|---|---|
| `admin` | `admin#26` | administrator (demo data) |
| `john` | `john_johnson&26` | customer (demo data), has already seen *Godzilla Minus Zero* |
| `lea` | `cinema2026` | new customer, created in step 1.3 |

### Ids to write down during the scenario

Some ids are created during the scenario: write down the value returned by the API and use it in the next steps.

| Name in this document | Created in step | Value in our run |
|---|---|---|
| `<MOVIE>` (Inception) | 2.7 | 11 |
| `<ROOM>` (room 7) | 2.10 | 9 |
| `<EVENING>` (screening tomorrow 20:00) | 2.14 | 133 |
| `<AFTERNOON>` (screening tomorrow 14:00) | 2.16 | 134 |

`<TOMORROW>` and `<YESTERDAY>` mean the date of tomorrow and of yesterday, in the format `YYYY-MM-DD`.

---

## Part 1 – Léa creates her account

Not logged in.

| # | Action | Data sent | Expected result | Rule checked |
|---|---|---|---|---|
| 1.1 | `POST /users/` | `{"username": "lea", "email": "lea@ensai.fr", "password": "abc", "first_name": "Lea", "last_name": "Martin"}` | **400** "Password length must be at least 8 characters" | password of at least 8 characters |
| 1.2 | `POST /users/` | same body as 1.1, **without** `email` | **422** "Field required" (`email`) | all the fields are mandatory |
| 1.3 | `POST /users/` | same body as 1.1 with `"password": "cinema2026"` | **201** `{"id": ..., "username": "lea"}` | normal registration |
| 1.4 | `POST /users/` | exactly the same body as 1.3 | **409** "Username or email already in use" | the username is unique |
| 1.5 | `POST /users/` | body of 1.3 with `"username": "lea2"` and `"email": "john@example.com"` | **409** "Username or email already in use" | the email is unique |
| 1.6 | `POST /users/jwt` | `username=lea`, `password=wrongpass` | **401** "Wrong password" | the password is checked |
| 1.7 | `POST /users/jwt` | `username=nobody`, `password=wrongpass` | **401** "Unknown username" | unknown account |
| 1.8 | `POST /users/jwt` | `username=lea`, `password=cinema2026` | **200** with an `access_token` | normal login |
| 1.9 | `GET /users/me` | **without** clicking Authorize | **401** "Not authenticated" | protected route |
| 1.10 | `GET /users/me` | Authorize with the text `not.a.token` | **403** "Error decoding token" | a fake token is refused |
| 1.11 | `GET /users/me` | Authorize with Léa's token | **200** `{"id": ..., "username": "lea"}` | the token identifies the user |

---

## Part 2 – The administrator prepares the programme

| # | Action | Data sent | Expected result | Rule checked |
|---|---|---|---|---|
| 2.1 | `GET /admin/users/` | **logged in as Léa** | **403** "Admin privileges required" | a customer cannot use admin routes |
| 2.2 | `POST /users/jwt`, then Authorize | `username=admin`, `password=admin#26` | **200** with a token | admin login |
| 2.3 | `GET /admin/movies/search` | `title` = three spaces | **400** "The title must not be empty" | empty search refused |
| 2.4 | `GET /admin/movies/search` | `title=inception`, `year=2010` | **200**, list with *Inception* (`tmdb_id` 27205) | search on TMDB |
| 2.5 | `POST /admin/movies/import/1381071` | – | **409** "... already in the catalogue" | *Godzilla Minus Zero* cannot be imported twice |
| 2.6 | `POST /admin/movies/import/999999999` | – | **404** "... not found on TMDB" | unknown TMDB id |
| 2.7 | `POST /admin/movies/import/27205` | – | **201**, *Inception*, `duration` 148 → write down `<MOVIE>` | import from TMDB |
| 2.8 | `POST /admin/rooms/` | `{"room_number": 1, "capacity": 50}` | **409** "Room number [1] is already used" | the room number is unique |
| 2.9 | `POST /admin/rooms/` | `{"room_number": 7, "capacity": 0}` | **409** "The capacity must be greater than 0" | a room has at least one seat |
| 2.10 | `POST /admin/rooms/` | `{"room_number": 7, "capacity": 2}` | **201** → write down `<ROOM>` | a small room, to test a full room later |
| 2.11 | `POST /admin/screenings/` | `{"movie_id": <MOVIE>, "room_id": <ROOM>, "start_time": "<TOMORROW>T20:00:00", "base_price": 0}` | **409** "The base price must be greater than 0" | positive base price |
| 2.12 | `POST /admin/screenings/` | same body, **without** `base_price` | **422** "Field required" (`base_price`) | the base price is mandatory |
| 2.13 | `POST /admin/screenings/` | same body with `"movie_id": 9999`, `"base_price": 10` | **404** "Movie [9999] not found" | unknown movie |
| 2.14 | `POST /admin/screenings/` | same body with `"base_price": 10` | **201**, `end_time` = 22:48 → write down `<EVENING>` | end time = start + 148 min + 20 min |
| 2.15 | `POST /admin/screenings/` | same body with `"start_time": "<TOMORROW>T21:00:00"` | **409** "The room is already booked on this time slot" | no overlap in a room |
| 2.16 | `POST /admin/screenings/` | same body with `"start_time": "<TOMORROW>T14:00:00"`, `"base_price": 8` | **201** → write down `<AFTERNOON>` | a second screening, without any sale |
| 2.17 | `POST /admin/screenings/` | same body with `"start_time": "<YESTERDAY>T20:00:00"`, `"base_price": 10` | **409** "The screening cannot start in the past" | no screening in the past |

---

## Part 3 – Léa books tickets

Log in again as **Léa** (`lea` / `cinema2026`).

| # | Action | Data sent | Expected result | Rule checked |
|---|---|---|---|---|
| 3.1 | `GET /screenings/` | `movie_id=<MOVIE>` | **200**, the two screenings of tomorrow | list of upcoming screenings |
| 3.2 | `GET /ticket-types/` | – | **200**: Normal (1.0), Child (0.6), ENSAI Student (0.8), ENSAI Staff (0.9) | ticket types available for booking |
| 3.3 | `POST /reservations/` | `{"screening_id": 99999, "ticket_type_id": 1}` | **404** "Screening [99999] not found" | unknown screening |
| 3.4 | `POST /reservations/` | `{"screening_id": <EVENING>, "ticket_type_id": 99}` | **404** "Ticket type [99] not found" | unknown ticket type |
| 3.5 | `POST /reservations/` | `{"screening_id": 1, "ticket_type_id": 1}` | **409** "Screening [1] has already started" | no booking for a past screening |
| 3.6 | `POST /reservations/` | `{"screening_id": "abc", "ticket_type_id": 1}` | **422** "Input should be a valid integer" | wrong type of data |
| 3.7 | `POST /reservations/` | `{"screening_id": <EVENING>, "ticket_type_id": 1}` | **201**, `price_paid` = **10.0** | Normal: 10.00 × 1.0 |
| 3.8 | `POST /reservations/` | `{"screening_id": <EVENING>, "ticket_type_id": 3}` | **201**, `price_paid` = **8.0** | ENSAI Student: 10.00 × 0.8 |
| 3.9 | `POST /reservations/` | `{"screening_id": <EVENING>, "ticket_type_id": 2}` | **409** "The screening is full" | room 7 has only 2 seats |
| 3.10 | `GET /reservations/me` | – | **200**, the 2 tickets of Léa with their price | a customer sees their bookings |
| 3.11 | `GET /reservations/1` | – (reservation 1 belongs to John) | **404** "Reservation with id [1] not found" | a customer cannot see the bookings of others |

---

## Part 4 – The administrator checks the sales

Log in again as **admin**.

| # | Action | Data sent | Expected result | Rule checked |
|---|---|---|---|---|
| 4.1 | `DELETE /admin/screenings/<EVENING>` | **without** `confirm` | **409** "Confirmation required ..." | a deletion must be confirmed |
| 4.2 | `DELETE /admin/screenings/<EVENING>` | `confirm=true` | **409** "2 ticket(s) already sold for this screening, it cannot be deleted" | the sales are protected |
| 4.3 | `DELETE /admin/screenings/<AFTERNOON>` | `confirm=true` | **204** | a screening without sale can be deleted |
| 4.4 | `DELETE /admin/screenings/<AFTERNOON>` | `confirm=true` (again) | **404** "Screening not found" | it does not exist anymore |
| 4.4b | `DELETE /admin/movies/<MOVIE>` | `confirm=true` | **409** "2 ticket(s) already sold for this movie, it cannot be deleted" | the sales of a movie are protected |
| 4.4c | `DELETE /admin/rooms/<ROOM>` | `confirm=true` | **409** "2 ticket(s) already sold in this room, it cannot be deleted" | the sales of a room are protected |
| 4.5 | `GET /admin/accounting/movies/<MOVIE>` | – | **200** `{"total_revenue": 18.0, "total_tickets": 2}` | revenue = 10.00 + 8.00 |
| 4.6 | `GET /admin/accounting/movies/<MOVIE>/details` | – | **200**, one line per screening; `<EVENING>`: 2 tickets, 18.0 | detail per screening |
| 4.7 | `GET /admin/accounting/period` | `start_from=2026-12-01T00:00:00`, `end_at=2026-11-01T00:00:00` | **400** "The start date is after the end date" | consistent period |
| 4.8 | `GET /admin/accounting/movies/9999` | – | **404** "Movie not found" | unknown movie |

---

## Part 5 – Reviews

| # | Action | Data sent | Expected result | Rule checked |
|---|---|---|---|---|
| 5.1 | `POST /reviews/` (logged in as **Léa**) | `{"movie_id": <MOVIE>, "rating": 8}` | **409** "You can only review a movie you have seen" | her screening is tomorrow: she has not seen the movie yet |
| 5.2 | Log in as **john**, then `POST /reviews/` | `{"movie_id": 8, "rating": 11}` | **422** "Input should be less than or equal to 10" | rating from 1 to 10 |
| 5.3 | `POST /reviews/` | `{"movie_id": 9999, "rating": 8}` | **404** "Movie [9999] not found" | unknown movie |
| 5.4 | `POST /reviews/` | `{"movie_id": 8, "rating": 9, "comment": "Impressive special effects!"}` | **201** | John saw *Godzilla Minus Zero* (id 8) on 5/11 |
| 5.5 | `POST /reviews/` | `{"movie_id": 8, "rating": 7}` | **409** "You have already reviewed this movie" | one review per customer and per movie |
| 5.6 | `GET /reviews/movies/8` | not logged in | **200**, John's review | reviews are public |

---

## Part 6 – Léa manages her account

Log in again as **Léa**.

| # | Action | Data sent | Expected result | Rule checked |
|---|---|---|---|---|
| 6.1 | `PUT /users/me/password` | `{"old_password": "cinema2026", "new_password": "abc"}` | **400** "Password length must be at least 8 characters" | the new password is checked too |
| 6.2 | `PUT /users/me/password` | `{"old_password": "wrongpass", "new_password": "newpass2026"}` | **403** "Wrong current password" | only the owner can change it |
| 6.3 | `PUT /users/me/password` | `{"old_password": "cinema2026", "new_password": "newpass2026"}` | **204** | password changed |
| 6.4 | `POST /users/jwt` | `username=lea`, `password=cinema2026` | **401** "Wrong password" | the old password does not work anymore |
| 6.5 | `POST /users/jwt` | `username=lea`, `password=newpass2026` | **200** | the new one works |
| 6.6 | `DELETE /users/me` | **without** `confirm` | **409** "Confirmation required ..." | a deletion must be confirmed |
| 6.7 | `DELETE /users/me` | `confirm=true` | **409** "This account has 2 reservation(s), it cannot be deleted ..." | the sales of a customer are protected |

---

## Part 7 – The administrator manages the prices (ticket types)

Run this part **after** part 6. At the end, reset the demo data again (see "Before you start").

| # | Action | Data sent | Expected result | Rule checked |
|---|---|---|---|---|
| 7.1 | **Logout**, then `POST /reservations/` | `{"screening_id": <EVENING>, "ticket_type_id": 1}` | **401** "Not authenticated" | you must be logged in to book |
| 7.2 | Log in as **Léa**, then `POST /admin/ticket-types/` | `{"name": "Senior", "price_multiplier": 0.7}` | **403** "Admin privileges required" | only the admin manages the prices |
| 7.3 | Log in as **admin**, then `POST /admin/ticket-types/` | `{"name": "Free", "price_multiplier": 0}` | **409** "The price multiplier must be greater than 0" | a ticket cannot be free |
| 7.4 | `POST /admin/ticket-types/` | `{"name": "child", "price_multiplier": 0.5}` | **409** "The ticket type [child] already exists" | the name is unique (whatever the case) |
| 7.5 | `POST /admin/ticket-types/` | `{"name": "Senior", "price_multiplier": 0.7}` | **201**, new ticket type *Senior* | the admin creates a price |
| 7.6 | `PUT /admin/ticket-types/3` | `{"name": "ENSAI Student", "price_multiplier": 0.6, "active": true}` | **200**, multiplier 0.6 | the admin changes a price |
| 7.7 | `GET /reservations/me` as **Léa** | – | the student ticket of step 3.8 is **still 8.0** | a price change never modifies past sales |
| 7.8 | As **admin**, `PUT /admin/ticket-types/2` | `{"name": "Child", "price_multiplier": 0.6, "active": false}` | **200**, `active` = false | the admin stops selling a price |
| 7.9 | `GET /ticket-types/` | – | **200**, *Child* is not in the list anymore, *Senior* is | only active ticket types are offered to customers |
| 7.10 | As **john**, `POST /reservations/` | `{"screening_id": <EVENING>, "ticket_type_id": 2}` | **409** "Ticket type [Child] is not available" | an inactive ticket type cannot be booked |
| 7.11 | As **admin**, `DELETE /admin/ticket-types/1` | `confirm=true` | **409** "... already sold with this ticket type, it cannot be deleted (set it as not active instead)" | the sales are protected |
| 7.12 | `DELETE /admin/ticket-types/<id of Senior>` | `confirm=true` | **204** | a ticket type never sold can be deleted |
| 7.13 | In `.env`, change one character of `TMDB_API_KEY`, restart the server, log in as **admin**, then `GET /admin/movies/search` | `title=inception` | **400** "Error while searching on TMDB: 401 Client Error ..." | a wrong API key gives a clear error (put the right key back after) |

---

## What this scenario showed us (known limitations)

- ~~A screening can be created in the past.~~ Found by this scenario on 20/11/2026, **fixed** on 21/11/2026 (step 2.17).
- ~~The error messages of `POST /admin/rooms/` were the raw PostgreSQL error.~~ Found by this scenario on 20/11/2026,
  **fixed** on 21/11/2026: the rules are now checked by `RoomService`, with a clear message (steps 2.8 and 2.9).
- ~~Deleting a movie, a room, a ticket type or an account also deleted its bookings~~ (ON DELETE CASCADE), so the
  revenue of these tickets disappeared from the accounting. **Fixed** on 21/11/2026: like a screening, they can only be
  deleted if no ticket was sold (steps 4.4b, 4.4c and 6.7). A ticket type already sold can be set as not active instead.
  Consequence: a customer who has booked cannot delete their account.

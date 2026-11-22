# Developer guide – Cinéville Bruz API

This guide is for developers who want to understand or change the code.
To install and run the application, follow the main [README](../README.md) first.

---

## 1. Tech stack

| Part | Tool |
|---|---|
| Language | Python 3.14 |
| Package manager | PDM (`pyproject.toml`, `pdm.lock`) |
| Web API | FastAPI + Uvicorn |
| Database | PostgreSQL, accessed with psycopg2 |
| Movie data | TMDB API, accessed with requests |
| Authentication | JWT tokens (PyJWT), passwords hashed with SHA-256 and a random salt |
| Tests | pytest, pytest-cov, freezegun |
| Quality | Ruff (lint + format), Pyrefly (type checking) |

## 2. Architecture

The code is organised in layers. Each layer only talks to the layer just below it.

```
HTTP request
   │
   ▼
App/            Controllers (FastAPI routers): read the request, check the login, turn errors into HTTP codes
   │
   ▼
Service/        Business rules (e.g. "a booking is refused if the room is full")
   │
   ▼
DAO/            Repositories: SQL queries, turn database rows into business objects
   │
   ▼
PostgreSQL      (and TMDB, through DAO/MovieDBConnector.py)
```

| Folder | Content |
|---|---|
| `Business_object/` | the classes of the domain: `Movie`, `Room`, `Screening`, `TicketType`, `Reservation`, `Review`, `User` |
| `Model/` | Pydantic models: the format of the request bodies and responses of the API |
| `DAO/` | `DBConnector` (connection to PostgreSQL), one `...Repo` per table, `MovieDBConnector` (TMDB) |
| `Service/` | one service per feature, plus `PasswordService` (hash, login) and `JWTService` (tokens) |
| `App/` | `API.py` (creates the app and includes the routers), one `...Controller` per resource, `JWTBearer` (token check), `reset_database.py` |

### Rules we follow

- **Business rules go in the services**, not in the controllers or the SQL. This way they can be unit tested.
- **Controllers stay thin:** call the service, then turn its exceptions into HTTP errors
  (`LookupError` → 404, `ValueError` → 409, `PermissionError` → 403).
- **Services receive their repositories in the constructor** (`MyService(repo=None)`). When nothing is given, they create the real one; in the tests, we give a fake one.
- **SQL values are never written in the query string:** they are passed with `%s` / `%(name)s` to protect against SQL injection.
- **Admin routes** use a router with the prefix `/admin/...` and `dependencies=[Depends(require_admin)]`.
- **Money uses `Decimal`**, never `float` (see `ReservationService.compute_ticket_price`).

## 3. Main features and where they are

| Feature | Controller | Service | Repositories |
|---|---|---|---|
| Accounts, login | `UserController` | `UserService`, `PasswordService`, `JWTService` | `UserRepo` |
| Movies (TMDB import) | `MovieController` | `MovieService` | `MovieRepo`, `MovieDBConnector` |
| Rooms | `RoomController` | `RoomService` | `RoomRepo` |
| F1 – Screening schedule | `ScreeningController` | `ScreeningService` | `ScreeningRepo` |
| F2 – Booking and pricing | `ReservationController`, `TicketTypeController` | `ReservationService`, `TicketTypeService` | `ReservationRepo`, `TicketTypeRepo` |
| F3 – Accounting | `AccountingController` | `AccountingService` | `ReservationRepo` |
| Reviews | `ReviewController` | `ReviewService` | `ReviewRepo` |

Some important business rules:

- **Price paid = base price of the screening × multiplier of the ticket type**, rounded to the cent, computed at booking time and **stored** in `reservations.price_paid` (so a later price change never modifies past sales).
- A booking is refused if the screening has started, the ticket type is inactive or the room is full.
- A screening, a movie, a room, a ticket type or a customer account with sold tickets cannot be deleted:
  its reservations would be erased too (`ON DELETE CASCADE`), and the sales would disappear from the accounting.
  The services check it with the `count_..._reservations` methods of `ReservationRepo`.
- A screening cannot be created in the past, and a room needs a unique number and at least one seat.
- A review needs a rating from 1 to 10, a movie the customer has seen (booking on a finished screening), and only one review per customer and movie.

## 4. Database

- `sql/production_init_db.sql`: creates the `production` schema, with demo data.
- `sql/test_init_db.sql`: creates the `test` schema, with the same tables but empty.
- The schema used by the app is chosen with `POSTGRES_SCHEMA` in `.env`. `DBConnector` sets the `search_path` to it, so the queries never write the schema name.
- Both scripts can be run several times (`CREATE TABLE IF NOT EXISTS`, `ON CONFLICT DO NOTHING`).
- To start again from a clean schema: `pdm run python -m src.App.reset_database` (erases all the data of the schema).

⚠️ **The tables are defined in both scripts. When you change a table, change it in both files.**

The data model is described in [doc/data_model.md](../doc/data_model.md).

## 5. Tests

```bash
pdm run pytest            # run all the tests
pdm test                  # run all the tests with the coverage report
pdm run pytest tests/Service/test_ReservationService.py -v    # one file
```

- `tests/Service/`: unit tests of the business rules (the most important ones).
- `tests/DAO/`: tests of the Python part of the repositories, with a fake `DBConnector`.
- **The unit tests never use the real database or TMDB**: they use fake classes (mocks) instead. They run on any machine, without `.env`.

How we write a test (see `tests/Service/test_ReservationService.py` as a model):

- one test = one business rule;
- a fake repository that returns what we need and remembers what was saved;
- the structure `GIVEN` / `WHEN` / `THEN` in comments;
- for a refusal, we also check that **nothing was saved**.

A complete manual test scenario (through the API, on the demo data, with wrong inputs at each step) is in
[doc/manual_tests.md](../doc/manual_tests.md). Run it before a delivery.

## 6. Code quality

```bash
pdm format      # format the code (Ruff)
pdm lint        # list the lint errors (Ruff)
pdm typecheck   # type checking (Pyrefly)
```

Before pushing: run `pdm run pytest`, and check that all the tests pass.

## 7. Adding a feature (checklist)

1. Table: add or change it in **both** SQL scripts.
2. Business object in `Business_object/`.
3. Repository in `DAO/` (SQL queries, rows → objects).
4. Service in `Service/` with the business rules, and its unit tests in `tests/Service/`.
5. Pydantic model in `Model/` for the request body, if needed.
6. Controller in `App/`, then include its router in `App/API.py`.
7. Check the route in `/docs`.

## 8. Git workflow

- Pull before you start: `git pull`. To avoid merge commits, set once: `git config pull.rebase true`.
- Add your files one by one (`git add <file>`), never `.env` (it contains passwords and keys).
- Small commits, with a clear message (`Add unit tests for UserService`).

## 9. Other documents

- [README.students.md](../README.students.md): presentation of the tools (PDM, Ruff…) by the teacher.
- [ARCHITECTURE.md](../ARCHITECTURE.md) and `doc/`: diagrams (architecture, classes, data model, use cases).
- [CONTRIBUTING.md](../CONTRIBUTING.md): the team.

# Cinéville Bruz API

Backend API of a movie theater, developed for the 2nd year IT project at ENSAI (team 4).

- **Customers** create an account, look at the upcoming screenings, book tickets and review the movies they have seen.
- **Administrators** import movies from [TMDB](https://www.themoviedb.org/), manage the rooms, plan the screenings and follow the revenue (accounting).

This file explains how to **install, run and use** the application.
If you want to work on the code, read the [Developer Guide](#developer-guide).

---

## 1. Prerequisites

| Tool | Version | Check with |
|---|---|---|
| Python | 3.14 | `python --version` |
| PDM (package manager) | 2.x | `pdm --version` |
| PostgreSQL | 14 or more | an empty database you can connect to (for example with pgAdmin) |
| TMDB API key | – | free, from your account settings on [themoviedb.org](https://www.themoviedb.org/settings/api) |

Install PDM if needed:

```bash
pip install --user pdm
```

> Onyxia / VSCode-server users: the script `init_project.sh` installs PDM for you. Open the port `8000` in the `Network access` configuration of your service.

## 2. Install the application

From the root of the project:

```bash
pdm install
```

This creates a virtual environment and installs all the dependencies listed in `pdm.lock`.

## 3. Configure the application

Copy the example file and fill it in:

```bash
cp .env.sample .env
```

| Variable | What to put |
|---|---|
| `POSTGRES_HOST` | address of your PostgreSQL server (e.g. `localhost`) |
| `POSTGRES_PORT` | its port (usually `5432`) |
| `POSTGRES_DATABASE` | name of your database |
| `POSTGRES_USER` / `POSTGRES_PASSWORD` | your PostgreSQL login |
| `POSTGRES_SCHEMA` | `production` (demo data, recommended) or `test` (empty tables) |
| `JWT_SECRET` | any long random text, used to sign the login tokens |
| `TMDB_API_KEY` | your TMDB API key |

## 4. Create the tables

The application uses one PostgreSQL schema, chosen with `POSTGRES_SCHEMA`:

- `production`: the tables **with demo data** (movies, rooms, screenings, ticket types, users including an administrator);
- `test`: the same tables, **empty**.

**Option A – one command (recommended).** It creates the schema written in your `.env`:

```bash
pdm run python -m src.App.Reset_database
```

Type `yes` to confirm.
⚠️ If the schema already exists, all its data is erased and replaced by the initial data.

**Option B – with pgAdmin.** Open the Query Tool on your database and run `sql/production_init_db.sql` (or `sql/test_init_db.sql`).

## 5. Run the application

```bash
pdm start
```

The API is available on <http://localhost:8000>.
Open **<http://localhost:8000/docs>** to see and try every route (Swagger interface).

For Onyxia users, you should go to your [Onyxia services](https://datalab.sspcloud.fr/my-services) and click on the **"Open"** button to view links to acces to the API.

## 6. Use the API

### Log in

1. In `/docs`, call `POST /users/jwt` with a username and a password.
2. Copy the token from the answer.
3. Click **Authorize** (top right) and paste the token.
4. You can now call the protected routes.

Demo accounts (schema `production` only):

| Username | Password | Role |
|---|---|---|
| `admin` | `admin#26` | administrator |
| `john` | `john_johnson&26` | customer |
| `mary` | `mary_smith&26` | customer |

You can also create your own customer account with `POST /users/`. In a URL, special characters must be encoded: `&` is `%26` and `#` is `%23`.

### Main routes

| Who | Route | What it does |
|---|---|---|
| Everyone | `GET /screenings/` | list the upcoming screenings |
| Everyone | `GET /movies/` | list the movies on show |
| Everyone | `GET /ticket-types/` | list the ticket types you can book (normal, student…) |
| Everyone | `GET /reviews/movies/{movie_id}` | read the reviews of a movie |
| Customer | `POST /reservations/` | book a ticket (screening + ticket type) |
| Customer | `GET /reservations/me` | see my bookings and the price paid |
| Customer | `POST /reviews/` | review a movie I have seen (rating from 1 to 10) |
| Customer | `GET` / `PUT` / `DELETE /users/me` | see, update or delete my account |
| Admin | `/admin/movies/...` | search movies on TMDB and import them |
| Admin | `/admin/rooms/...` | manage the rooms |
| Admin | `/admin/ticket-types/...` | create, update, deactivate or delete the ticket types (prices) |
| Admin | `/admin/screenings/...` | plan or delete screenings |
| Admin | `/admin/accounting/...` | revenue and tickets sold, per movie or per period |
| Admin | `/admin/users/`, `/admin/reviews/...` | list users, delete any review |

### Prices

The price of a ticket = **base price of the screening × multiplier of the ticket type**.
It is computed by the server when booking, and stored with the booking.

## 7. Troubleshooting

| Problem | Solution |
|---|---|
| `KeyError: 'POSTGRES_HOST'` (or another variable) | the `.env` file is missing or a variable is empty (step 3) |
| `relation "..." does not exist` | the tables of the schema in `POSTGRES_SCHEMA` were not created (step 4) |
| `connection refused` | PostgreSQL is not running, or the host / port in `.env` is wrong |
| The admin routes answer `403` | log in with an administrator account and click **Authorize** |
| The list of screenings is empty | the `test` schema has no data: use `production`, or create screenings as an admin |
| Port 8000 already in use | stop the other program using this port |

# Developer Guide

## Architecture

The code follows a **layered architecture**: each layer only calls the one directly below it.

```
Controller  →  Service  →  DAO  →  Database
 (HTTP)        (rules)    (SQL)    (PostgreSQL)
```

| Layer | Folder | Responsibility |
|---|---|---|
| **Controller** | `src/App/` | Receive HTTP requests, validate the format (Pydantic models), call the service, return a JSON response with the right status code. No business logic here. |
| **Service** | `src/Service/` | Business rules: computing ticket prices, checking that a room is not full, refusing to delete a movie with tickets sold, importing from TMDB, etc. |
| **DAO** (Data Access) | `src/DAO/` | Repositories that send SQL queries to PostgreSQL, and the TMDB API connector. No business logic here. |
| **Business object** | `src/Business_object/` | Plain data classes (Movie, Room, Screening, Reservation, Review, TicketType, User) shared by every layer. |
| **Model** | `src/Model/` | Pydantic models that describe the request body and the JSON responses. |

**Rules:**

- A Controller never talks to the DAO directly — it goes through a Service.
- A Service never builds an SQL query — it goes through a DAO (repository).
- A DAO never contains business rules — it only reads and writes data.
- A Business object never imports from another layer.

## Development tools

| Command | Description |
|---|---|
| `pdm run test` | Run the tests with coverage |
| `pdm run lint` | Check the code with ruff |
| `pdm run format` | Format the code with ruff |
| `pdm run typecheck` | Type checking with pyrefly |

The tests never use the real database or the TMDB API: they use fake connectors and repositories.

## Project structure

```
.
├── __main__.py            # Entry point: starts the FastAPI application
├── .env.sample            # Template for the .env configuration file
├── init_project.sh        # Helper script to install PDM on Onyxia / VSCode-server
├── pdm.lock               # Locked dependency versions (generated by PDM)
├── pyproject.toml         # Dependencies and tool configuration (ruff, pytest, pyrefly)
├── sql/                   # Database init scripts (production with demo data, test with empty tables)
├── src/
│   ├── App/               # Controllers (FastAPI routes), JWT handling, database reset script
│   ├── Service/           # Business rules (prices, availability, accounting, import from TMDB...)
│   ├── DAO/               # Repositories: SQL queries (PostgreSQL) and the TMDB API connector
│   ├── Business_object/   # Domain classes (Movie, Room, Screening, Reservation, Review, TicketType, User)
│   └── Model/             # Pydantic models (request bodies and JSON responses)
└── tests/
    ├── DAO/               # Tests of the repositories (fake DBConnector)
    └── Service/           # Tests of the services (fake repositories)
```

### Tests

- The tests **never use the real database or the TMDB API**: they use fake connectors and repositories (mocks).
- You can run a single test file or a single test function:

```bash
pdm run python -m pytest tests/Service/test_MovieService.py -v
pdm run python -m pytest tests/Service/test_MovieService.py::test_create_movie_ok -v
```

### Linting and formatting

- **Ruff** is the linter and formatter (configured in `pyproject.toml`).
- Run `pdm run format` before committing to keep the code consistent.

### Type checking

- **Pyrefly** checks the types at import time. Use the `# pyrefly: ignore` comment only when a type is genuinely unknown at runtime (for example a row read from the database).

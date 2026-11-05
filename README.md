# Prerequisite:  PDM 

Install PDM for your user with pip 

`> pip install --user pdm`

Check your PDM version with 

`> pdm --version`

Optionally, use uv "under the hood" for faster installation: 

`> pip install --user uv`

`> pdm config use_uv true`

## Note for Onyxia/k8s users

The installation can be handled by the setup script `init_project.sh`.

You can provide that configuration file as a custom initialization script for your vscode image. 

Be sure to provide the ports used by the app in the `Network access` configuration. For example, this app uses the `8000` port.

# How to install the app 

`> pdm install`

That's all 😊

# How to set up the database

1. Create a PostgreSQL database (for example with pgAdmin)
2. Copy `.env.sample` to `.env` and fill in your database information and your TMDB API key (`TMDB_API_KEY`)
3. Run the scripts on your database (pgAdmin > Query Tool):
   - `sql/test_init_db.sql` creates the `test` schema with empty tables (to test the app without touching the demo data)
   - `sql/production_init_db.sql` creates the `production` schema with demo data (movies, users, rooms, screenings, ticket types)
4. In your `.env`, set `POSTGRES_SCHEMA` to `test` or `production`, then restart the app

⚠️ The tables are defined in both scripts: when you change a table, change it in both files.

# How to run the app 

```> pdm start```

This starts a server accessible on `localhost:8000`

The API is then documented on `localhost:8000/docs`
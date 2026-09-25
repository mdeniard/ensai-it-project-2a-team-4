from typing import Optional

from src.Model.Movie import Movie

from .DBConnector import DBConnector


class MovieRepo:
    db_connector: DBConnector

    def __init__(self, db_connector: DBConnector) -> None:
        self.db_connector = db_connector

    def get_by_id(self, movie_id: int) -> Optional[Movie]:
        raw_movie = self.db_connector.sql_query("SELECT * from movies WHERE id=%s", [movie_id], "one")
        if raw_movie is None:
            return None
        # pyrefly: ignore
        return Movie(**raw_movie)

    def get_screening_movie(self) -> None:
        raw_movie = self.db_connector.sql_query("SELECT * from movies")
        if raw_movie is None:
            return None
        # pyrefly: ignore
        return Movie(**raw_movie)

    def create(self, movie) -> Movie:
        raw_created_movie = self.db_connector.sql_query(
            """
        INSERT INTO movies (id, tmdb_id, title, description, duration, released_date, rating, poster_url)
        VALUES (DEFAULT, %(tmdb_id)s, %(title)s, %(description)s, %(duration)s, %(released_date)s, %(rating)s, %(poster_url)s)
        RETURNING *;
        """,
            {"tmdb_id": movie.tmdb_id,
            "title": movie.title,
            "description": movie.description,
            "duration": movie.duration,
            "released_date": movie.released_date,
            "rating": movie.rating,
            "poster_url": movie.poster_url
            },
            "one",
        )
        # pyrefly: ignore
        return Movie(**raw_created_movie)


from typing import Optional

from src.Business_object.Movie import Movie

from .DBConnector import DBConnector


class MovieRepo:
    db_connector: DBConnector

    def __init__(self, db_connector: Optional[DBConnector] = None) -> None:
        self.db_connector = db_connector or DBConnector()

    def get_by_id(self, tmdb_id: int) -> Optional[Movie]:
        raw_movie = self.db_connector.sql_query(
            "SELECT * FROM movie WHERE tmdb_id = %s;",
            [tmdb_id],
            "one"
        )
        if raw_movie is None:
            return None
        return Movie(**raw_movie)

    def get_screening_movies(self) -> Optional[Movie]:
        raw_movies = self.db_connector.sql_query(
            "SELECT * FROM movie;",
            return_type="all"
        )
        if not raw_movies:
                    return []

        return [Movie(**movie_data) for movie_data in raw_movies]

    def create(self, movie) -> Movie:
        raw_created_movie = self.db_connector.sql_query(
            """
            INSERT INTO movie (tmdb_id, title, description, duration, released_date, rating, poster_url)
            VALUES (%(tmdb_id)s, %(title)s, %(description)s, %(duration)s, %(released_date)s, %(rating)s, %(poster_url)s)
            RETURNING *;
            """,
            {
                "tmdb_id": movie.tmdb_id,
                "title": movie.title,
                "description": movie.description,
                "duration": movie.duration,
                "released_date": movie.released_date,
                "rating": movie.rating,
                "poster_url": movie.poster_url,
            },
            "one",
        )
        return Movie(**raw_created_movie)

    def update(self, movie: Movie) -> Optional[Movie]:
        raw_updated_movie = self.db_connector.sql_query(
            """
            UPDATE movie
            SET tmdb_id = %(tmdb_id)s,
                title = %(title)s,
                description = %(description)s,
                duration = %(duration)s,
                released_date = %(released_date)s,
                rating = %(rating)s,
                poster_url = %(poster_url)s
            WHERE id = %(id)s
            RETURNING *;
            """,
            {
                "id": movie.id,
                "tmdb_id": movie.tmdb_id,
                "title": movie.title,
                "description": movie.description,
                "duration": movie.duration,
                "released_date": movie.released_date,
                "rating": movie.rating,
                "poster_url": movie.poster_url,
            },
            "one",
        )

        if raw_updated_movie is None:
            return None

        return Movie(**raw_updated_movie)

    def delete(self, movie_id: int) -> bool:
        deleted_movie = self.db_connector.sql_query(
            """
            DELETE FROM movie
            WHERE id = %s
            RETURNING id;
            """,
            [movie_id],
            "one",
        )
        return deleted_movie is not None

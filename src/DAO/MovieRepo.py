from typing import Optional

from src.Business_object.Movie import Movie

from .DBConnector import DBConnector


class MovieRepo:
    db_connector: DBConnector

    def __init__(self, db_connector: Optional[DBConnector] = None) -> None:
        """Create the repository.
        Args:
            db_connector (DBConnector, optional): The connection to the database.
                If none is given, a new DBConnector is created.
        """
        self.db_connector = db_connector or DBConnector()

    def get_by_tmdb_id(self, tmdb_id: int) -> Optional[Movie]:
        """Retrieve a movie by its TMDB identifier.
        Args:
            tmdb_id (int): The unique TMDB id of the movie.
        Returns:
            The Movie object, or None if no movie has this TMDB id.
        """
        raw_movie = self.db_connector.sql_query("SELECT * FROM movies WHERE tmdb_id = %s;", [tmdb_id], "one")
        if raw_movie is None:
            return None
        return Movie(**raw_movie)

    def get_by_id(self, id: int) -> Optional[Movie]:
        """Retrieve a movie by its database identifier.
        Args:
            id (int): The unique database id of the movie (not its TMDB id).
        Returns:
            The Movie object, or None if no movie has this id.
        """
        raw_movie = self.db_connector.sql_query("SELECT * FROM movies WHERE id = %s;", [id], "one")
        if raw_movie is None:
            return None
        return Movie(**raw_movie)

    def get_screening_movies(self) -> Optional[Movie]:
        """Retrieve all the movies of the theater database.
        Returns:
            list[Movie] of all the movies, or an empty list if there is none.
        """
        raw_movies = self.db_connector.sql_query("SELECT * FROM movies;", return_type="all")
        if not raw_movies:
            return []

        return [Movie(**movie_data) for movie_data in raw_movies]

    def create(self, movie) -> Movie:
        """Save a new movie (the id is given by the database).
        Args:
            movie (Movie): The movie to save (TMDB id, title, description, duration,
                release date, rating and poster url).
        Returns:
            The saved Movie, with its id.
        """
        raw_created_movie = self.db_connector.sql_query(
            """
            INSERT INTO movies (tmdb_id, title, description, duration, released_date, rating, poster_url)
            VALUES (%(tmdb_id)s, %(title)s, %(description)s, %(duration)s,
            %(released_date)s, %(rating)s, %(poster_url)s)
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
        """Update all the fields of an existing movie.
        Args:
            movie (Movie): The movie with its new data. Its id identifies the row to update.
        Returns:
            The updated Movie, or None if no movie has this id.
        """
        raw_updated_movie = self.db_connector.sql_query(
            """
            UPDATE movies
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
        """Delete a movie. Its screenings, their reservations and its reviews are deleted too (ON DELETE CASCADE).
        Args:
            movie_id (int): The database id of the movie to delete.
        Returns:
            True if a movie was deleted, False if no movie has this id.
        """
        deleted_movie = self.db_connector.sql_query(
            """
            DELETE FROM movies
            WHERE id = %s
            RETURNING id;
            """,
            [movie_id],
            "one",
        )
        return deleted_movie is not None

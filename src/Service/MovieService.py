from typing import Optional

from src.Business_object.Movie import Movie
from src.DAO.MovieDBConnector import MovieDBConnector
from src.DAO.MovieRepo import MovieRepo


class MovieService:
    """Service that manages movies."""

    def __init__(
        self,
        movie_repo: Optional[MovieRepo] = None,
        movie_db_connector: Optional[MovieDBConnector] = None,
    ):
        # Access to our own database (table movie)
        self.movie_repo = movie_repo or MovieRepo()
        # Access to the external TMDB API
        self.movie_db_connector = movie_db_connector or MovieDBConnector()

    def get_screening_movies(self) -> list[Movie]:
        """List all movies currently screening.
        Returns:
            list[Movie] containing all movies currently playing.
        """
        return self.movie_repo.get_screening_movies()

    def get_by_id(self, tmdb_id: int) -> Movie:
        """Find a specific movie by its id.
        Args:
            movie_db (int): The unique identifier of the movie.
        Returns:
            Movie object if found, otherwise None.
        """
        return self.movie_repo.get_by_id(tmdb_id)

    def create_movie(self, movie):
        """Create a movie
        Args:
            movie : all the data concerning the movie
        """
        return self.movie_repo.create(movie)

    def update_movie(self, movie):
        """Update a movie
        Args:
            movie : new data concerning the movie
        """
        return self.movie_repo.update(movie)

    def delete_movie(self, movie_id):
        """Delete a movie
        Args:
            movie_id : id of the movie we want to delete
        """
        return self.movie_repo.delete(movie_id)

    def search_movies(self, query) -> list[Movie]:
        """Find specifics movie by a query.
        Args:
            query (): a query.
        Returns:
            list of Movie objects if found, otherwise None.
        """
        return self.movie_repo.search_movies(query)

    def search_tmdb(self, title: str, year: Optional[int] = None) -> list[dict]:
        """Search movies on TMDB, so that the administrator can choose which one to import.
        Args:
            title (str): The title (or part of the title) of the movie.
            year (int, optional): The release year, to reduce ambiguity.
        Returns:
            list[dict] of matching movies (tmdb_id, title, release_date, overview, poster_url).
        Raises:
            ValueError if the title is empty.
        """
        # We refuse an empty search (or a search made only of spaces)
        if title is None or title.strip() == "":
            raise ValueError("The title must not be empty")

        # The connector does the call to TMDB
        return self.movie_db_connector.search_by_title(title.strip(), year)

    def import_from_tmdb(self, tmdb_id: int) -> Optional[Movie]:
        """Get a movie from TMDB and save it in our database.
        Args:
            tmdb_id (int): The TMDB identifier of the movie chosen by the administrator.
        Returns:
            The saved Movie (with its id in our database), or None if TMDB does not know this movie.
        Raises:
            ValueError if the movie is already in our catalogue.
        """
        # 1. Check that the movie is not already in our database
        existing_movie = self.movie_repo.get_by_id(tmdb_id)
        if existing_movie is not None:
            raise ValueError(f"Movie with tmdb_id [{tmdb_id}] is already in the catalogue")

        # 2. Get the full details of the movie from TMDB
        movie = self.movie_db_connector.get_by_tmdb_id(tmdb_id)
        if movie is None:
            # TMDB does not know this movie
            return None

        # 3. Save the movie in our database and return it (now with its id)
        return self.movie_repo.create(movie)

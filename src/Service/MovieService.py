from typing import Optional

from src.DAO.MovieRepo import MovieRepo
from src.Business_object.Movie import Movie


class MovieService:
    movie_db: None
    """Service that manages movies."""

    def __init__(self, movie_repo: Optional[MovieRepo] = None):
        self.movie_repo = movie_repo or MovieRepo()

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

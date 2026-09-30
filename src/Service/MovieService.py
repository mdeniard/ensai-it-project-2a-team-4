from src.DAO.MovieRepo import MovieRepo
from src.Model.Movie import Movie


class MovieService:
    movie_db: None
    """Service that manages movies."""

    def __init__(self, movie_db: None):
        self.movie_db = movie_db

    def get_screening_movies(self) -> list[Movie]:
        """List all movies currently screening.
        Returns:
            list[Movie] containing all movies currently playing.
        """
        return self.movie_db.get_screening_movies()

    def get_by_id(self, movie_id: int) -> Movie:
        """Find a specific movie by its id.
        Args:
            movie_db (int): The unique identifier of the movie.
        Returns:
            Movie object if found, otherwise None.
        """
        # return Movie(id=1, original_title="A Clockwork Orange")
        # return self.movie_db.get_by_id(movie_id)
        return self.movie_db.get_by_id(movie_id)

    def create_movie(self, movie_data):
        """Create a movie
        Args:
            movie_data : all the data concerning the movie
        """
        return self.movie_db.create_movie(movie_data)

    def search_movies(self.query) -> list[Movie]:
        """Find specifics movie by a query.
        Args:
            query (): a query.
        Returns:
            list of Movie objects if found, otherwise None.
        """
        return self.movie_db.search_movies(query)

from typing import Optional

from src.Business_object.Movie import Movie
from src.DAO.MovieDBConnector import MovieDBConnector
from src.DAO.MovieRepo import MovieRepo
from src.DAO.ReservationRepo import ReservationRepo


class MovieService:
    """Service that manages movies (our catalogue and the import from TMDB)."""

    def __init__(
        self,
        movie_repo: Optional[MovieRepo] = None,
        movie_db_connector: Optional[MovieDBConnector] = None,
        reservation_repo: Optional[ReservationRepo] = None,
    ):
        """Create the service.
        Args:
            movie_repo (MovieRepo, optional): Access to the movies in our database.
            movie_db_connector (MovieDBConnector, optional): Access to the external TMDB API.
                If one is not given, a new one is created.
            reservation_repo (ReservationRepo, optional): Access to the reservations, only used before
                deleting a movie. If none is given, a new ReservationRepo is created when it is needed.
        """
        # Access to our own database (table movie)
        self.movie_repo = movie_repo or MovieRepo()
        # Access to the external TMDB API
        self.movie_db_connector = movie_db_connector or MovieDBConnector()
        # Access to the reservations (to protect the sales before a deletion)
        self.reservation_repo = reservation_repo

    def get_screening_movies(self) -> list[Movie]:
        """List all the movies of our database.
        Returns:
            list[Movie] of all the movies, or an empty list if there is none.
        """
        return self.movie_repo.get_screening_movies()

    def get_by_id(self, tmdb_id: int) -> Movie:
        """Find a movie by its id in our database.
        Args:
            tmdb_id (int): The database id of the movie. Despite its name, this is not the TMDB id.
        Returns:
            The Movie, or None if no movie has this id.
        """
        return self.movie_repo.get_by_id(tmdb_id)

    def create_movie(self, movie):
        """Create a movie from data given by hand (to get it from TMDB, use import_from_tmdb).
        Args:
            movie (Movie): The movie to save (TMDB id, title, description, duration,
                release date, rating and poster url).
        Returns:
            The saved Movie, with its id.
        """
        return self.movie_repo.create(movie)

    def update_movie(self, movie):
        """Update all the fields of a movie.
        Args:
            movie (Movie): The movie with its new data. Its id identifies the one to update.
        Returns:
            The updated Movie, or None if no movie has this id.
        """
        return self.movie_repo.update(movie)

    def delete_movie(self, movie_id):
        """Delete a movie that has no ticket sold. Its screenings and its reviews are deleted too.
        A movie with tickets sold cannot be deleted: its reservations would be deleted too
        (ON DELETE CASCADE), so the sales would disappear from the accounting.
        Args:
            movie_id (int): The database id of the movie to delete.
        Returns:
            True if the movie was deleted, False if no movie has this id.
        Raises:
            ValueError if tickets were already sold for this movie.
        """
        # Refuse the deletion if at least one ticket was sold for this movie
        reservation_repo = self.reservation_repo or ReservationRepo()
        tickets_sold = reservation_repo.count_movie_reservations(movie_id)
        if tickets_sold > 0:
            raise ValueError(f"{tickets_sold} ticket(s) already sold for this movie, it cannot be deleted")

        return self.movie_repo.delete(movie_id)

    def search_tmdb(self, title: str, year: Optional[int] = None) -> list[dict]:
        """Search movies on TMDB, so that the administrator can choose which one to import.
        The search is refused if the title is empty or made only of spaces.
        Args:
            title (str): The title (or part of the title) of the movie.
            year (int, optional): The release year, to reduce ambiguity.
        Returns:
            list[dict] of matching movies (tmdb_id, title, release_date, overview, poster_url).
        """
        # We refuse an empty search (or a search made only of spaces)
        if title is None or title.strip() == "":
            raise ValueError("The title must not be empty")

        # The connector does the call to TMDB
        return self.movie_db_connector.search_by_title(title.strip(), year)

    def import_from_tmdb(self, tmdb_id: int) -> Optional[Movie]:
        """Get a movie from TMDB and save it in our database.
        The import is refused if the movie is already in our catalogue.
        Args:
            tmdb_id (int): The TMDB identifier of the movie chosen by the administrator.
        Returns:
            The saved Movie (with its id in our database), or None if TMDB does not know this movie.
        """
        # 1. Check that the movie is not already in our database
        # (we search with the TMDB id, not with the id of our database)
        existing_movie = self.movie_repo.get_by_tmdb_id(tmdb_id)
        if existing_movie is not None:
            raise ValueError(f"Movie with tmdb_id [{tmdb_id}] is already in the catalogue")

        # 2. Get the full details of the movie from TMDB
        movie = self.movie_db_connector.get_by_tmdb_id(tmdb_id)
        if movie is None:
            # TMDB does not know this movie
            return None

        # 3. Save the movie in our database and return it (now with its id)
        return self.movie_repo.create(movie)

import pytest

from src.Business_object.Movie import Movie
from src.Service.MovieService import MovieService

# These tests use a fake repo (instead of the database) and a fake connector (instead of TMDB),
# like the MockDBConnector in tests/DAO/test_UserRepo.py


def make_wild_robot(movie_id=None):
    """Create the movie used in the tests."""
    return Movie(
        tmdb_id=1184918,
        title="The Wild Robot",
        description="A robot on an island.",
        duration=102,
        released_date="2024-09-12",
        rating=8.3,
        poster_url="https://image.tmdb.org/t/p/w500/wild_robot.jpg",
        id=movie_id,
    )


class MockMovieRepo:
    """Fake MovieRepo: the movies are kept in a Python list instead of the database."""

    def __init__(self, movies_in_database):
        self.movies_in_database = movies_in_database
        self.create_was_called = False

    def get_by_id(self, tmdb_id):
        for movie in self.movies_in_database:
            if movie.tmdb_id == tmdb_id:
                return movie
        return None

    def create(self, movie):
        self.create_was_called = True
        # The database would give an id to the new movie
        movie.id = len(self.movies_in_database) + 1
        self.movies_in_database.append(movie)
        return movie


class MockMovieDBConnector:
    """Fake MovieDBConnector: TMDB only knows The Wild Robot."""

    def __init__(self):
        self.last_search = None

    def search_by_title(self, title, year=None):
        # Remember what was searched, to check it in the tests
        self.last_search = (title, year)
        return [{"tmdb_id": 1184918, "title": "The Wild Robot"}]

    def get_by_tmdb_id(self, tmdb_id):
        if tmdb_id == 1184918:
            return make_wild_robot()
        return None


# ---------- search_tmdb ----------


def test_search_tmdb_ok():
    # GIVEN
    connector = MockMovieDBConnector()
    movie_service = MovieService(MockMovieRepo([]), connector)

    # WHEN
    movies = movie_service.search_tmdb("wild robot", 2024)

    # THEN the search is sent to the connector and its result is returned
    assert movies == [{"tmdb_id": 1184918, "title": "The Wild Robot"}]
    assert connector.last_search == ("wild robot", 2024)


def test_search_tmdb_removes_spaces_around_title():
    # GIVEN
    connector = MockMovieDBConnector()
    movie_service = MovieService(MockMovieRepo([]), connector)

    # WHEN
    movie_service.search_tmdb("   wild robot  ")

    # THEN the spaces before and after the title are removed
    assert connector.last_search == ("wild robot", None)


def test_search_tmdb_empty_title():
    # GIVEN
    movie_service = MovieService(MockMovieRepo([]), MockMovieDBConnector())

    # WHEN / THEN an empty title is refused
    with pytest.raises(ValueError):
        movie_service.search_tmdb("   ")


# ---------- import_from_tmdb ----------


def test_import_from_tmdb_ok():
    # GIVEN an empty database
    movie_repo = MockMovieRepo([])
    movie_service = MovieService(movie_repo, MockMovieDBConnector())

    # WHEN we import The Wild Robot
    movie = movie_service.import_from_tmdb(1184918)

    # THEN it is saved in the database and returned with its id
    assert movie_repo.create_was_called
    assert movie.id == 1
    assert movie.title == "The Wild Robot"
    assert movie.duration == 102


def test_import_from_tmdb_already_in_catalogue():
    # GIVEN The Wild Robot is already in the database
    movie_repo = MockMovieRepo([make_wild_robot(movie_id=1)])
    movie_service = MovieService(movie_repo, MockMovieDBConnector())

    # WHEN / THEN importing it again is refused
    with pytest.raises(ValueError):
        movie_service.import_from_tmdb(1184918)

    # AND nothing new was saved
    assert not movie_repo.create_was_called


def test_import_from_tmdb_unknown_movie():
    # GIVEN
    movie_repo = MockMovieRepo([])
    movie_service = MovieService(movie_repo, MockMovieDBConnector())

    # WHEN we import a movie that TMDB does not know
    movie = movie_service.import_from_tmdb(999999999)

    # THEN we get None and nothing was saved
    assert movie is None
    assert not movie_repo.create_was_called

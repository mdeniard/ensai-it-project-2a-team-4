import pytest

from src.Business_object.Movie import Movie
from src.Service.MovieService import MovieService

# These tests use a fake repo (instead of the database) and a fake connector (instead of TMDB)


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

    def get_screening_movies(self):
        return self.movies_in_database

    def get_by_id(self, movie_id):
        for movie in self.movies_in_database:
            if movie.id == movie_id:
                return movie
        return None

    def get_by_tmdb_id(self, tmdb_id):
        for movie in self.movies_in_database:
            if movie.tmdb_id == tmdb_id:
                return movie
        return None

    def create(self, movie):
        self.create_was_called = True
        movie.id = len(self.movies_in_database) + 1
        self.movies_in_database.append(movie)
        return movie

    def update(self, movie):
        for i, existing in enumerate(self.movies_in_database):
            if existing.id == movie.id:
                self.movies_in_database[i] = movie
                return movie
        return None

    def delete(self, movie_id):
        for i, movie in enumerate(self.movies_in_database):
            if movie.id == movie_id:
                self.movies_in_database.pop(i)
                return True
        return False


class MockReservationRepo:
    """Fake ReservationRepo: we choose how many tickets were sold for the movie."""

    def __init__(self, tickets_sold=0):
        self.tickets_sold = tickets_sold

    def count_movie_reservations(self, movie_id):
        return self.tickets_sold


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


# ---------- get_screening_movies ----------


def test_get_screening_movies_returns_all():
    # GIVEN the database has 2 movies
    movie_repo = MockMovieRepo(
        [
            make_wild_robot(movie_id=1),
            Movie(
                tmdb_id=2,
                title="Other",
                description="x",
                duration=90,
                released_date="2020-01-01",
                rating=7.0,
                poster_url=None,
                id=2,
            ),
        ]
    )
    movie_service = MovieService(movie_repo, MockMovieDBConnector())

    # WHEN we list all movies
    result = movie_service.get_screening_movies()

    # THEN we get them
    assert len(result) == 2


def test_get_screening_movies_returns_empty_list():
    # GIVEN the database is empty
    movie_service = MovieService(MockMovieRepo([]), MockMovieDBConnector())

    # WHEN we list all movies / THEN we get an empty list
    assert movie_service.get_screening_movies() == []


# ---------- get_by_id ----------


def test_get_by_id_returns_movie_when_found():
    # GIVEN movie 1 exists
    movie_repo = MockMovieRepo([make_wild_robot(movie_id=1)])
    movie_service = MovieService(movie_repo, MockMovieDBConnector())

    # WHEN we look it up by id
    result = movie_service.get_by_id(1)

    # THEN we get it
    assert result.title == "The Wild Robot"


def test_get_by_id_returns_none_when_not_found():
    # GIVEN movie 99 does not exist
    movie_service = MovieService(MockMovieRepo([make_wild_robot(movie_id=1)]), MockMovieDBConnector())

    # WHEN we look it up / THEN we get None
    assert movie_service.get_by_id(99) is None


# ---------- create_movie ----------


def test_create_movie_ok():
    # GIVEN the admin enters a movie by hand
    movie_repo = MockMovieRepo([])
    movie_service = MovieService(movie_repo, MockMovieDBConnector())
    new_movie = Movie(
        tmdb_id=2, title="Other", description="x", duration=90, released_date="2020-01-01", rating=7.0, poster_url=None
    )

    # WHEN the admin saves it
    created = movie_service.create_movie(new_movie)

    # THEN it is saved and returned with its id
    assert created.id == 1
    assert created.title == "Other"
    assert movie_repo.create_was_called is True


# ---------- update_movie ----------


def test_update_movie_ok():
    # GIVEN movie 1 exists
    movie_repo = MockMovieRepo([make_wild_robot(movie_id=1)])
    movie_service = MovieService(movie_repo, MockMovieDBConnector())

    # WHEN the admin updates its title
    updated_movie = make_wild_robot(movie_id=1)
    updated_movie.title = "The Wild Robot (Remastered)"
    updated = movie_service.update_movie(updated_movie)

    # THEN the update is saved and returned
    assert updated.title == "The Wild Robot (Remastered)"
    assert movie_repo.movies_in_database[0].title == "The Wild Robot (Remastered)"


def test_update_movie_returns_none_when_not_found():
    # GIVEN movie 99 does not exist
    movie_repo = MockMovieRepo([make_wild_robot(movie_id=1)])
    movie_service = MovieService(movie_repo, MockMovieDBConnector())

    # WHEN we update it / THEN we get None
    updated_movie = make_wild_robot(movie_id=99)
    assert movie_service.update_movie(updated_movie) is None


# ---------- delete_movie ----------


def test_delete_movie_ok():
    # GIVEN movie 1 exists and no ticket was sold for it
    movie_repo = MockMovieRepo([make_wild_robot(movie_id=1)])
    movie_service = MovieService(movie_repo, MockMovieDBConnector(), MockReservationRepo(tickets_sold=0))

    # WHEN the admin deletes it
    result = movie_service.delete_movie(1)

    # THEN it is deleted
    assert result is True
    assert len(movie_repo.movies_in_database) == 0


def test_delete_movie_with_tickets_sold_is_refused():
    # GIVEN 3 tickets were sold for movie 1
    movie_repo = MockMovieRepo([make_wild_robot(movie_id=1)])
    movie_service = MovieService(movie_repo, MockMovieDBConnector(), MockReservationRepo(tickets_sold=3))

    # WHEN the admin deletes it / THEN ValueError and the movie is still there
    with pytest.raises(ValueError, match="3 ticket"):
        movie_service.delete_movie(1)
    assert len(movie_repo.movies_in_database) == 1


def test_delete_movie_returns_false_when_not_found():
    # GIVEN movie 99 does not exist
    movie_repo = MockMovieRepo([make_wild_robot(movie_id=1)])
    movie_service = MovieService(movie_repo, MockMovieDBConnector(), MockReservationRepo())

    # WHEN the admin deletes it / THEN we get False
    assert movie_service.delete_movie(99) is False

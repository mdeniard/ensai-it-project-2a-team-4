from src.Business_object.Movie import Movie
from src.DAO.MovieRepo import MovieRepo

# These tests never use the real database:
# we give MovieRepo a fake DBConnector (like the MockDBConnector in tests/DAO/test_UserRepo.py)


class MockDBConnector:
    """Fake DBConnector.
    - it returns the answer we prepared (as if PostgreSQL had answered)
    - it remembers the query and the data it received, so that we can check them in the tests
    """

    def __init__(self, answer):
        self.answer = answer
        self.last_query = None
        self.last_data = None

    def sql_query(self, query, data=None, return_type="one"):
        # Remember what the repo sent
        self.last_query = query
        self.last_data = data
        # Return the prepared answer
        return self.answer


# A row of the movies table, as PostgreSQL would return it
WILD_ROBOT_ROW = {
    "id": 1,
    "tmdb_id": 1184918,
    "title": "The Wild Robot",
    "description": "A robot on an island.",
    "duration": 102,
    "released_date": "2024-09-12",
    "rating": 8.3,
    "poster_url": "https://image.tmdb.org/t/p/w500/wild_robot.jpg",
}

# Another row, for the tests that need several movies
INCEPTION_ROW = {
    "id": 2,
    "tmdb_id": 27205,
    "title": "Inception",
    "description": "A thief who steals secrets through dreams.",
    "duration": 148,
    "released_date": "2010-07-15",
    "rating": 8.4,
    "poster_url": "https://image.tmdb.org/t/p/w500/inception.jpg",
}


def make_wild_robot(movie_id=None):
    """Create the Movie object used in the tests."""
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


# ---------- get_by_tmdb_id ----------


def test_get_by_tmdb_id_found():
    # GIVEN the database contains The Wild Robot
    db_connector = MockDBConnector(WILD_ROBOT_ROW)
    movie_repo = MovieRepo(db_connector)

    # WHEN we search it with its TMDB id
    movie = movie_repo.get_by_tmdb_id(1184918)

    # THEN we get a Movie object with the right values
    assert movie is not None
    assert movie.id == 1
    assert movie.tmdb_id == 1184918
    assert movie.title == "The Wild Robot"
    # AND the repo searched with the TMDB id
    assert "WHERE tmdb_id" in db_connector.last_query
    assert db_connector.last_data == [1184918]


def test_get_by_tmdb_id_not_found():
    # GIVEN the database finds nothing
    movie_repo = MovieRepo(MockDBConnector(None))

    # WHEN we search a movie / THEN we get None
    assert movie_repo.get_by_tmdb_id(999999999) is None


# ---------- get_by_id ----------


def test_get_by_id_found():
    # GIVEN the database contains The Wild Robot
    db_connector = MockDBConnector(WILD_ROBOT_ROW)
    movie_repo = MovieRepo(db_connector)

    # WHEN we search it with the id of our database
    movie = movie_repo.get_by_id(1)

    # THEN we get the movie
    assert movie is not None
    assert movie.title == "The Wild Robot"
    # AND the repo searched with the id (not the TMDB id)
    assert "WHERE id" in db_connector.last_query
    assert db_connector.last_data == [1]


def test_get_by_id_not_found():
    # GIVEN the database finds nothing
    movie_repo = MovieRepo(MockDBConnector(None))

    # WHEN we search a movie / THEN we get None
    assert movie_repo.get_by_id(42) is None


# ---------- get_screening_movies ----------


def test_get_screening_movies_several_movies():
    # GIVEN the database contains two movies
    movie_repo = MovieRepo(MockDBConnector([WILD_ROBOT_ROW, INCEPTION_ROW]))

    # WHEN we list the movies
    movies = movie_repo.get_screening_movies()

    # THEN we get two Movie objects, in the same order
    assert len(movies) == 2
    assert movies[0].title == "The Wild Robot"
    assert movies[1].title == "Inception"


def test_get_screening_movies_no_movie():
    # GIVEN the movies table is empty (PostgreSQL returns an empty list)
    movie_repo = MovieRepo(MockDBConnector([]))

    # WHEN we list the movies / THEN we get an empty list
    assert movie_repo.get_screening_movies() == []


# ---------- create ----------


def test_create():
    # GIVEN a new movie (no id yet) and a database that returns the saved row
    db_connector = MockDBConnector(WILD_ROBOT_ROW)
    movie_repo = MovieRepo(db_connector)
    new_movie = make_wild_robot()

    # WHEN we save it
    created_movie = movie_repo.create(new_movie)

    # THEN we get the movie with the id given by the database
    assert created_movie.id == 1
    assert created_movie.title == "The Wild Robot"
    # AND the repo sent an INSERT with the values of the movie
    assert "INSERT INTO movies" in db_connector.last_query
    assert db_connector.last_data["tmdb_id"] == 1184918
    assert db_connector.last_data["title"] == "The Wild Robot"
    assert db_connector.last_data["duration"] == 102


# ---------- update ----------


def test_update_found():
    # GIVEN the database returns the updated row (the title was changed)
    updated_row = dict(WILD_ROBOT_ROW)
    updated_row["title"] = "The Wild Robot (new title)"
    db_connector = MockDBConnector(updated_row)
    movie_repo = MovieRepo(db_connector)

    movie_to_update = make_wild_robot(movie_id=1)
    movie_to_update.title = "The Wild Robot (new title)"

    # WHEN we update the movie
    updated_movie = movie_repo.update(movie_to_update)

    # THEN we get the updated movie
    assert updated_movie is not None
    assert updated_movie.title == "The Wild Robot (new title)"
    # AND the repo sent an UPDATE for the right movie
    assert "UPDATE movies" in db_connector.last_query
    assert db_connector.last_data["id"] == 1


def test_update_not_found():
    # GIVEN the movie does not exist (PostgreSQL updates no row and returns nothing)
    movie_repo = MovieRepo(MockDBConnector(None))

    # WHEN we update it / THEN we get None
    assert movie_repo.update(make_wild_robot(movie_id=42)) is None


# ---------- delete ----------


def test_delete_found():
    # GIVEN the database deleted the movie (it returns the id of the deleted row)
    db_connector = MockDBConnector({"id": 1})
    movie_repo = MovieRepo(db_connector)

    # WHEN we delete it / THEN we get True
    assert movie_repo.delete(1) is True
    # AND the repo sent a DELETE for the right movie
    assert "DELETE FROM movies" in db_connector.last_query
    assert db_connector.last_data == [1]


def test_delete_not_found():
    # GIVEN the movie does not exist (no row deleted, nothing returned)
    movie_repo = MovieRepo(MockDBConnector(None))

    # WHEN we delete it / THEN we get False
    assert movie_repo.delete(42) is False

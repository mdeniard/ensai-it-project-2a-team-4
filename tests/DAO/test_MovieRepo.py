from src.DAO.MovieRepo import MovieRepo

# These tests never use the real database: we give MovieRepo a fake DBConnector.
# They only check the Python part of the repo (a row is turned into a Movie, "nothing found" gives None
# or an empty list, the right id is sent). They cannot tell if the SQL is correct: that needs a real database.


class MockDBConnector:
    """Fake DBConnector.
    - it returns the answer we prepared (as if PostgreSQL had answered)
    - it remembers the data it received, so that we can check them in the tests
    """

    def __init__(self, answer):
        self.answer = answer
        self.last_data = None

    def sql_query(self, query, data=None, return_type="one"):
        # Remember what the repo sent
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

# Another row, for the test that needs several movies
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


# ---------- get_by_tmdb_id (used to refuse importing the same movie twice) ----------


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
    # AND the repo searched with the TMDB id (not the id of our database)
    assert db_connector.last_data == [1184918]


def test_get_by_tmdb_id_not_found():
    # GIVEN the database finds nothing
    movie_repo = MovieRepo(MockDBConnector(None))

    # WHEN we search a movie / THEN we get None (so the movie can be imported)
    assert movie_repo.get_by_tmdb_id(999999999) is None


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

import pytest
import requests

from src.DAO import MovieDBConnector as movie_db_connector_module
from src.DAO.MovieDBConnector import MovieDBConnector

# These tests never call the real TMDB API:
# we replace requests.get by a fake function that returns a prepared answer.


class FakeResponse:
    """Imitates the object returned by requests.get."""

    def __init__(self, status_code, json_data=None):
        self.status_code = status_code
        self.json_data = json_data

    def json(self):
        return self.json_data

    def raise_for_status(self):
        # Like the real requests library: error codes raise an exception
        if self.status_code >= 400:
            raise requests.HTTPError(f"Error {self.status_code}")


# Answer of TMDB for a search (only the fields we use)
FAKE_SEARCH_ANSWER = {
    "results": [
        {
            "id": 1184918,
            "title": "The Wild Robot",
            "release_date": "2024-09-12",
            "overview": "A robot on an island.",
            "poster_path": "/wild_robot.jpg",
        },
        {
            "id": 123,
            "title": "The Wild Robot Escapes",
            "release_date": "",
            "overview": "",
            "poster_path": None,
        },
    ]
}

# Answer of TMDB for the details of a movie (only the fields we use)
FAKE_DETAILS_ANSWER = {
    "id": 1184918,
    "title": "The Wild Robot",
    "overview": "A robot on an island.",
    "runtime": 102,
    "release_date": "2024-09-12",
    "vote_average": 8.3,
    "poster_path": "/wild_robot.jpg",
}


def test_search_by_title_ok(monkeypatch):
    # GIVEN TMDB returns two movies
    def fake_get(url, params, timeout):
        return FakeResponse(200, FAKE_SEARCH_ANSWER)

    monkeypatch.setattr(movie_db_connector_module.requests, "get", fake_get)
    connector = MovieDBConnector(api_key="fake_key")

    # WHEN we search a title
    movies = connector.search_by_title("wild robot")

    # THEN we get the two movies with the fields we need
    assert len(movies) == 2
    assert movies[0]["tmdb_id"] == 1184918
    assert movies[0]["title"] == "The Wild Robot"
    assert movies[0]["poster_url"] == "https://image.tmdb.org/t/p/w500/wild_robot.jpg"


def test_search_by_title_empty_values_become_none(monkeypatch):
    # GIVEN TMDB returns a movie with an empty date, empty overview and no poster
    def fake_get(url, params, timeout):
        return FakeResponse(200, FAKE_SEARCH_ANSWER)

    monkeypatch.setattr(movie_db_connector_module.requests, "get", fake_get)
    connector = MovieDBConnector(api_key="fake_key")

    # WHEN we search a title
    movies = connector.search_by_title("wild robot")

    # THEN the empty values are replaced by None
    assert movies[1]["release_date"] is None
    assert movies[1]["overview"] is None
    assert movies[1]["poster_url"] is None


def test_search_by_title_sends_title_year_and_key(monkeypatch):
    # GIVEN a fake TMDB that remembers the parameters it received
    received = {}

    def fake_get(url, params, timeout):
        received["url"] = url
        received["params"] = params
        return FakeResponse(200, {"results": []})

    monkeypatch.setattr(movie_db_connector_module.requests, "get", fake_get)
    connector = MovieDBConnector(api_key="fake_key")

    # WHEN we search with a year
    connector.search_by_title("close", 2022)

    # THEN the right endpoint and parameters were sent to TMDB
    assert received["url"] == "https://api.themoviedb.org/3/search/movie"
    assert received["params"]["query"] == "close"
    assert received["params"]["year"] == 2022
    assert received["params"]["api_key"] == "fake_key"


def test_search_by_title_no_result(monkeypatch):
    # GIVEN TMDB finds nothing
    def fake_get(url, params, timeout):
        return FakeResponse(200, {"results": []})

    monkeypatch.setattr(movie_db_connector_module.requests, "get", fake_get)
    connector = MovieDBConnector(api_key="fake_key")

    # WHEN we search / THEN we get an empty list
    assert connector.search_by_title("zzzzzz") == []


def test_get_by_tmdb_id_ok(monkeypatch):
    # GIVEN TMDB returns the details of a movie
    def fake_get(url, params, timeout):
        return FakeResponse(200, FAKE_DETAILS_ANSWER)

    monkeypatch.setattr(movie_db_connector_module.requests, "get", fake_get)
    connector = MovieDBConnector(api_key="fake_key")

    # WHEN we get the movie
    movie = connector.get_by_tmdb_id(1184918)

    # THEN we get a Movie object with all the fields converted
    assert movie is not None
    assert movie.id is None  # not saved in our database yet
    assert movie.tmdb_id == 1184918
    assert movie.title == "The Wild Robot"
    assert movie.description == "A robot on an island."
    assert movie.duration == 102
    assert movie.released_date == "2024-09-12"
    assert movie.rating == 8.3
    assert movie.poster_url == "https://image.tmdb.org/t/p/w500/wild_robot.jpg"


def test_get_by_tmdb_id_not_found(monkeypatch):
    # GIVEN TMDB does not know the movie (404)
    def fake_get(url, params, timeout):
        return FakeResponse(404)

    monkeypatch.setattr(movie_db_connector_module.requests, "get", fake_get)
    connector = MovieDBConnector(api_key="fake_key")

    # WHEN we get the movie / THEN we get None
    assert connector.get_by_tmdb_id(999999999) is None


def test_get_by_tmdb_id_wrong_api_key(monkeypatch):
    # GIVEN TMDB refuses the API key (401)
    def fake_get(url, params, timeout):
        return FakeResponse(401)

    monkeypatch.setattr(movie_db_connector_module.requests, "get", fake_get)
    connector = MovieDBConnector(api_key="wrong_key")

    # WHEN we get the movie / THEN an exception is raised
    with pytest.raises(requests.HTTPError):
        connector.get_by_tmdb_id(1184918)

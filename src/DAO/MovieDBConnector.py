import os
from typing import Optional

import requests

from src.Business_object.Movie import Movie

# Base address of the TMDB API (all the requests start with it)
TMDB_BASE_URL = "https://api.themoviedb.org/3"
# TMDB only gives the end of the poster address, we add this beginning to get the full image URL
TMDB_POSTER_BASE_URL = "https://image.tmdb.org/t/p/w500"


class MovieDBConnector:
    """Retrieves movie information from the TMDB API."""

    api_key: Optional[str]

    def __init__(self, api_key: Optional[str] = None) -> None:
        # If no key is given, we read it from the .env file
        # (giving a key by hand is useful for the tests)
        if api_key is not None:
            self.api_key = api_key
        else:
            self.api_key = os.environ.get("TMDB_API_KEY")

    def search_by_title(self, title: str, year: Optional[int] = None) -> list[dict]:
        """Search movies on TMDB by title.
        Args:
            title (str): The title (or part of the title) of the movie.
            year (int, optional): The release year, to reduce ambiguity.
        Returns:
            list[dict] of matching movies, so that the administrator can choose the right one.
        """
        # Parameters sent to TMDB: the title, and the year only if it was given
        params = {"query": title}
        if year is not None:
            params["year"] = year

        # Call the TMDB search endpoint
        data = self._get("/search/movie", params)
        if data is None:
            return []

        # TMDB returns a lot of information, we only keep what the administrator
        # needs to recognise the movie
        movies_found = []
        for result in data["results"]:
            movies_found.append(  # noqa: PERF401 (a simple loop is easier to read here)
                {
                    "tmdb_id": result["id"],
                    "title": result["title"],
                    "release_date": self._empty_to_none(result.get("release_date")),
                    "overview": self._empty_to_none(result.get("overview")),
                    "poster_url": self._build_poster_url(result.get("poster_path")),
                }
            )
        return movies_found

    def get_by_tmdb_id(self, tmdb_id: int) -> Optional[Movie]:
        """Get the full details of a movie from TMDB.
        Args:
            tmdb_id (int): The TMDB identifier of the movie.
        Returns:
            Movie object (not yet saved in the database) if found, otherwise None.
        """
        # Call the TMDB details endpoint (the search does not give the duration, this one does)
        data = self._get(f"/movie/{tmdb_id}")
        if data is None:
            return None

        # Transform the TMDB answer into our own Movie object
        # (the id stays None because the movie is not saved in our database yet)
        return Movie(
            tmdb_id=data["id"],
            title=data["title"],
            description=self._empty_to_none(data.get("overview")),
            duration=self._empty_to_none(data.get("runtime")),
            released_date=self._empty_to_none(data.get("release_date")),
            rating=data.get("vote_average"),
            poster_url=self._build_poster_url(data.get("poster_path")),
        )

    def _get(self, endpoint: str, params: Optional[dict] = None) -> Optional[dict]:
        """Send a GET request to TMDB.
        Returns:
            The JSON response as a dict, or None if TMDB answers 404 (not found).
        Raises:
            requests.HTTPError for any other error (invalid API key, TMDB unavailable...).
        """
        # The API key must be sent with every request
        if params is None:
            params = {}
        params["api_key"] = self.api_key

        # Send the request (we stop waiting after 10 seconds)
        response = requests.get(TMDB_BASE_URL + endpoint, params=params, timeout=10)

        # 404 means that TMDB does not know this movie
        if response.status_code == 404:
            return None

        # Any other error code (401 bad key, 500 TMDB problem...) raises an exception
        response.raise_for_status()

        # Everything went well: return the answer as a Python dict
        return response.json()

    @staticmethod
    def _build_poster_url(poster_path: Optional[str]) -> Optional[str]:
        """Build the full poster URL from the end of the address given by TMDB."""
        if not poster_path:
            return None
        return TMDB_POSTER_BASE_URL + poster_path

    @staticmethod
    def _empty_to_none(value):
        """TMDB sometimes returns "" or 0 when it has no information: we store None instead."""
        if not value:
            return None
        return value

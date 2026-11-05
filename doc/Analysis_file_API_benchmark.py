import os
import time

import requests
from dotenv import load_dotenv


load_dotenv()

OMDB_API_KEY = os.getenv("OMDB_API_KEY")
TMDB_API_KEY = os.getenv("TMDB_API_KEY")


OMDB_URL = "https://www.omdbapi.com/"
TMDB_SEARCH_URL = "https://api.themoviedb.org/3/search/movie"
TMDB_MOVIE_URL = "https://api.themoviedb.org/3/movie"
TMDB_IMAGE_URL = "https://image.tmdb.org/t/p/w500"


TEST_MOVIES = [
    "Oppenheimer",
    "12 Angry Men",
    "Intouchables",
    "Anatomie d'une chute",
    "Incendies",
    "The Handmaiden",
    "A Separation",
    "Perfect Days",
    "Persepolis",
    "The Lives of Others",
    "Suspiria",
    "CODA",
    "The Worst Person in the World",
    "Close",
    "The Man Who Sold His Skin",
]


def get_omdb_movie(title):
    """Retrieve movie information from OMDb."""

    start = time.perf_counter()

    response = requests.get(
        OMDB_URL,
        params={
            "apikey": OMDB_API_KEY,
            "t": title,
            "type": "movie",
        },
        timeout=10,
    )

    response.raise_for_status()
    data = response.json()

    elapsed = time.perf_counter() - start

    if data.get("Response") != "True":
        return None, elapsed

    movie = {
        "title": data.get("Title"),
        "year": data.get("Year"),
        "runtime": data.get("Runtime"),
        "genres": data.get("Genre"),
        "overview": data.get("Plot"),
        "poster": (
            data.get("Poster")
            if data.get("Poster") != "N/A"
            else None
        ),
    }

    return movie, elapsed


def get_tmdb_movie(title):
    """Search a movie on TMDB, then retrieve its full details."""

    start = time.perf_counter()

    # First request: search for the movie
    search_response = requests.get(
        TMDB_SEARCH_URL,
        params={
            "api_key": TMDB_API_KEY,
            "query": title,
            "language": "en-US",
        },
        timeout=10,
    )

    search_response.raise_for_status()
    search_data = search_response.json()

    results = search_data.get("results", [])

    if not results:
        return None, time.perf_counter() - start

    movie_id = results[0]["id"]

    # Second request: retrieve full movie details
    details_response = requests.get(
        f"{TMDB_MOVIE_URL}/{movie_id}",
        params={
            "api_key": TMDB_API_KEY,
            "language": "en-US",
        },
        timeout=10,
    )

    details_response.raise_for_status()
    data = details_response.json()

    elapsed = time.perf_counter() - start

    poster = None

    if data.get("poster_path"):
        poster = TMDB_IMAGE_URL + data["poster_path"]

    movie = {
        "title": data.get("title"),
        "year": data.get("release_date", "")[:4],
        "runtime": data.get("runtime"),
        "genres": [
            genre["name"]
            for genre in data.get("genres", [])
        ],
        "overview": data.get("overview"),
        "poster": poster,
    }

    return movie, elapsed


def benchmark_api(api_name, movie_function):
    """Run the benchmark for one API."""

    print(f"\n=== {api_name} ===")

    times = []
    found = 0
    posters = 0
    overviews = 0

    for title in TEST_MOVIES:

        try:
            movie, elapsed = movie_function(title)

        except requests.RequestException as error:
            print(f"{title} -> request error: {error}")
            continue

        if movie is None:
            print(f"{title} -> not found")
            continue

        found += 1
        times.append(elapsed)

        if movie["poster"]:
            posters += 1

        if movie["overview"]:
            overviews += 1

        print(
            f"{title} -> "
            f"{movie['title']} ({movie['year']}) | "
            f"{elapsed:.2f} s | "
            f"poster: {bool(movie['poster'])} | "
            f"overview: {bool(movie['overview'])}"
        )

    average_time = sum(times) / len(times) if times else 0

    print(f"\n--- {api_name} SUMMARY ---")
    print(f"Movies found: {found}/{len(TEST_MOVIES)}")
    print(f"Poster available: {posters}/{found}")
    print(f"Overview available: {overviews}/{found}")
    print(f"Average full retrieval time: {average_time:.2f} s")

    return average_time


def main():

    if not OMDB_API_KEY or not TMDB_API_KEY:
        raise RuntimeError(
            "Missing API keys. Set OMDB_API_KEY and TMDB_API_KEY "
            "as environment variables."
        )

    omdb_time = benchmark_api("OMDb", get_omdb_movie)
    tmdb_time = benchmark_api("TMDB", get_tmdb_movie)

    print("\n=== FINAL COMPARISON ===")
    print(f"OMDb average full retrieval time: {omdb_time:.2f} s")
    print(f"TMDB average full retrieval time: {tmdb_time:.2f} s")


if __name__ == "__main__":
    main()

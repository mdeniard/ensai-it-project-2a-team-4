from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status

from src.App.UserController import require_admin
from src.Business_object.Movie import Movie
from src.Model.MovieModel import MovieModel
from src.Service.MovieService import MovieService

movie_router = APIRouter(prefix="/movies", tags=["Movies"])

admin_movie_router = APIRouter(
    prefix="/admin/movies",
    tags=["Movies"],
    dependencies=[Depends(require_admin)],
)


# ---------- Public routes ----------


@movie_router.get("/{tmdb_id}", summary="Get movie by id", status_code=status.HTTP_200_OK)
def get_movie_by_id(tmdb_id: int):
    """
    Get a movie of the theater database.

    Args:

    * tmdb_id: the id of the movie in our database (not the TMDB id)
    """
    try:
        my_movie = MovieService().get_by_id(tmdb_id)
        return my_movie
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Movie with id [{}] not found".format(tmdb_id),
        ) from FileNotFoundError
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid request") from Exception


@movie_router.get("/", summary="Get screening movies", status_code=status.HTTP_200_OK)
def get_screening_movies():
    """
    Get all the movies of the theater database.
    """
    try:
        screening_movies = MovieService().get_screening_movies()
        return screening_movies
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Movie not found",
        ) from FileNotFoundError
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid request") from Exception


# ---------- Admin routes ----------


@admin_movie_router.get("/search", summary="Search movies on TMDB", status_code=status.HTTP_200_OK)
def search_movies_on_tmdb(
    title: str,
    year: Optional[int] = None,
):
    """
    Search movies on TMDB. The administrator uses the result to choose which movie to import.

    Args:

    * title: the title (or part of the title) of the movie, must not be empty
    * year: the release year, to reduce ambiguity (optional)
    """
    try:
        movies_found = MovieService().search_tmdb(title, year)
        return movies_found
    except ValueError as e:
        # The title is empty
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    except Exception as e:
        # Problem when calling TMDB (wrong API key, TMDB unavailable...)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error while searching on TMDB: {str(e)}",
        ) from e


@admin_movie_router.post("/import/{tmdb_id}", summary="Import a movie from TMDB", status_code=status.HTTP_201_CREATED)
def import_movie_from_tmdb(
    tmdb_id: int,
):
    """
    Get a movie from TMDB and save it in our database.
    Refused (409) if the movie is already in the catalogue.

    Args:

    * tmdb_id: the TMDB id of the movie to import (found with the search route)
    """
    try:
        imported_movie = MovieService().import_from_tmdb(tmdb_id)
    except ValueError as e:
        # The movie is already in our catalogue
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e)) from e
    except Exception as e:
        # Problem when calling TMDB or the database
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error while importing movie: {str(e)}",
        ) from e

    # The service returns None when TMDB does not know this tmdb_id
    if imported_movie is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Movie with tmdb_id [{tmdb_id}] not found on TMDB",
        )

    return imported_movie


@admin_movie_router.post("/", summary="Create a movie", status_code=status.HTTP_201_CREATED)
def create_movie(
    m: MovieModel,
):
    """
    Create a movie by giving all its data by hand (to get it from TMDB, use the import route).

    Args:

    * m: the data of the movie (tmdb_id, title, description, duration, released_date, rating, poster_url)
    """
    try:
        created_movie = MovieService().create_movie(
            Movie(m.tmdb_id, m.title, m.description, m.duration, m.released_date, m.rating, m.poster_url)
        )
        return created_movie
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error while creating movie: {str(e)}"
        ) from e


@admin_movie_router.put("/{movie_id}", summary="Update a movie", status_code=status.HTTP_200_OK)
def update_movie(
    movie_id: int,
    m: MovieModel,
):
    """
    Update a movie of the theater database.

    Args:

    * movie_id: the id of the movie in our database
    * m: the new data of the movie (tmdb_id, title, description, duration, released_date, rating, poster_url)
    """
    try:
        updated_movie = MovieService().update_movie(
            Movie(m.tmdb_id, m.title, m.description, m.duration, m.released_date, m.rating, m.poster_url, id=movie_id)
        )

        if updated_movie is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Movie with id [{movie_id}] not found")

        return updated_movie
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error while updating movie: {str(e)}"
        ) from e


@admin_movie_router.delete("/{movie_id}", summary="Delete a movie", status_code=status.HTTP_200_OK)
def delete_movie(
    movie_id: int,
    confirm: bool = False,
):
    """
    Delete a movie, with its screenings and its reviews.
    Refused (409) if tickets were already sold for this movie, so that the sales stay in the accounting.

    Args:

    * movie_id: the id of the movie in our database
    * confirm: must be true to confirm the deletion (default false, the request is then refused)
    """
    if not confirm:
        raise HTTPException(
            status_code=409,
            detail="Confirmation required: repeat the request with confirm=True",
        )
    try:
        is_deleted = MovieService().delete_movie(movie_id)
        if not is_deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Movie with id [{movie_id}] not found")
        return {"message": f"Movie with id [{movie_id}] successfully deleted"}
    except HTTPException:
        raise
    except ValueError as e:
        # Tickets were already sold for this movie
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error while deleting movie: {str(e)}"
        ) from e

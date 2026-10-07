from fastapi import APIRouter, HTTPException, status

from src.Business_object.Movie import Movie
from src.Model.MovieModel import MovieModel
from src.Service.MovieService import MovieService

movie_router = APIRouter(prefix="/movies", tags=["Movies"])


@movie_router.get("/{tmdb_id}", status_code=status.HTTP_200_OK)
def get_movie_by_id(tmdb_id: int):
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

@movie_router.get("/", status_code=status.HTTP_200_OK)
def get_screening_movies():
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

@movie_router.post("/", status_code=status.HTTP_201_CREATED)
def create_movie(m: MovieModel):
    try:
        created_movie = MovieService().create_movie(
            Movie(m.tmdb_id,
            m.title,
            m.description,
            m.duration,
            m.released_date,
            m.rating,
            m.poster_url)
        )
        return created_movie
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error while creating movie: {str(e)}"
        ) from e

@movie_router.put("/{movie_id}", status_code=status.HTTP_200_OK)
def update_movie(movie_id: int, m: MovieModel):
    try:
        updated_movie = MovieService().update_movie(
            Movie(m.tmdb_id,
            m.title,
            m.description,
            m.duration,
            m.released_date,
            m.rating,
            m.poster_url,
            id=movie_id)
        )

        if updated_movie is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Movie with id [{movie_id}] not found"
            )

        return updated_movie
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error while updating movie: {str(e)}"
        ) from e

@movie_router.delete("/{movie_id}", status_code=status.HTTP_200_OK)
def delete_movie(movie_id: int):
    try:
        is_deleted = MovieService().delete_movie(movie_id)
        if not is_deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Movie with id [{movie_id}] not found"
            )
        return {"message": f"Movie with id [{movie_id}] successfully deleted"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error while deleting movie: {str(e)}"
        ) from e

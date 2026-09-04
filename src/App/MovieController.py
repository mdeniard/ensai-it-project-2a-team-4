from fastapi import APIRouter, HTTPException, status

from src.Model.Movie import Movie

movie_router = APIRouter(prefix="/movies", tags=["Movies"])


@movie_router.get("/{tmdb_id}", status_code=status.HTTP_200_OK)
def get_movie_by_id(tmdb_id: int):
    try:
        # my_movie = movie_service.get_by_id(tmdb_id)
        my_movie = Movie(original_title="The Wild Robot", id=1)
        return my_movie
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Movie with id [{}] not found".format(tmdb_id),
        ) from FileNotFoundError
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid request") from Exception

from pydantic import BaseModel


class MovieModel(BaseModel):
    """Body of the request to add a movie by hand."""

    tmdb_id: int
    title: str
    description: str
    duration: int
    released_date: str
    rating: float
    poster_url: str

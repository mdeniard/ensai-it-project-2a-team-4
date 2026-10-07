from pydantic import BaseModel


class MovieModel(BaseModel):
    tmdb_id: int
    title: str
    description: str
    duration: int
    released_date: str
    rating: float
    poster_url: str
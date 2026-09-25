from datetime import date

from pydantic import BaseModel


class Movie(BaseModel):
    id: int
    tmdb_id: int
    title: str
    description: str
    duration: int
    released_date: date
    rating: float
    poster_url: str
    original_title: str

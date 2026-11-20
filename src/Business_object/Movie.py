from typing import Optional


class Movie:
    """A movie of the catalogue, imported from TMDB (tmdb_id) and saved in our database (id)."""

    def __init__(
        self,
        tmdb_id: int,
        title: str,
        description: Optional[str],
        duration: Optional[int],
        released_date: Optional[str],
        rating: Optional[float],
        poster_url: Optional[str],
        id: Optional[int] = None,
    ):
        self.id = id
        self.tmdb_id = tmdb_id
        self.title = title
        self.description = description
        self.duration = duration
        self.released_date = released_date
        self.rating = rating
        self.poster_url = poster_url

    def __str__(self) -> str:
        return f"Movie(id={self.id}, title='{self.title}', released_date='{self.released_date}', rating={self.rating})"

from typing import Optional


class Movie:
    def __init__(
        self,
        tmdb_id: int,
        title: str,
        description: str,
        duration: int,
        released_date: str,
        rating: float,
        poster_url: str,
        id: Optional[int] = None
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
        return (
            f"Movie(id={self.id}, title='{self.title}', "
            f"released_date='{self.released_date}', rating={self.rating})"
        )

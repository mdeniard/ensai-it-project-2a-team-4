class Movie:
    def __init__(
        self,
        id: int,
        tmdb_id: int,
        title: str,
        description: str,
        duration: int,
        released_date: str,
        rating: float,
        poster_url: str
    ):
        self.id = id
        self.tmdb_id = tmdb_id
        self.title = title
        self.description = description
        self.duration = duration
        self.released_date = released_date
        self.rating = rating
        self.poster_url = poster_url

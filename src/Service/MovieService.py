from src.Model.Movie import Movie


class MovieService:
    movie_db: None

    def __init__(self, movie_db: None):
        self.movie_db = movie_db

    def get_by_id(self, movie_id: int) -> Movie:
        return Movie(id=1, original_title="A Clockwork Orange")
        # return self.movie_db.get_by_id(movie_id)

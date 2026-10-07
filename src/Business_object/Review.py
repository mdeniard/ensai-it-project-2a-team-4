from datetime import datetime


class Review:
    def __init__(
        self,
        id: int,
        customer_id: int,
        movie_id: int,
        rating: int,
        comment: str,
        created_at: datetime
    ):
        self.id = id
        self.customer_id = customer_id
        self.movie_id = movie_id
        self.rating = rating
        self.comment = comment
        self.created_at = created_at

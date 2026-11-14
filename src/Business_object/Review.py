from datetime import datetime
from typing import Optional


class Review:
    def __init__(
        self,
        customer_id: int,
        movie_id: int,
        rating: int,
        comment: Optional[str] = None,
        # None until the review is saved (the date is set by the database)
        created_at: Optional[datetime] = None,
        id: Optional[int] = None,
    ):
        self.id = id
        self.customer_id = customer_id
        self.movie_id = movie_id
        self.rating = rating
        self.comment = comment
        self.created_at = created_at

    def __str__(self) -> str:
        return f"Review #{self.id} (Customer: {self.customer_id}, Movie: {self.movie_id}) : {self.rating}/5"
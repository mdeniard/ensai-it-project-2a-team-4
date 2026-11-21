from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from datetime import datetime


class Review:
    """The review of a movie by a customer: a rating from 1 to 10 and an optional comment."""

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
        return f"Review #{self.id} (Customer: {self.customer_id}, Movie: {self.movie_id}) : {self.rating}/10"

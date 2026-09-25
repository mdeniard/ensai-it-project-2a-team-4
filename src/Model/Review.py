from datetime import datetime
from pydantic import BaseModel


class Review(BaseModel):
    id: int
    customer_id: int
    movie_id: int
    rating: int
    comment: str
    created_at: datetime

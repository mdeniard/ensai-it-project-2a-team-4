from typing import Optional

from pydantic import BaseModel, Field


class ReviewModel(BaseModel):
    """Body of the request to write a review (rating from 1 to 10, optional comment)."""

    movie_id: int
    rating: int = Field(ge=1, le=10)
    comment: Optional[str] = None

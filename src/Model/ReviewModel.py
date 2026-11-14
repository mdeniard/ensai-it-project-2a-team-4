from typing import Optional

from pydantic import BaseModel, Field


class ReviewModel(BaseModel):
    movie_id: int
    rating: int = Field(ge=1, le=10)
    comment: Optional[str] = None

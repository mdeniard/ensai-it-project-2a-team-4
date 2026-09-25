from datetime import datetime

from pydantic import BaseModel


class Screening(BaseModel):
    id: int
    movie_id: int
    room_id: int
    start_time: datetime
    end_time: datetime

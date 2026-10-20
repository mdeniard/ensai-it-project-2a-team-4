from datetime import datetime

from pydantic import BaseModel


class ScreeningModel(BaseModel):
    movie_id: int
    room_id: int
    start_time: datetime

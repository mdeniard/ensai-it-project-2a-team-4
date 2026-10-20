from datetime import datetime
from typing import Optional


class Screening:
    def __init__(
        self,
        movie_id: int,
        room_id: int,
        start_time: datetime,
        end_time: datetime,
        id: Optional[int] = None,
    ):
        self.id = id
        self.movie_id = movie_id
        self.room_id = room_id
        self.start_time = start_time
        self.end_time = end_time

    def __str__(self) -> str:
            start_str = self.start_time.strftime("%Y-%m-%d %H:%M")
            end_str = self.end_time.strftime("%H:%M")
            return f"Screening #{self.id} (Movie ID: {self.movie_id}, Room ID: {self.room_id}) : {start_str} -> {end_str}"

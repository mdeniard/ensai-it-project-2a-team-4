from datetime import datetime


class Screening:
    def __init__(
        self,
        id: int,
        movie_id: int,
        room_id: int,
        start_time: datetime,
        end_time: datetime,
    ):
        self.id = id
        self.movie_id = movie_id
        self.room_id = room_id
        self.start_time = start_time
        self.end_time = end_time

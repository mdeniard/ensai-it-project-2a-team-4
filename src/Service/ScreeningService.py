from datetime import datetime, timedelta
from typing import Optional
from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

LOCAL_TZ = ZoneInfo("Europe/Paris")

from src.Business_object.Screening import Screening
from src.DAO.ScreeningRepo import ScreeningRepo
from src.DAO.MovieRepo import MovieRepo
from src.DAO.RoomRepo import RoomRepo


class ScreeningService:
    """Service that manages rooms."""

    def __init__(
        self,
        screening_repo: Optional[ScreeningRepo] = None,
        movie_repo: Optional[MovieRepo] = None,
        room_repo: Optional[RoomRepo] = None,
    ):
        self.screening_repo = screening_repo or ScreeningRepo()
        self.movie_repo = movie_repo or MovieRepo()
        self.room_repo = room_repo or RoomRepo()

    def filter_screenings(
        self, movie_id: Optional[int] = None, day: Optional[date] = None
    ) -> list[Screening]:
        now = datetime.now(timezone.utc)
        start_from = now

        if day is not None:
            # "day" is interpreted in local time, not UTC
            day_start = datetime.combine(day, time.min, tzinfo=LOCAL_TZ)
            start_from = max(now, day_start)  # never show past screenings

        return self.screening_repo.filter_screenings(start_from, movie_id)

    def room_schedule(self, room_number: int) -> list[Screening]:
        return self.screening_repo.room_schedule(room_number)

    def create_screening(self, movie_id: int, room_id: int, start_time: datetime) -> Screening:
        movie = self.movie_repo.get_by_id(movie_id)
        if not movie:
            raise LookupError(f"Movie [{movie_id}] not found")

        room = self.room_repo.get_by_id(room_id)
        if not room:
            raise LookupError(f"Room [{room_id}] not found")

        end_time = start_time + timedelta(minutes=movie.duration) + timedelta(minutes=20)

        if not self.screening_repo.session_is_available(room_id, start_time, end_time):
            raise ValueError("The room is already booked on this time slot")

        return self.screening_repo.create_screening(
            Screening(movie_id=movie_id, room_id=room_id, start_time=start_time, end_time=end_time)
        )

    def delete_screening(self, screening_id: int) -> bool:
        return self.screening_repo.delete_screening(screening_id)

from datetime import datetime, timedelta
from typing import Optional
from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

LOCAL_TZ = ZoneInfo("Europe/Paris")

from src.Business_object.Screening import Screening
from src.DAO.ScreeningRepo import ScreeningRepo
from src.DAO.MovieRepo import MovieRepo
from src.DAO.RoomRepo import RoomRepo
from src.DAO.ReservationRepo import ReservationRepo


class ScreeningService:
    """Service that manages screenings (schedule of the rooms and creation by the administrators)."""

    def __init__(
        self,
        screening_repo: Optional[ScreeningRepo] = None,
        movie_repo: Optional[MovieRepo] = None,
        room_repo: Optional[RoomRepo] = None,
        reservation_repo: Optional[ReservationRepo] = None,
    ):
        """Create the service.
        Args:
            screening_repo (ScreeningRepo, optional): Access to the screenings in the database.
            movie_repo (MovieRepo, optional): Access to the movies in the database.
            room_repo (RoomRepo, optional): Access to the rooms in the database.
            reservation_repo (ReservationRepo, optional): Access to the reservations in the database.
                If one is not given, a new one is created.
        """
        self.screening_repo = screening_repo or ScreeningRepo()
        self.movie_repo = movie_repo or MovieRepo()
        self.room_repo = room_repo or RoomRepo()
        self.reservation_repo = reservation_repo or ReservationRepo()

    def filter_screenings(self, movie_id: Optional[int] = None, day: Optional[date] = None) -> list[Screening]:
        """List the upcoming screenings, sorted by start time (50 at most).
        The screenings already started are never returned.
        Args:
            movie_id (int, optional): Only the screenings of this movie (its id in our database).
            day (date, optional): Only the screenings from the start of this day on.
                The day is read in Paris time, and a day in the past is replaced by the current moment.
        Returns:
            list[Screening] of the matching screenings, or an empty list if there is none.
        """
        now = datetime.now(timezone.utc)
        start_from = now

        if day is not None:
            # "day" is interpreted in local time, not UTC
            day_start = datetime.combine(day, time.min, tzinfo=LOCAL_TZ)
            start_from = max(now, day_start)  # never show past screenings

        return self.screening_repo.filter_screenings(start_from, movie_id)

    def room_schedule(self, room_number: int) -> list[Screening]:
        """List the upcoming screenings of a room, sorted by start time.
        Args:
            room_number (int): The number of the room (not its database id).
        Returns:
            list[Screening] of the room, or an empty list if there is none.
        """
        return self.screening_repo.room_schedule(room_number)

    def create_screening(self, movie_id: int, room_id: int, start_time: datetime, base_price: float) -> Screening:
        """Create a screening. The end time is computed: start time + duration of the movie + 20 minutes.
        The screening is refused if the base price is not positive, if the movie or the room
        does not exist, or if the room is already booked during this time slot.
        Args:
            movie_id (int): The database id of the movie.
            room_id (int): The database id of the room.
            start_time (datetime): The start of the screening.
            base_price (float): The base price of a ticket (multiplied by the coefficient
                of the ticket type when a customer books).
        Returns:
            The saved Screening, with its id and its end time.
        """
        # The base price of a ticket must be positive
        if base_price <= 0:
            raise ValueError("The base price must be greater than 0")

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
            Screening(
                movie_id=movie_id,
                room_id=room_id,
                start_time=start_time,
                end_time=end_time,
                base_price=base_price,
            )
        )

    def delete_screening(self, screening_id: int) -> bool:
        """Delete a screening that has no ticket sold.
        A screening with tickets sold cannot be deleted: its reservations would be deleted too
        (ON DELETE CASCADE), so the sales would disappear from the accounting.
        Args:
            screening_id (int): The database id of the screening to delete.
        Returns:
            True if the screening was deleted, False if no screening has this id.
        Raises:
            ValueError if tickets were already sold for this screening.
        """
        # Refuse the deletion if at least one ticket was sold
        tickets_sold = self.reservation_repo.count_screening_reservations(screening_id)
        if tickets_sold > 0:
            raise ValueError(f"{tickets_sold} ticket(s) already sold for this screening, it cannot be deleted")

        # No ticket sold: the screening can be deleted safely
        return self.screening_repo.delete_screening(screening_id)

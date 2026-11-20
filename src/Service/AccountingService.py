from datetime import datetime
from decimal import Decimal
from typing import Optional

from src.DAO.MovieRepo import MovieRepo
from src.DAO.ReservationRepo import ReservationRepo


class AccountingService:
    """Service that manages the accounting (revenue and tickets sold) of the movies."""

    def __init__(
        self, reservation_repo: Optional[ReservationRepo] = None, movie_repo: Optional[MovieRepo] = None
    ) -> None:
        """Create the service.
        Args:
            reservation_repo (ReservationRepo, optional): Access to the reservations in the database.
            movie_repo (MovieRepo, optional): Access to the movies in the database.
                If one is not given, a new one is created.
        """
        self.reservation_repo = reservation_repo or ReservationRepo()
        self.movie_repo = movie_repo or MovieRepo()

    def detailed_accounting_by_movie(
        self, movie_id, start_from: Optional[datetime] = None, end_at: Optional[datetime] = None
    ):
        """Compute the tickets sold and the revenue of each screening of a movie.
        Only the reservations made between the two dates are counted.
        The request is refused if the movie does not exist or if the start date is not before the end date.
        Args:
            movie_id (int): The database id of the movie.
            start_from (datetime, optional): Only the reservations made from this date on.
            end_at (datetime, optional): Only the reservations made until this date.
        Returns:
            list[dict] with one row per screening, sorted by start time. Each row contains
            movie_id, screening_id, start_time, tickets_sold and revenue.
        """
        movie = self.movie_repo.get_by_id(movie_id)
        if not movie:
            raise LookupError(f"Movie [{movie_id}] not found")

        if start_from is not None and end_at is not None and start_from >= end_at:
            raise ValueError("The start date is after the end date")

        return self.reservation_repo.get_accounting_by_movie(movie_id, start_from, end_at)

    def get_accounting_by_movie(
        self, movie_id, start_from: Optional[datetime] = None, end_at: Optional[datetime] = None
    ):
        """Compute the total tickets sold and the total revenue of a movie, over all its screenings.
        Only the reservations made between the two dates are counted.
        Args:
            movie_id (int): The database id of the movie.
            start_from (datetime, optional): Only the reservations made from this date on.
            end_at (datetime, optional): Only the reservations made until this date.
        Returns:
            dict with the movie_id, the total_revenue and the total_tickets.
        """
        screenings = self.detailed_accounting_by_movie(movie_id, start_from, end_at)

        total_revenue = sum((screening["revenue"] for screening in screenings), Decimal("0"))

        total_tickets = sum(screening["tickets_sold"] for screening in screenings)

        return {"movie_id": movie_id, "total_revenue": total_revenue, "total_tickets": total_tickets}

    def get_accounting_by_period(self, start_at: datetime, end_date: datetime, movies: Optional[list[int]] = None):
        """Compute the accounting of several movies over a period.
        Args:
            start_at (datetime): Only the reservations made from this date on.
            end_date (datetime): Only the reservations made until this date (must be after start_at).
            movies (list[int], optional): The database ids of the movies to include.
                If none is given, all the movies of the database are included.
        Returns:
            list[dict] with one row per movie, each one with the movie_id, the total_revenue
            and the total_tickets (same content as get_accounting_by_movie).
        """
        if movies is None:
            movies_list = self.movie_repo.get_screening_movies()
            movies = [m.id for m in movies_list]
        return [self.get_accounting_by_movie(m, start_at, end_date) for m in movies]

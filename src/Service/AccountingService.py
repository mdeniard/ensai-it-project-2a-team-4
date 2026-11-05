from datetime import datetime
from decimal import Decimal
from typing import Optional

from src.DAO.MovieRepo import MovieRepo
from src.DAO.ReservationRepo import ReservationRepo


class AccountingService:
    """Class that manages accouting"""
    def __init__(
        self,
        reservation_repo: Optional[ReservationRepo] = None,
        movie_repo: Optional[MovieRepo] = None
    ) -> None:
        self.reservation_repo = reservation_repo or ReservationRepo()
        self.movie_repo = movie_repo or MovieRepo()

    def detailed_accounting_by_movie(
        self,
        movie_id,
        start_from: Optional[datetime]= None,
        end_at: Optional[datetime] = None
    ):
        movie = self.movie_repo.get_by_id(movie_id)
        if not movie:
            raise LookupError(f"Movie [{movie_id}] not found")

        if start_from is not None and end_at is not None and start_from >= end_at:
            raise ValueError("The start date is after the end date")

        return self.reservation_repo.get_accounting_by_movie(
            movie_id,
            start_from,
            end_at
        )

    def get_accounting_by_movie(
        self,
        movie_id,
        start_from: Optional[datetime]= None,
        end_at: Optional[datetime] = None
    ):
        screenings = self.detailed_accounting_by_movie(
            movie_id,
            start_from,
            end_at
        )

        total_revenue = sum(
            (screening["revenue"] for screening in screenings),
            Decimal("0")
        )

        total_tickets = sum(
            screening["tickets_sold"] for screening in screenings
        )

        return {"movie_id": movie_id, "total_revenue": total_revenue, "total_tickets": total_tickets}

    def get_accounting_by_period(
        self,
        start_at: datetime,
        end_date: datetime,
        movies: Optional[list[int]] = None
    ):
        if movies is None:
            movies_list = self.movie_repo.get_screening_movies()
            movies = [m.id for m in movies_list]
        return [self.get_accounting_by_movie(m, start_at, end_date) for m in movies]

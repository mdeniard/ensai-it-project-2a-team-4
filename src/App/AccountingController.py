from typing_extensions import Optional
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Query

from src.Service.AccountingService import AccountingService

from .UserController import require_admin


admin_accounting_router = APIRouter(
    prefix="/admin/accounting",
    tags=["Accounting"],
    dependencies=[Depends(require_admin)],
)


@admin_accounting_router.get("/movies/{movie_id}", summary="Get accounting by movie", status_code=status.HTTP_200_OK)
def get_accounting_by_movie(
    movie_id: int,
    start_from: Optional[datetime] = None,
    end_at: Optional[datetime] = None
):
    """
    Get the total revenue and the total number of tickets sold for a movie, over all its screenings.
    Only the reservations made between the two dates are counted.

    Args:

    * movie_id: the id of the movie in our database
    * start_from: only the reservations made from this date on (optional)
    * end_at: only the reservations made until this date (optional, must be after start_from)
    """
    try:
        accounting = AccountingService().get_accounting_by_movie(movie_id, start_from, end_at)
        return accounting
    except LookupError as e:
        raise HTTPException(
            status_code=404,
            detail="Movie not found",
        ) from e
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail="Invalid request: The start date is after the end date",
        ) from e

@admin_accounting_router.get("/movies/{movie_id}/details", summary="Detailed accounting for one movie", status_code=status.HTTP_200_OK)
def detailed_accounting_by_movie(
    movie_id: int,
    start_from: Optional[datetime] = None,
    end_at: Optional[datetime] = None
):
    """
    Get the revenue and the number of tickets sold for each screening of a movie.
    Only the reservations made between the two dates are counted.

    Args:

    * movie_id: the id of the movie in our database
    * start_from: only the reservations made from this date on (optional)
    * end_at: only the reservations made until this date (optional, must be after start_from)
    """
    try:
        accounting = AccountingService().detailed_accounting_by_movie(movie_id, start_from, end_at)
        return accounting
    except LookupError as e:
        raise HTTPException(
            status_code=404,
            detail="Movie not found",
        ) from e
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail="Invalid request: The start date is after the end date",
        ) from e

@admin_accounting_router.get("/period", summary="Get accounting by period", status_code=status.HTTP_200_OK)
def get_accounting_by_period(
    start_from: datetime,
    end_at: datetime,
    movies: Annotated[Optional[list[int]], Query()]= None
):
    """
    Get the total revenue and the number of tickets sold for several movies over a period.
    Without `movies`, all the movies of the database are included.
    Example: /admin/accounting/period?start_from=...&end_at=...&movies=1&movies=2

    Args:

    * start_from: only the reservations made from this date on
    * end_at: only the reservations made until this date (must be after start_from)
    * movies: the ids of the movies to include, repeat the parameter for each movie (optional)
    """
    try:
        accounting = AccountingService().get_accounting_by_period(start_from, end_at, movies)
        return accounting
    except LookupError as e:
        raise HTTPException(
            status_code=404,
            detail="Movie not found",
        ) from e
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail="Invalid request: The start date is after the end date",
        ) from e
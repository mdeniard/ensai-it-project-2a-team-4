from typing_extensions import Optional
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import HTTPAuthorizationCredentials

from src.Service.AccountingService import AccountingService

from .JWTBearer import JWTBearer
from .UserController import get_admin_from_credentials


def require_admin(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(JWTBearer())],
):
    return get_admin_from_credentials(credentials)

accounting_router = APIRouter(
    prefix="/accounting",
    tags=["Accounting"],
    dependencies=[Depends(require_admin)],
)

# All the routes of this controller require to be logged in (JWTBearer):

@accounting_router.get("/movies/{movie_id}", summary="Get accounting by movie (Admin Only)", status_code=status.HTTP_200_OK)
def get_accounting_by_movie(
    movie_id: int,
    start_from: Optional[datetime] = None,
    end_at: Optional[datetime] = None
):
    """
    Get the revenue and the number of tickets sold for a movie,
    optionally between two dates.
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

@accounting_router.get("/movies/{movie_id}/details", summary="Detailed accounting for one movie (Admin Only)", status_code=status.HTTP_200_OK)
def detailed_accounting_by_movie(
    movie_id: int,
    start_from: Optional[datetime] = None,
    end_at: Optional[datetime] = None
):
    """
    Get the revenue and the number of tickets sold for each screening of a movie,
    optionally between two dates.
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

@accounting_router.get("/period", summary="Get accounting by period (Admin Only)", status_code=status.HTTP_200_OK)
def get_accounting_by_period(
    start_from: datetime,
    end_at: datetime,
    movies: Annotated[Optional[list[int]], Query()]= None
):
    """
    Get the accounting of several movies over a period.
    Without `movies`, all the movies currently screened are included.
    Example: /accounting/period?start_from=...&end_at=...&movies=1&movies=2
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

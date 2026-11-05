from typing_extensions import Optional
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials

from src.Service.AccountingService import AccountingService

from .JWTBearer import JWTBearer
from .UserController import get_user_from_credentials

accounting_router = APIRouter(prefix="/accounting", tags=["Accounting"])

# All the routes of this controller require to be logged in (JWTBearer):
# in the Swagger, log in with POST /users/jwt, then paste the token in "Authorize"

@accounting_router.get("/movies/{movie_id}?start_from=&end_at=", status_code=status.HTTP_200_OK)
def get_accounting_by_movie(
    movie_id: int,
    start_from: Optional[datetime] = None,
    end_at: Optional[datetime] = None
):
    """
    Get one of my reservations by its id
    """
    try:
        accounting = AccountingService().get_accounting_by_movie(movie_id, start_from, end_at)
        return accounting
    except LookupError as e:
        raise HTTPException(
            status_code=404,
            detail="Movie not found",
        ) from e
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid request: The start date is after the end date",
        ) from FileNotFoundError

@accounting_router.get("/movies/{movie_id}/details?start_from=&end_at=", status_code=status.HTTP_200_OK)
def detailed_accounting_by_movie(
    movie_id: int,
    start_from: Optional[datetime] = None,
    end_at: Optional[datetime] = None
):
    """
    Get one of my reservations by its id
    """
    try:
        accounting = AccountingService().detailed_accounting_by_movie(movie_id, start_from, end_at)
        return accounting
    except LookupError as e:
        raise HTTPException(
            status_code=404,
            detail="Movie not found",
        ) from e
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid request: The start date is after the end date",
        ) from FileNotFoundError

@accounting_router.get("/period?start_from=&end_at=&movie1=&movie2=", status_code=status.HTTP_200_OK)
def get_accounting_by_period(
    start_from: datetime,
    end_at: datetime,
    movies: Optional[list[int]]= None
):
    """
    Get accounting by period
    """
    try:
        accounting = AccountingService().get_accounting_by_period(start_from, end_at, movies)
        return accounting
    except LookupError as e:
        raise HTTPException(
            status_code=404,
            detail="Movie not found",
        ) from e
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid request: The start date is after the end date",
        ) from FileNotFoundError

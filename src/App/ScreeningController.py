from src.App import JWTBearer
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials
from typing import Annotated
from typing import Optional

from fastapi import APIRouter, HTTPException, status

from datetime import date

from src.Business_object.Screening import Screening
from src.Model.ScreeningModel import ScreeningModel
from src.Service.ScreeningService import ScreeningService
from src.App.UserController import get_admin_from_credentials, get_user_from_credentials

screening_router = APIRouter(prefix="/screenings", tags=["Screenings"])

@screening_router.get("/rooms/{room_number}", summary="Get room Schedule", status_code=status.HTTP_200_OK)
def get_room_schedule(room_number: int):
    """
    Upcoming screenings of a room
    """
    return ScreeningService().room_schedule(room_number)

@screening_router.get("/", summary="Get upcoming screenings", status_code=status.HTTP_200_OK)
def get_upcoming_screenings(
    movie_id: Optional[int] = None,
    day: Optional[date] = None,
):
    """
    List upcoming screenings, optionally filtered by movie and/or day (YYYY-MM-DD)
    """
    return ScreeningService().filter_screenings(movie_id, day)

@screening_router.post("/", summary="Create a screening (Admin Only)", status_code=status.HTTP_201_CREATED)
def create_screening(
    s: ScreeningModel,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(JWTBearer())],
):
    """
    Create a screening
    """
    try:
        get_admin_from_credentials(credentials)
        return ScreeningService().create_screening(s.movie_id, s.room_id, s.start_time, s.base_price)
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e)) from e

@screening_router.delete("/{screening_id}", summary="Delete a screening (Admin Only)", status_code=status.HTTP_204_NO_CONTENT)
def delete_screening(
    screening_id: int,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(JWTBearer())],
    confirm: bool = False,
) -> None:
    """
    Delete a screening by its id
    """
    if not confirm:
        raise HTTPException(
            status_code=409,
            detail="Confirmation required: repeat the request with confirm=True",
        )
    try:
        get_admin_from_credentials(credentials)
        if not ScreeningService().delete_screening(screening_id):
            raise HTTPException(status_code=404, detail="Screening not found")

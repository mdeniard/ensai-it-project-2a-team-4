from typing import Optional

from fastapi import APIRouter, HTTPException, status

from datetime import date

from src.Business_object.Screening import Screening
from src.Model.ScreeningModel import ScreeningModel
from src.Service.ScreeningService import ScreeningService

screening_router = APIRouter(prefix="/screenings", tags=["Screenings"])

@screening_router.get("/rooms/{room_number}", status_code=status.HTTP_200_OK)
def get_room_schedule(room_number: int):
    """
    Upcoming screenings of a room
    """
    return ScreeningService().room_schedule(room_number)

@screening_router.get("/", status_code=status.HTTP_200_OK)
def get_upcoming_screenings(
    movie_id: Optional[int] = None,
    day: Optional[date] = None,
):
    """
    List upcoming screenings, optionally filtered by movie and/or day (YYYY-MM-DD)
    """
    return ScreeningService().filter_screenings(movie_id, day)

@screening_router.post("/", status_code=status.HTTP_201_CREATED)
def create_screening(
    s: ScreeningModel,
):
    """
    Create a screening
    """
    try:
        return ScreeningService().create_screening(s.movie_id, s.room_id, s.start_time)
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e)) from e

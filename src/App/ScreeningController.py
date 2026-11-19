from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status

from datetime import date

from src.Model.ScreeningModel import ScreeningModel
from src.Service.ScreeningService import ScreeningService
from src.App.UserController import require_admin

screening_router = APIRouter(prefix="/screenings", tags=["Screenings"])

admin_screening_router = APIRouter(
    prefix="/admin/screenings",
    tags=["Screenings"],
    dependencies=[Depends(require_admin)],
)


# ---------- Public routes ----------


@screening_router.get("/rooms/{room_number}", summary="Get room Schedule", status_code=status.HTTP_200_OK)
def get_room_schedule(room_number: int):
    """
    Get the upcoming screenings of a room, sorted by start time.

    Args:

    * room_number: the number of the room (not its database id)
    """
    return ScreeningService().room_schedule(room_number)


@screening_router.get("/", summary="Get upcoming screenings", status_code=status.HTTP_200_OK)
def get_upcoming_screenings(
    movie_id: Optional[int] = None,
    day: Optional[date] = None,
):
    """
    List the upcoming screenings (at most 50, sorted by start time). Screenings already started are never shown.

    Args:

    * movie_id: only the screenings of this movie, by its id in our database (optional)
    * day: only the screenings from this day on, in local time, format YYYY-MM-DD (optional)
    """
    return ScreeningService().filter_screenings(movie_id, day)


# ---------- Admin routes ----------


@admin_screening_router.post("/", summary="Create a screening", status_code=status.HTTP_201_CREATED)
def create_screening(
    s: ScreeningModel,
):
    """
    Create a screening. The end time is computed by the server: start time + duration of the movie + 20 minutes.
    Refused (409) if the room is already booked on this time slot or if the base price is not positive.

    Args:

    * s: the movie_id, the room_id, the start_time (without time zone, it is read as Paris time)
      and the base_price of a ticket (multiplied by the coefficient of the ticket type when booking)
    """
    try:
        return ScreeningService().create_screening(s.movie_id, s.room_id, s.start_time, s.base_price)
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e)) from e


@admin_screening_router.delete("/{screening_id}", summary="Delete a screening", status_code=status.HTTP_204_NO_CONTENT)
def delete_screening(
    screening_id: int,
    confirm: bool = False,
) -> None:
    """
    Delete a screening. It is refused if tickets were already sold for it,
    so that the sales stay in the accounting.

    Args:

    * screening_id: the id of the screening
    * confirm: must be true to confirm the deletion (default false, the request is then refused)
    """
    if not confirm:
        raise HTTPException(
            status_code=409,
            detail="Confirmation required: repeat the request with confirm=True",
        )

    try:
        deleted = ScreeningService().delete_screening(screening_id)
    except ValueError as e:
        # Tickets were already sold for this screening
        raise HTTPException(status_code=409, detail=str(e)) from e

    if not deleted:
        raise HTTPException(status_code=404, detail="Screening not found")

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials

from src.Business_object.Reservation import Reservation
from src.Model.ReservationModel import ReservationModel
from src.Service.ReservationService import ReservationService

from .JWTBearer import JWTBearer
from .UserController import get_user_from_credentials

reservation_router = APIRouter(prefix="/reservations", tags=["Reservations"])

# All the routes of this controller require to be logged in (JWTBearer):
# in the Swagger, log in with POST /users/jwt, then paste the token in "Authorize"


@reservation_router.post("/", status_code=status.HTTP_201_CREATED)
def create_reservation(
    r: ReservationModel,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(JWTBearer())],
):
    """
    Book one ticket for a screening (logged-in users only)
    """
    # The customer is the logged-in user: we find him with the token,
    # so that nobody can book in the name of somebody else
    current_user = get_user_from_credentials(credentials)

    # Build the reservation (the date is set later by the service)
    reservation = Reservation(
        customer_id=current_user.id,
        screening_id=r.screening_id,
        ticket_type_id=r.ticket_type_id,
    )

    try:
        return ReservationService().create_reservation(reservation)
    except LookupError as e:
        # The screening or the ticket type does not exist
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except ValueError as e:
        # The screening has started, the ticket type is not active or the room is full
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e)) from e


@reservation_router.get("/me", status_code=status.HTTP_200_OK)
def get_my_reservations(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(JWTBearer())],
):
    """
    List the reservations of the logged-in user
    """
    current_user = get_user_from_credentials(credentials)
    return ReservationService().get_customer_reservation(current_user.id)


@reservation_router.get("/{reservation_id}", status_code=status.HTTP_200_OK)
def get_reservation_by_id(
    reservation_id: int,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(JWTBearer())],
):
    """
    Get one of my reservations by its id
    """
    current_user = get_user_from_credentials(credentials)
    reservation = ReservationService().get_by_id(reservation_id)

    # We answer "not found" if the reservation does not exist
    # or if it belongs to another customer (a customer only sees his own reservations)
    if reservation is None or reservation.customer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Reservation with id [{reservation_id}] not found",
        )
    return reservation

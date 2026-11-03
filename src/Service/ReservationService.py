from datetime import datetime, timezone
from typing import Optional

from src.Business_object.Reservation import Reservation
from src.Business_object.Screening import Screening
from src.DAO.ReservationRepo import ReservationRepo
from src.DAO.ScreeningRepo import ScreeningRepo
from src.DAO.UserRepo import UserRepo


class ReservationService:
    """Class that manages reervation"""

    def __init__(
        self,
        reservation_repo: Optional[ReservationRepo]= None,
        screening_repo: Optional[ScreeningRepo]= None,
        user_repo: Optional[UserRepo]= None
    ) -> None:
        self.reservation_repo = reservation_repo or ReservationRepo()
        self.screening_repo = screening_repo or ScreeningRepo()
        self.user_repo = user_repo or UserRepo()

    def get_by_id(self, id: int) -> Optional[Reservation]:
        return self.reservation_repo.get_by_id(id)

    def get_customer_reservation(self, customer_id: int)-> list[Reservation]:
        return self.reservation_repo.get_customer_reservations(customer_id)

    def create_reservation(self, reservation:Reservation)-> Reservation:

        # Check that screening didn't already starts
        now = datetime.now(timezone.utc)
        screening = self.screening_repo.filter_screenings(start_from=now)
        if reservation.screening_id not in screening:
            raise LookupError(f"Screening [{reservation.screening_id}] not found")

        # Check that customer exist
        customer = self.user_repo.get_by_id(reservation.customer_id)
        if not customer:
            raise LookupError(f"Customer [{reservation.customer_id}] not found")

        # Check that room is not full



        return self.reservation_repo.create_reservation(reservation)

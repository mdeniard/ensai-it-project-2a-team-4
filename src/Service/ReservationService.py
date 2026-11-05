from datetime import datetime, timezone
from decimal import ROUND_HALF_UP, Decimal
from typing import Optional

from src.Business_object.Reservation import Reservation
from src.DAO.ReservationRepo import ReservationRepo
from src.DAO.ScreeningRepo import ScreeningRepo
from src.DAO.TicketTypeRepo import TicketTypeRepo
from src.DAO.UserRepo import UserRepo


class ReservationService:
    """Class that manages reservations"""

    def __init__(
        self,
        reservation_repo: Optional[ReservationRepo] = None,
        screening_repo: Optional[ScreeningRepo] = None,
        user_repo: Optional[UserRepo] = None,
        ticket_type_repo: Optional[TicketTypeRepo] = None,
    ) -> None:
        self.reservation_repo = reservation_repo or ReservationRepo()
        self.screening_repo = screening_repo or ScreeningRepo()
        self.user_repo = user_repo or UserRepo()
        self.ticket_type_repo = ticket_type_repo or TicketTypeRepo()

    def get_by_id(self, id: int) -> Optional[Reservation]:
        return self.reservation_repo.get_by_id(id)

    def get_customer_reservation(self, customer_id: int) -> list[Reservation]:
        return self.reservation_repo.get_customer_reservations(customer_id)

    @staticmethod
    def compute_ticket_price(base_price, price_multiplier) -> Decimal:
        """Compute the price of one ticket.
        Args:
            base_price: the base price of the screening (for example 10.00)
            price_multiplier: the coefficient of the ticket type (for example 0.8 for students)
        Returns:
            The price, rounded to 2 decimals (for example 8.00)
        """
        # We use Decimal (and not float) to compute money:
        # with float, 0.1 + 0.2 gives 0.30000000000000004
        # (str() is used so that a float like 0.8 becomes exactly Decimal("0.8"))
        price = Decimal(str(base_price)) * Decimal(str(price_multiplier))

        # Round to the cent (0.005 is rounded up, like in a shop)
        return price.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def create_reservation(self, reservation: Reservation) -> Reservation:
        """Book one ticket for a screening.
        Args:
            reservation: the reservation to save (customer, screening and ticket type)
        Returns:
            The saved reservation (with its id)
        Raises:
            LookupError if the screening, the customer or the ticket type does not exist.
            ValueError if the screening has already started, the ticket type is not active
            or the room is full.
        """
        now = datetime.now(timezone.utc)

        # Check that the screening exists
        screening = self.screening_repo.get_by_id(reservation.screening_id)
        if screening is None:
            raise LookupError(f"Screening [{reservation.screening_id}] not found")

        # Check that screening didn't already start
        if screening.start_time <= now:
            raise ValueError(f"Screening [{reservation.screening_id}] has already started")

        # Check that customer exist
        customer = self.user_repo.get_by_id(reservation.customer_id)
        if not customer:
            raise LookupError(f"Customer [{reservation.customer_id}] not found")

        # Check that the ticket type exists and can still be sold
        ticket_type = self.ticket_type_repo.get_by_id(reservation.ticket_type_id)
        if ticket_type is None:
            raise LookupError(f"Ticket type [{reservation.ticket_type_id}] not found")
        if not ticket_type.active:
            raise ValueError(f"Ticket type [{ticket_type.name}] is not available")

        # Check that room is not full
        if not self.reservation_repo.check_room_capacity_reservation(reservation):
            raise ValueError("The screening is full")

        # The date of the reservation is set by the server (not by the customer)
        reservation.reserved_at = now

        # The price paid = base price of the screening x coefficient of the ticket type.
        # It is saved with the reservation, so that a later change of the prices
        # does not change the revenue of past sales
        reservation.price_paid = self.compute_ticket_price(screening.base_price, ticket_type.price_multiplier)

        return self.reservation_repo.create_reservation(reservation)

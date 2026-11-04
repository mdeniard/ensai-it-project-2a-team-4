from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from src.Business_object.Reservation import Reservation
from src.Business_object.Screening import Screening
from src.Business_object.TicketType import TicketType
from src.Business_object.User import User
from src.Service.ReservationService import ReservationService

# These tests use fake repos instead of the database (like the MockDBConnector in tests/DAO/test_UserRepo.py)

NOW = datetime.now(timezone.utc)

# ---------- Fake repos ----------


class MockScreeningRepo:
    """Fake ScreeningRepo:
    - screening 1 is tomorrow, base price 10.00
    - screening 2 was yesterday
    - screening 3 is tomorrow, base price 9.50
    """

    def get_by_id(self, object_id):
        if object_id == 1:
            return Screening(movie_id=1, room_id=1, start_time=NOW + timedelta(days=1),
                             end_time=NOW + timedelta(days=1, hours=2), base_price=10.0, id=1)
        if object_id == 2:
            return Screening(movie_id=1, room_id=1, start_time=NOW - timedelta(days=1),
                             end_time=NOW - timedelta(hours=22), base_price=10.0, id=2)
        if object_id == 3:
            return Screening(movie_id=1, room_id=1, start_time=NOW + timedelta(days=1),
                             end_time=NOW + timedelta(days=1, hours=2), base_price=9.5, id=3)
        return None


class MockUserRepo:
    """Fake UserRepo: only the customer 5 exists."""

    def get_by_id(self, user_id):
        if user_id == 5:
            return User("alice", "alice@test.fr", "hash", "Alice", "Test", id=5)
        return None


class MockTicketTypeRepo:
    """Fake TicketTypeRepo: ticket type 2 is not active, the others are."""

    def get_by_id(self, object_id):
        if object_id == 1:
            return TicketType("Normal", 1.0, True, id=1)
        if object_id == 2:
            return TicketType("Old", 0.5, False, id=2)
        if object_id == 3:
            return TicketType("ENSAI Student", 0.8, True, id=3)
        if object_id == 4:
            return TicketType("Special", 0.7, True, id=4)
        return None


class MockReservationRepo:
    """Fake ReservationRepo: we choose if the room is full, and we remember the saved reservation."""

    def __init__(self, room_is_full=False):
        self.room_is_full = room_is_full
        self.saved_reservation = None

    def check_room_capacity_reservation(self, reservation):
        # True means "there is still a free seat"
        return not self.room_is_full

    def create_reservation(self, reservation):
        # The database would give an id to the new reservation
        reservation.id = 1
        self.saved_reservation = reservation
        return reservation


def make_service(reservation_repo):
    """Create a ReservationService that only uses fake repos."""
    return ReservationService(
        reservation_repo=reservation_repo,
        screening_repo=MockScreeningRepo(),
        user_repo=MockUserRepo(),
        ticket_type_repo=MockTicketTypeRepo(),
    )


# ---------- create_reservation ----------


def test_create_reservation_ok():
    # GIVEN a screening tomorrow, an existing customer, an active ticket type and free seats
    reservation_repo = MockReservationRepo(room_is_full=False)
    reservation_service = make_service(reservation_repo)
    reservation = Reservation(customer_id=5, screening_id=1, ticket_type_id=1)

    # WHEN the customer books
    created = reservation_service.create_reservation(reservation)

    # THEN the reservation is saved and returned with its id
    assert created.id == 1
    assert reservation_repo.saved_reservation is not None
    # AND the date of the reservation was set by the service
    assert created.reserved_at is not None


def test_create_reservation_unknown_screening():
    # GIVEN
    reservation_repo = MockReservationRepo()
    reservation_service = make_service(reservation_repo)

    # WHEN the screening does not exist / THEN LookupError and nothing is saved
    with pytest.raises(LookupError):
        reservation_service.create_reservation(Reservation(customer_id=5, screening_id=99, ticket_type_id=1))
    assert reservation_repo.saved_reservation is None


def test_create_reservation_screening_already_started():
    # GIVEN
    reservation_repo = MockReservationRepo()
    reservation_service = make_service(reservation_repo)

    # WHEN the screening was yesterday / THEN ValueError and nothing is saved
    with pytest.raises(ValueError):
        reservation_service.create_reservation(Reservation(customer_id=5, screening_id=2, ticket_type_id=1))
    assert reservation_repo.saved_reservation is None


def test_create_reservation_unknown_customer():
    # GIVEN
    reservation_repo = MockReservationRepo()
    reservation_service = make_service(reservation_repo)

    # WHEN the customer does not exist / THEN LookupError and nothing is saved
    with pytest.raises(LookupError):
        reservation_service.create_reservation(Reservation(customer_id=99, screening_id=1, ticket_type_id=1))
    assert reservation_repo.saved_reservation is None


def test_create_reservation_unknown_ticket_type():
    # GIVEN
    reservation_repo = MockReservationRepo()
    reservation_service = make_service(reservation_repo)

    # WHEN the ticket type does not exist / THEN LookupError and nothing is saved
    with pytest.raises(LookupError):
        reservation_service.create_reservation(Reservation(customer_id=5, screening_id=1, ticket_type_id=99))
    assert reservation_repo.saved_reservation is None


def test_create_reservation_inactive_ticket_type():
    # GIVEN
    reservation_repo = MockReservationRepo()
    reservation_service = make_service(reservation_repo)

    # WHEN the ticket type is not active anymore / THEN ValueError and nothing is saved
    with pytest.raises(ValueError):
        reservation_service.create_reservation(Reservation(customer_id=5, screening_id=1, ticket_type_id=2))
    assert reservation_repo.saved_reservation is None


def test_create_reservation_room_full():
    # GIVEN the room is full
    reservation_repo = MockReservationRepo(room_is_full=True)
    reservation_service = make_service(reservation_repo)

    # WHEN the customer books / THEN ValueError and nothing is saved
    with pytest.raises(ValueError):
        reservation_service.create_reservation(Reservation(customer_id=5, screening_id=1, ticket_type_id=1))
    assert reservation_repo.saved_reservation is None


# ---------- compute_ticket_price ----------


def test_compute_ticket_price_normal():
    # Normal ticket: 10.00 x 1.0 = 10.00
    assert ReservationService.compute_ticket_price(10.0, 1.0) == Decimal("10.00")


def test_compute_ticket_price_reduced():
    # Reduced ticket: 10.00 x 0.8 = 8.00 and 10.00 x 0.6 = 6.00
    assert ReservationService.compute_ticket_price(10.0, 0.8) == Decimal("8.00")
    assert ReservationService.compute_ticket_price(10.0, 0.6) == Decimal("6.00")


def test_compute_ticket_price_rounded_to_the_cent():
    # 9.50 x 0.7 = 6.65 (and not 6.6499999... like with float)
    assert ReservationService.compute_ticket_price(9.5, 0.7) == Decimal("6.65")
    # 9.99 x 0.5 = 4.995, rounded up to 5.00
    assert ReservationService.compute_ticket_price(9.99, 0.5) == Decimal("5.00")


def test_compute_ticket_price_with_decimal_values():
    # PostgreSQL returns NUMERIC columns as Decimal: it must work too
    assert ReservationService.compute_ticket_price(Decimal("10.00"), Decimal("0.80")) == Decimal("8.00")


# ---------- price saved with the reservation ----------


def test_create_reservation_saves_normal_price():
    # GIVEN a screening at 10.00 and the Normal ticket type (x1.0)
    reservation_repo = MockReservationRepo()
    reservation_service = make_service(reservation_repo)

    # WHEN the customer books
    created = reservation_service.create_reservation(Reservation(customer_id=5, screening_id=1, ticket_type_id=1))

    # THEN he pays 10.00
    assert created.price_paid == Decimal("10.00")


def test_create_reservation_saves_student_price():
    # GIVEN a screening at 10.00 and the ENSAI Student ticket type (x0.8)
    reservation_repo = MockReservationRepo()
    reservation_service = make_service(reservation_repo)

    # WHEN the customer books
    created = reservation_service.create_reservation(Reservation(customer_id=5, screening_id=1, ticket_type_id=3))

    # THEN he pays 8.00
    assert created.price_paid == Decimal("8.00")


def test_create_reservation_uses_base_price_of_the_screening():
    # GIVEN a screening at 9.50 and a ticket type at x0.7
    reservation_repo = MockReservationRepo()
    reservation_service = make_service(reservation_repo)

    # WHEN the customer books
    created = reservation_service.create_reservation(Reservation(customer_id=5, screening_id=3, ticket_type_id=4))

    # THEN he pays 9.50 x 0.7 = 6.65
    assert created.price_paid == Decimal("6.65")

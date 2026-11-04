from datetime import datetime, timedelta, timezone

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
    """Fake ScreeningRepo: screening 1 is tomorrow, screening 2 was yesterday."""

    def get_by_id(self, object_id):
        if object_id == 1:
            return Screening(movie_id=1, room_id=1, start_time=NOW + timedelta(days=1),
                             end_time=NOW + timedelta(days=1, hours=2), id=1)
        if object_id == 2:
            return Screening(movie_id=1, room_id=1, start_time=NOW - timedelta(days=1),
                             end_time=NOW - timedelta(hours=22), id=2)
        return None


class MockUserRepo:
    """Fake UserRepo: only the customer 5 exists."""

    def get_by_id(self, user_id):
        if user_id == 5:
            return User("alice", "alice@test.fr", "hash", "Alice", "Test", id=5)
        return None


class MockTicketTypeRepo:
    """Fake TicketTypeRepo: ticket type 1 is active, ticket type 2 is not."""

    def get_by_id(self, object_id):
        if object_id == 1:
            return TicketType("Normal", 1.0, True, id=1)
        if object_id == 2:
            return TicketType("Old", 0.5, False, id=2)
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

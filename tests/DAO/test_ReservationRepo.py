from datetime import datetime, timezone
from decimal import Decimal

from src.Business_object.Reservation import Reservation
from src.DAO.ReservationRepo import ReservationRepo

# These tests never use the real database: we give ReservationRepo a fake DBConnector.
# They only check the Python part of the repo (a row is turned into a Reservation, the right values are sent,
# the free seats are compared to the capacity). They cannot tell if the SQL is correct: that needs a real database.


class MockDBConnector:
    """Fake DBConnector.
    - it returns the answer we prepared (as if PostgreSQL had answered)
    - it remembers the data it received, so that we can check them in the tests
    """

    def __init__(self, answer):
        self.answer = answer
        self.last_data = None

    def sql_query(self, query, data=None, return_type="one"):
        # Remember what the repo sent
        self.last_data = data
        # Return the prepared answer
        return self.answer


RESERVED_AT = datetime(2026, 11, 4, 10, 0, tzinfo=timezone.utc)

# A row of the reservations table, as PostgreSQL would return it
RESERVATION_ROW = {
    "id": 1,
    "customer_id": 5,
    "screening_id": 3,
    "ticket_type_id": 2,
    "reserved_at": RESERVED_AT,
    "price_paid": Decimal("8.00"),
}


def make_reservation():
    """Create the Reservation object used in the tests (not saved yet, so no id)."""
    return Reservation(
        customer_id=5, screening_id=3, ticket_type_id=2, reserved_at=RESERVED_AT, price_paid=Decimal("8.00")
    )


# ---------- get_by_id ----------


def test_get_by_id_found():
    # GIVEN the database contains the reservation
    reservation_repo = ReservationRepo(MockDBConnector(RESERVATION_ROW))

    # WHEN we search it
    reservation = reservation_repo.get_by_id(1)

    # THEN we get a Reservation object with the right values (the price stays a Decimal)
    assert reservation is not None
    assert reservation.customer_id == 5
    assert reservation.screening_id == 3
    assert reservation.price_paid == Decimal("8.00")


# ---------- get_customer_reservations ----------


def test_get_customer_reservations():
    # GIVEN the customer has two reservations
    second_row = dict(RESERVATION_ROW)
    second_row["id"] = 2
    db_connector = MockDBConnector([RESERVATION_ROW, second_row])
    reservation_repo = ReservationRepo(db_connector)

    # WHEN we list his reservations
    reservations = reservation_repo.get_customer_reservations(5)

    # THEN we get the two reservations
    assert len(reservations) == 2
    # AND the repo searched with the id of the customer
    assert db_connector.last_data == [5]


# ---------- count_screening_reservations (used before deleting a screening) ----------


def test_count_screening_reservations():
    # GIVEN 3 tickets were sold for the screening
    db_connector = MockDBConnector({"tickets_sold": 3})
    reservation_repo = ReservationRepo(db_connector)

    # WHEN we count them / THEN we get 3
    assert reservation_repo.count_screening_reservations(3) == 3
    # AND the repo counted the reservations of the right screening
    assert db_connector.last_data == [3]


# ---------- create_reservation ----------


def test_create_reservation():
    # GIVEN a database that returns the saved row
    db_connector = MockDBConnector(RESERVATION_ROW)
    reservation_repo = ReservationRepo(db_connector)

    # WHEN we save a new reservation
    created = reservation_repo.create_reservation(make_reservation())

    # THEN we get the reservation with the id given by the database
    assert created.id == 1
    # AND the id is not sent (PostgreSQL creates it), but the price paid is
    assert "id" not in db_connector.last_data
    assert db_connector.last_data["price_paid"] == Decimal("8.00")


# ---------- check_room_capacity_reservation ----------


def test_check_room_capacity_free_seats():
    # GIVEN a room of 100 seats where 40 tickets were sold
    reservation_repo = ReservationRepo(MockDBConnector({"capacity": 100, "tickets_sold": 40}))

    # WHEN we check / THEN there is still room
    assert reservation_repo.check_room_capacity_reservation(make_reservation()) is True


def test_check_room_capacity_full():
    # GIVEN a room of 100 seats where 100 tickets were sold
    reservation_repo = ReservationRepo(MockDBConnector({"capacity": 100, "tickets_sold": 100}))

    # WHEN we check / THEN the room is full
    assert reservation_repo.check_room_capacity_reservation(make_reservation()) is False


def test_check_room_capacity_unknown_screening():
    # GIVEN the screening does not exist (the query returns no row)
    reservation_repo = ReservationRepo(MockDBConnector(None))

    # WHEN we check / THEN we answer False (no seat can be booked)
    assert reservation_repo.check_room_capacity_reservation(make_reservation()) is False

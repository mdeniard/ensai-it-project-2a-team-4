from datetime import datetime
from typing import Optional

from src.Business_object.Reservation import Reservation

from .DBConnector import DBConnector


class ReservationRepo:
    db_connector: DBConnector

    def __init__(self, db_connector: Optional[DBConnector] = None) -> None:
        """Create the repository.
        Args:
            db_connector (DBConnector, optional): The connection to the database.
                If none is given, a new DBConnector is created.
        """
        self.db_connector = db_connector or DBConnector()

    def get_by_id(self, id) -> Optional[Reservation]:
        """Retrieve a reservation by its database identifier.
        Args:
            id (int): The unique database id of the reservation.
        Returns:
            The Reservation object, or None if no reservation has this id.
        """
        raw_reservation = self.db_connector.sql_query("SELECT * FROM reservations WHERE id = %s;", [id], "one")
        if raw_reservation is None:
            return None
        return Reservation(**raw_reservation)

    def get_customer_reservations(self, customer_id) -> list[Reservation]:
        """Retrieve all the reservations of a customer.
        Args:
            customer_id (int): The database id of the customer.
        Returns:
            list[Reservation] of the customer, or an empty list if he has none.
        """
        raw_reservation = self.db_connector.sql_query(
            "SELECT * FROM reservations WHERE customer_id = %s;", [customer_id], return_type="all"
        )
        return [Reservation(**raw) for raw in raw_reservation or []]

    def count_screening_reservations(self, screening_id: int) -> int:
        """Count the tickets sold for a screening (one reservation = one ticket).
        Args:
            screening_id (int): The database id of the screening.
        Returns:
            The number of reservations of the screening (0 if it has none or does not exist).
        """
        raw = self.db_connector.sql_query(
            "SELECT COUNT(*) AS tickets_sold FROM reservations WHERE screening_id = %s;",
            [screening_id],
            "one",
        )
        # COUNT(*) always returns one row, but we stay careful if nothing comes back
        if raw is None:
            return 0
        # pyrefly: ignore
        return raw["tickets_sold"]

    def get_accounting_by_movie(
        self, movie_id: int, start_from: Optional[datetime] = None, end_at: Optional[datetime] = None
    ):
        """Compute the number of tickets sold and the revenue of each screening of a movie.
        Only the reservations made between the two dates are counted (the screenings
        without any reservation in this period are still returned, with 0 ticket and 0 revenue).
        Args:
            movie_id (int): The database id of the movie.
            start_from (datetime, optional): Only the reservations made from this date on.
            end_at (datetime, optional): Only the reservations made until this date.
        Returns:
            list[dict] with one row per screening, sorted by start time. Each row contains
            movie_id, screening_id, start_time, tickets_sold and revenue.
        """
        query = """
            SELECT
                m.id AS movie_id,
                s.id AS screening_id,
                s.start_time,
                COUNT(r.id) AS tickets_sold,
                COALESCE(SUM(r.price_paid), 0) AS revenue
            FROM screenings s
            JOIN movies m ON m.id = s.movie_id
            LEFT JOIN reservations r
                ON r.screening_id = s.id
        """

        params: dict = {"movie_id": movie_id}

        if start_from is not None:
            query += " AND r.reserved_at >= %(start_from)s"
            params["start_from"] = start_from

        if end_at is not None:
            query += " AND r.reserved_at <= %(end_at)s"
            params["end_at"] = end_at

        query += """
            WHERE m.id = %(movie_id)s
            GROUP BY m.id, s.id, s.start_time
            ORDER BY s.start_time;
        """

        return self.db_connector.sql_query(query, params, "all")

    def create_reservation(self, reservation: Reservation) -> Reservation:
        """Save a new reservation (the id is given by the database).
        Args:
            reservation (Reservation): The reservation to save (customer, screening, ticket type,
                date of the reservation and price paid).
        Returns:
            The saved Reservation, with its id.
        """
        raw = self.db_connector.sql_query(
            """
            INSERT INTO reservations (customer_id, screening_id, ticket_type_id, reserved_at, price_paid)
            VALUES (%(customer_id)s, %(screening_id)s, %(ticket_type_id)s, %(reserved_at)s, %(price_paid)s)
            RETURNING *;
            """,
            {
                "customer_id": reservation.customer_id,
                "screening_id": reservation.screening_id,
                "ticket_type_id": reservation.ticket_type_id,
                "reserved_at": reservation.reserved_at,
                "price_paid": reservation.price_paid,
            },
            "one",
        )
        return Reservation(**raw)

    def check_room_capacity_reservation(self, reservation: Reservation) -> bool:
        """Check if there is still at least one free seat for the screening of the reservation.
        (one reservation = one ticket = one seat)
        Args:
            reservation (Reservation): The reservation we want to make (only its screening is used).
        Returns:
            True if the room is not full, False if it is full (or if the screening does not exist).
        """
        # We start from the screening (and not from the reservations), so that a screening
        # with no reservation yet is found too: the LEFT JOIN then gives 0 tickets sold
        raw = self.db_connector.sql_query(
            """
            SELECT ro.capacity, COUNT(re.id) AS tickets_sold
            FROM screenings s
            JOIN rooms ro ON ro.id = s.room_id
            LEFT JOIN reservations re ON re.screening_id = s.id
            WHERE s.id = %(screening_id)s
            GROUP BY ro.capacity;
            """,
            {"screening_id": reservation.screening_id},
            "one",
        )

        # No row: the screening does not exist
        if raw is None:
            return False

        # There is a free seat if fewer tickets were sold than the capacity of the room
        # pyrefly: ignore
        return raw["tickets_sold"] < raw["capacity"]

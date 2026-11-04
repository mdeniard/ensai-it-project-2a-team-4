from typing import Optional

from src.Business_object.Reservation import Reservation

from .DBConnector import DBConnector


class ReservationRepo:
    db_connector: DBConnector

    def __init__(self, db_connector: Optional[DBConnector] = None) -> None:
        self.db_connector = db_connector or DBConnector()

    def get_by_id(self, id)-> Optional[Reservation]:
        raw_reservation = self.db_connector.sql_query(
            "SELECT * FROM reservations WHERE id = %s;",
            [id],
            "one"
        )
        if raw_reservation is None:
            return None
        return Reservation(**raw_reservation)

    def get_customer_reservations(self, customer_id)->list[Reservation]:
        raw_reservation = self.db_connector.sql_query(
            "SELECT * FROM reservations WHERE customer_id = %s;",
            [customer_id],
            return_type="all"
        )
        return [Reservation(**raw) for raw in raw_reservation or []]

    def create_reservation(self, reservation: Reservation)-> Reservation:
        raw = self.db_connector.sql_query(
            """
            INSERT INTO reservations (customer_id, screening_id, ticket_type_id, reserved_at)
            VALUES (%(customer_id)s, %(screening_id)s, %(ticket_type_id)s, %(reserved_at)s)
            RETURNING *;
            """,
            {
                "customer_id": reservation.customer_id,
                "screening_id": reservation.screening_id,
                "ticket_type_id": reservation.ticket_type_id,
                "reserved_at": reservation.reserved_at
            },
            "one",
        )
        return Reservation(**raw)


    def check_room_capacity_reservation(self, reservation: Reservation) -> bool:
        """Check if there is still at least one free seat for the screening of the reservation.
        (one reservation = one ticket = one seat)
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

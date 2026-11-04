from datetime import datetime
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


    def check_room_capacity_reservation(self, reservation: Reservation)-> bool:
        raw = self.db_connector.sql_query(
             """
            SELECT COUNT(re.id)
            FROM reservation re
            LEFT JOIN screenings s on s.id = re.screening_id
            JOIN rooms ro ON ro.id = s.room_id
            WHERE s.id = %(screening_id)s
            GROUP BY s.id, ro.capacity
            HAVING COUNT(re.id) < ro.capacity;
            """,
            {"screening_id": reservation.screening_id},
            "all",
        )
        return raw is not None and len(raw) > 0

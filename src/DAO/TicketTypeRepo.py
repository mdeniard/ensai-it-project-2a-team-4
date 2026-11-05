from typing import Optional

from src.Business_object.TicketType import TicketType

from .DBConnector import DBConnector


class TicketTypeRepo:
    db_connector: DBConnector

    def __init__(self, db_connector: Optional[DBConnector] = None) -> None:
        self.db_connector = db_connector or DBConnector()

    def get_by_id(self, id: int) -> Optional[TicketType]:
        raw_ticket_type = self.db_connector.sql_query(
            "SELECT * FROM ticket_types WHERE id = %s;",
            [id],
            "one"
        )
        if raw_ticket_type is None:
            return None
        return TicketType(**raw_ticket_type)

    def get_all(self)-> list[TicketType]:
        raw_ticket_type = self.db_connector.sql_query(
            "SELECT * FROM ticket_types ORDER BY id;",
            return_type="all"
        )
        return [TicketType(**raw) for raw in raw_ticket_type or []]

    def insert_ticket_type(self, ticket_type: TicketType) -> TicketType:
        raw = self.db_connector.sql_query(
            """
            INSERT INTO ticket_types (id, name, price_multiplier, active)
            VALUES %(name)s, %(price_multiplier)s, %(active)s)
            RETURNING *;
            """,
            {
                "name": ticket_type.name,
                "price_multiplier": ticket_type.price_multiplier,
                "active": ticket_type.active,
            },
            "one",
        )
        return TicketType(**raw)

    def update_ticket_type(self, ticket_type: TicketType) -> Optional[TicketType]:
        raw_updated_ticket_type = self.db_connector.sql_query(
            """
            UPDATE ticket_types
            SET name = %(name)s,
                price_multiplier = %(price_multiplier)s,
                active = %(active)s
            WHERE id = %(id)s
            RETURNING *;
            """,
            {
                "id": ticket_type.id,
                "name": ticket_type.name,
                "price_multiplier": ticket_type.price_multiplier,
                "active": ticket_type.active,
            },
            "one",
        )

        if raw_updated_ticket_type is None:
            return None

        return TicketType(**raw_updated_ticket_type)

    def delete_ticket_type(self, ticket_type_id)-> bool:
        deleted_ticket_type = self.db_connector.sql_query(
            """
            DELETE FROM ticket_types
            WHERE id = %s
            RETURNING id;
            """,
            [ticket_type_id],
            "one",
        )
        return deleted_ticket_type is not None


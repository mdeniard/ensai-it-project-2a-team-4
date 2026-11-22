from typing import Optional

from src.Business_object.TicketType import TicketType

from .DBConnector import DBConnector


class TicketTypeRepo:
    """Repository that manages the ticket types in the database (table ticket_types)."""

    db_connector: DBConnector

    def __init__(self, db_connector: Optional[DBConnector] = None) -> None:
        """Create the repository.
        Args:
            db_connector (DBConnector, optional): The connection to the database.
                If none is given, a new DBConnector is created.
        """
        self.db_connector = db_connector or DBConnector()

    def get_by_id(self, ticket_type_id: int) -> Optional[TicketType]:
        """Retrieve a ticket type by its database identifier.
        Args:
            ticket_type_id (int): The unique database id of the ticket type.
        Returns:
            The TicketType object, or None if no ticket type has this id.
        """
        raw_ticket_type = self.db_connector.sql_query(
            "SELECT * FROM ticket_types WHERE id = %s;", [ticket_type_id], "one"
        )
        if raw_ticket_type is None:
            return None
        return TicketType(**raw_ticket_type)

    def get_all(self) -> list[TicketType]:
        """Retrieve all the ticket types, sorted by id.
        Returns:
            list[TicketType] of all the ticket types, or an empty list if there is none.
        """
        raw_ticket_type = self.db_connector.sql_query("SELECT * FROM ticket_types ORDER BY id;", return_type="all")
        return [TicketType(**raw) for raw in raw_ticket_type or []]

    def create_ticket_type(self, ticket_type: TicketType) -> TicketType:
        """Create a new ticket type (the id is given by the database).
        Args:
            ticket_type (TicketType): The ticket type to create.
        Returns:
            The saved TicketType, with its id.
        """
        # The id is not sent: PostgreSQL creates it (SERIAL) and RETURNING * gives it back
        raw = self.db_connector.sql_query(
            """
            INSERT INTO ticket_types (name, price_multiplier, active)
            VALUES (%(name)s, %(price_multiplier)s, %(active)s)
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
        """Update all the fields of an existing ticket type.
        Args:
            ticket_type (TicketType): The ticket type with its new data. Its id identifies the row to update,
                so it must be set.
        Returns:
            The updated TicketType.
        """
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

    def delete_ticket_type(self, ticket_type_id) -> bool:
        """Delete a ticket type. Its reservations and reviews are deleted too (ON DELETE CASCADE).
        Args:
            ticket_type_id (int): The id of the ticket type to delete.
        Returns:
            True if a ticket type was deleted, False if no ticket type has this id.
        """
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

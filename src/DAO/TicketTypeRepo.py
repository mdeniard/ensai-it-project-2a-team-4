from typing import Optional

from src.Business_object.TicketType import TicketType

from .DBConnector import DBConnector


class TicketTypeRepo:
    """Repository that manages the tickets in the database (table ticket_types)."""

    db_connector: DBConnector

    def __init__(self, db_connector: Optional[DBConnector] = None) -> None:
        """Create the repository.
        Args:
            db_connector (DBConnector, optional): The connection to the database.
                If none is given, a new DBConnector is created.
        """
        self.db_connector = db_connector or DBConnector()

    def get_by_id(self, ticket_id: int) -> Optional[TicketType]:
        """Retrieve a ticket by its database identifier.
        Args:
            ticket_id (int): The unique database id of the ticket.
        Returns:
            The TicketType object, or None if no ticket has this id.
        """
        raw_ticket_type = self.db_connector.sql_query("SELECT * FROM ticket_types WHERE id = %s;", [ticket_id], "one")
        if raw_ticket_type is None:
            return None
        return TicketType(**raw_ticket_type)

    def get_all(self) -> list[TicketType]:
        """Retrieve the tickets, sorted by id, page by page.
        Returns:
            list[TicketType] of the requested page, or an empty list if there is none.
        """
        raw_ticket_type = self.db_connector.sql_query("SELECT * FROM ticket_types ORDER BY id;", return_type="all")
        return [TicketType(**raw) for raw in raw_ticket_type or []]

    def insert_ticket_type(self, ticket_type: TicketType) -> TicketType:
        """Insert a new type of ticket (the id is given by the database).
        Args:
            ticket_type (TicketType): The ticket to create.
        Returns:
            The saved TicketType, with its id.
        """
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
        """Update all the fields of an existing ticket.
        Args:
            ticket_type (TicketType): The ticket with its new data. Its id identifies the row to update,
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
        """Delete a type of ticket. Its reservations and reviews are deleted too (ON DELETE CASCADE).
        Args:
            ticket_type_id (int): The id of the ticket to delete.
        Returns:
            True if a ticket was deleted, False if no ticket has this id.
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

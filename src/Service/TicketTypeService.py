from typing import Optional

from src.Business_object.TicketType import TicketType
from src.DAO.TicketTypeRepo import TicketTypeRepo


class TicketTypeService:
    """Service that manages ticket types (Normal, Child, Student...)."""

    def __init__(
        self,
        ticket_type_repo: Optional[TicketTypeRepo] = None,
    ):
        """Create the service.
        Args:
            ticket_type_repo (TicketTypeRepo, optional): Access to the ticket types in the database.
                If none is given, a new TicketTypeRepo is created.
        """
        # Access to our own database (table ticket_types)
        self.ticket_type_repo: TicketTypeRepo = ticket_type_repo or TicketTypeRepo()

    def get_by_id(self, ticket_type_id) -> Optional[TicketType]:
        """Find a ticket type by its id.
        Args:
            ticket_type_id (int): The id of the wanted ticket type.
        Returns:
            The TicketType, or None if no ticket type has this id.
        """
        return self.ticket_type_repo.get_by_id(ticket_type_id)

    def get_all_ticket_types(self) -> list[TicketType]:
        """List all the ticket types, including the inactive ones.
        Returns:
            list[TicketType] of all the ticket types, sorted by id, or an empty list if there is none.
        """
        return self.ticket_type_repo.get_all()

    def get_active_ticket_types(self) -> list[TicketType]:
        """Get the ticket types that a customer can choose when booking
        Returns:
            list[TicketType] containing only the active ticket types.
        """
        active_ticket_types = []
        for ticket_type in self.ticket_type_repo.get_all():
            # An inactive ticket type can no longer be sold, so we do not show it
            if ticket_type.active:
                active_ticket_types.append(ticket_type)  # noqa: PERF401 (a simple loop is easier to read here)
        return active_ticket_types

    def create_ticket_type(self, ticket_type: TicketType) -> TicketType:
        """Create a ticket type.
        Args:
            ticket_type (TicketType): The ticket type to save (name, price multiplier and active).
        Returns:
            The saved TicketType, with its id.
        """
        return self.ticket_type_repo.insert_ticket_type(ticket_type)

    def update_ticket_type(self, ticket_type: TicketType) -> Optional[TicketType]:
        """Update a ticket type.
        Args:
            ticket_type (TicketType): The ticket type with its new data. Its id identifies the one to update.
        Returns:
            The updated TicketType, or None if no ticket type has this id.
        """
        return self.ticket_type_repo.update_ticket_type(ticket_type)

    def delete_ticket_type(self, ticket_type_id: int) -> bool:
        """Delete a ticket type. The reservations made with it are deleted too (ON DELETE CASCADE).
        To stop selling a ticket type without losing the sales, set it as not active instead.
        Args:
            ticket_type_id (int): The id of the ticket type to delete.
        Returns:
            True if a ticket type was deleted, False if no ticket type has this id.
        """
        return self.ticket_type_repo.delete_ticket_type(ticket_type_id)

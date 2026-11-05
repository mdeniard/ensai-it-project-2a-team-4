from typing import Optional

from src.Business_object.TicketType import TicketType
from src.DAO.TicketTypeRepo import TicketTypeRepo


class TicketTypeService:
    """Service that manages ticket types."""

    def __init__(
        self,
        ticket_type_repo: Optional[TicketTypeRepo] = None,
    ):
        # Access to our own database (table ticket_types)
        self.ticket_type_repo: TicketTypeRepo = ticket_type_repo or TicketTypeRepo()

    def get_by_id(self, ticket_type_id)-> Optional[TicketType]:
        """Get the ticket type with the id
        Args:
            ticket_type_id : id of the wanted ticket type
        """
        return self.ticket_type_repo.get_by_id(ticket_type_id)

    def get_all_ticket_types(self)-> list[TicketType]:
        """Get all ticket types
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

    def create_ticket_type(self, ticket_type: TicketType) ->TicketType:
        """Create a ticket type
        Args:
            ticket_type : data concerning the ticket type
        """
        return self.ticket_type_repo.insert_ticket_type(ticket_type)

    def update_ticket_type(self, ticket_type: TicketType)-> Optional[TicketType]:
        """Update a ticket type
        Args:
            ticket_type : new data concerning the ticket type
        """
        return self.ticket_type_repo.update_ticket_type(ticket_type)

    def delete_ticket_type(self, ticket_type_id: int)-> bool:
        """Delete a ticket type
        Args:
            ticket_type_id : the id of the ticket type we wish to delete
        """
        return self.ticket_type_repo.delete_ticket_type(ticket_type_id)

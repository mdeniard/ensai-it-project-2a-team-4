from typing import Optional

from src.Business_object.TicketType import TicketType
from src.DAO.ReservationRepo import ReservationRepo
from src.DAO.TicketTypeRepo import TicketTypeRepo


class TicketTypeService:
    """Service that manages ticket types (Normal, Child, Student...)."""

    def __init__(
        self,
        ticket_type_repo: Optional[TicketTypeRepo] = None,
        reservation_repo: Optional[ReservationRepo] = None,
    ):
        """Create the service.
        Args:
            ticket_type_repo (TicketTypeRepo, optional): Access to the ticket types in the database.
                If none is given, a new TicketTypeRepo is created.
            reservation_repo (ReservationRepo, optional): Access to the reservations, only used before
                deleting a ticket type. If none is given, a new ReservationRepo is created when it is needed.
        """
        # Access to our own database (table ticket_types)
        self.ticket_type_repo: TicketTypeRepo = ticket_type_repo or TicketTypeRepo()
        # Access to the reservations (to protect the sales before a deletion)
        self.reservation_repo = reservation_repo

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

    def check_ticket_type(self, ticket_type: TicketType) -> None:
        """Check the data of a ticket type before saving it.
        The ticket type is refused (ValueError) if its name is empty, if its price multiplier
        is not greater than 0, or if its name is already used by another ticket type.
        Args:
            ticket_type (TicketType): The ticket type to check. Its id is None for a new ticket type.
        """
        # The name is shown to the customers: it must not be empty
        ticket_type.name = ticket_type.name.strip()
        if ticket_type.name == "":
            raise ValueError("The name of the ticket type must not be empty")

        # price paid = base price of the screening x price_multiplier, so it must be positive
        if ticket_type.price_multiplier <= 0:
            raise ValueError("The price multiplier must be greater than 0")

        # Two ticket types cannot have the same name
        # (when we update a ticket type, it can keep its own name)
        for existing in self.ticket_type_repo.get_all():
            if existing.name.lower() == ticket_type.name.lower() and existing.id != ticket_type.id:
                raise ValueError(f"The ticket type [{ticket_type.name}] already exists")

    def create_ticket_type(self, ticket_type: TicketType) -> TicketType:
        """Create a ticket type. It is refused if its name is empty or already used,
        or if its price multiplier is not greater than 0.
        Args:
            ticket_type (TicketType): The ticket type to save (name, price multiplier and active).
        Returns:
            The saved TicketType, with its id.
        """
        self.check_ticket_type(ticket_type)
        return self.ticket_type_repo.create_ticket_type(ticket_type)

    def update_ticket_type(self, ticket_type: TicketType) -> Optional[TicketType]:
        """Update a ticket type (its name, its price multiplier, or active to stop selling it).
        It is refused if the new name is empty or used by another ticket type,
        or if the new price multiplier is not greater than 0.
        The price of the tickets already sold never changes: it is stored with each reservation.
        Args:
            ticket_type (TicketType): The ticket type with its new data. Its id identifies the one to update.
        Returns:
            The updated TicketType, or None if no ticket type has this id.
        """
        self.check_ticket_type(ticket_type)
        return self.ticket_type_repo.update_ticket_type(ticket_type)

    def delete_ticket_type(self, ticket_type_id: int) -> bool:
        """Delete a ticket type that was never sold.
        A ticket type already sold cannot be deleted: its reservations would be deleted too
        (ON DELETE CASCADE), so the sales would disappear from the accounting.
        To stop selling it, set it as not active instead.
        Args:
            ticket_type_id (int): The id of the ticket type to delete.
        Returns:
            True if a ticket type was deleted, False if no ticket type has this id.
        Raises:
            ValueError if tickets were already sold with this ticket type.
        """
        # Refuse the deletion if at least one ticket was sold with this ticket type
        reservation_repo = self.reservation_repo or ReservationRepo()
        tickets_sold = reservation_repo.count_ticket_type_reservations(ticket_type_id)
        if tickets_sold > 0:
            raise ValueError(
                f"{tickets_sold} ticket(s) already sold with this ticket type, it cannot be deleted "
                "(set it as not active instead)"
            )

        return self.ticket_type_repo.delete_ticket_type(ticket_type_id)

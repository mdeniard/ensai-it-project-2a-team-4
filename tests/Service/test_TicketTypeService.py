from src.Business_object.TicketType import TicketType
from src.Service.TicketTypeService import TicketTypeService

# These tests use a fake repo instead of the database.
# The other methods of TicketTypeService only pass the call to the repo (no business rule), so they are not tested here.


class MockTicketTypeRepo:
    """Fake TicketTypeRepo: we choose the ticket types it returns."""

    def __init__(self, ticket_types):
        self.ticket_types = ticket_types

    def get_all(self):
        return self.ticket_types


# ---------- get_active_ticket_types ----------


def test_get_active_ticket_types_hides_inactive():
    # GIVEN an active ticket type and an inactive one
    ticket_type_repo = MockTicketTypeRepo(
        [
            TicketType("Student", 0.7, True, id=1),
            TicketType("Old", 0.5, False, id=2),
        ]
    )
    ticket_type_service = TicketTypeService(ticket_type_repo)

    # WHEN we list the ticket types available for booking
    ticket_types = ticket_type_service.get_active_ticket_types()

    # THEN we only get the active one (an inactive ticket type can no longer be sold)
    assert len(ticket_types) == 1
    assert ticket_types[0].name == "Student"


def test_get_active_ticket_types_no_ticket_type():
    # GIVEN there is no ticket type
    ticket_type_service = TicketTypeService(MockTicketTypeRepo([]))

    # WHEN we list the ticket types available for booking / THEN we get an empty list
    assert ticket_type_service.get_active_ticket_types() == []

from src.Business_object.TicketType import TicketType
from src.Service.TicketTypeService import TicketTypeService

# These tests use a fake repo instead of the database.


class MockTicketTypeRepo:
    """Fake TicketTypeRepo: we choose the ticket types it returns and we remember what was saved."""

    def __init__(self, ticket_types=None):
        self.ticket_types = ticket_types or []
        self.created_ticket_type = None
        self.updated_ticket_type = None
        self.deleted_ticket_type_id = None

    def get_by_id(self, ticket_type_id):
        for ticket_type in self.ticket_types:
            if ticket_type.id == ticket_type_id:
                return ticket_type
        return None

    def get_all(self):
        return self.ticket_types

    def insert_ticket_type(self, ticket_type):
        ticket_type.id = len(self.ticket_types) + 1
        self.ticket_types.append(ticket_type)
        self.created_ticket_type = ticket_type
        return ticket_type

    def update_ticket_type(self, ticket_type):
        self.updated_ticket_type = ticket_type
        return ticket_type

    def delete_ticket_type(self, ticket_type_id):
        for i, ticket_type in enumerate(self.ticket_types):
            if ticket_type.id == ticket_type_id:
                self.ticket_types.pop(i)
                self.deleted_ticket_type_id = ticket_type_id
                return True
        return False


# ---------- get_by_id ----------


def test_get_by_id_returns_ticket_type_when_found():
    # GIVEN ticket type 1 exists
    ticket_type_repo = MockTicketTypeRepo([TicketType("Student", 0.7, True, id=1)])
    ticket_type_service = TicketTypeService(ticket_type_repo)

    # WHEN we look it up by id
    result = ticket_type_service.get_by_id(1)

    # THEN we get it
    assert result.name == "Student"
    assert result.id == 1


def test_get_by_id_returns_none_when_not_found():
    # GIVEN ticket type 99 does not exist
    ticket_type_repo = MockTicketTypeRepo([TicketType("Student", 0.7, True, id=1)])
    ticket_type_service = TicketTypeService(ticket_type_repo)

    # WHEN we look it up by id / THEN we get None
    assert ticket_type_service.get_by_id(99) is None


# ---------- get_all_ticket_types ----------


def test_get_all_ticket_types_returns_all():
    # GIVEN the repo has 2 ticket types (one active, one inactive)
    ticket_type_repo = MockTicketTypeRepo(
        [
            TicketType("Student", 0.7, True, id=1),
            TicketType("Old", 0.5, False, id=2),
        ]
    )
    ticket_type_service = TicketTypeService(ticket_type_repo)

    # WHEN we list all ticket types
    result = ticket_type_service.get_all_ticket_types()

    # THEN we get both, including the inactive one
    assert len(result) == 2


def test_get_all_ticket_types_returns_empty_list():
    # GIVEN there is no ticket type
    ticket_type_service = TicketTypeService(MockTicketTypeRepo([]))

    # WHEN we list all ticket types / THEN we get an empty list
    assert ticket_type_service.get_all_ticket_types() == []


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


# ---------- create_ticket_type ----------


def test_create_ticket_type_returns_saved():
    # GIVEN the admin wants to create a new ticket type
    ticket_type_repo = MockTicketTypeRepo()
    ticket_type_service = TicketTypeService(ticket_type_repo)
    new_type = TicketType("Child", 0.5, True)

    # WHEN the admin creates it
    created = ticket_type_service.create_ticket_type(new_type)

    # THEN the repo saved it and the service returns it
    assert created is ticket_type_repo.created_ticket_type
    assert created.name == "Child"


# ---------- update_ticket_type ----------


def test_update_ticket_type_returns_updated():
    # GIVEN ticket type 1 exists
    ticket_type_repo = MockTicketTypeRepo([TicketType("Student", 0.7, True, id=1)])
    ticket_type_service = TicketTypeService(ticket_type_repo)

    # WHEN the admin updates its multiplier
    updated_type = TicketType("Student", 0.6, True, id=1)
    updated = ticket_type_service.update_ticket_type(updated_type)

    # THEN the repo saved the update and the service returns it
    assert updated is ticket_type_repo.updated_ticket_type
    assert updated.price_multiplier == 0.6


# ---------- delete_ticket_type ----------


def test_delete_ticket_type_ok():
    # GIVEN ticket type 1 exists
    ticket_type_repo = MockTicketTypeRepo([TicketType("Student", 0.7, True, id=1)])
    ticket_type_service = TicketTypeService(ticket_type_repo)

    # WHEN the admin deletes it
    result = ticket_type_service.delete_ticket_type(1)

    # THEN it is deleted
    assert result is True
    assert ticket_type_repo.deleted_ticket_type_id == 1
    assert len(ticket_type_repo.ticket_types) == 0


def test_delete_ticket_type_unknown():
    # GIVEN ticket type 99 does not exist
    ticket_type_repo = MockTicketTypeRepo([TicketType("Student", 0.7, True, id=1)])
    ticket_type_service = TicketTypeService(ticket_type_repo)

    # WHEN the admin deletes it / THEN we get False
    assert ticket_type_service.delete_ticket_type(99) is False
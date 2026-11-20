from src.Business_object.TicketType import TicketType
from src.DAO.TicketTypeRepo import TicketTypeRepo

# These tests never use the real database: we give TicketTypeRepo a fake DBConnector.
# They only check the Python part of the repo. They cannot tell if the SQL is correct: that needs a real database.


class MockDBConnector:
    """Fake DBConnector.
    - it returns the answer we prepared (as if PostgreSQL had answered)
    - it remembers the data it received, so that we can check them in the tests
    """

    def __init__(self, answer):
        self.answer = answer
        self.last_data = None

    def sql_query(self, query, data=None, return_type="one"):
        # Remember what the repo sent
        self.last_data = data
        # Return the prepared answer
        return self.answer


# Rows of the ticket_types table, as PostgreSQL would return them
STUDENT_ROW = {
    "id": 1,
    "name": "Student",
    "price_multiplier": 0.7,
    "active": True,
}
NORMAL_ROW = {
    "id": 2,
    "name": "Normal",
    "price_multiplier": 1,
    "active": True,
}


# ---------- get_all ----------


def test_get_all_several_ticket_types():
    # GIVEN the database contains two ticket types
    ticket_type_repo = TicketTypeRepo(MockDBConnector([STUDENT_ROW, NORMAL_ROW]))

    # WHEN we list them
    ticket_types = ticket_type_repo.get_all()

    # THEN we get two TicketType objects, in the same order
    assert len(ticket_types) == 2
    assert ticket_types[0].name == "Student"
    assert ticket_types[1].price_multiplier == 1


# ---------- insert_ticket_type ----------


def test_insert_ticket_type():
    # GIVEN a new ticket type (no id yet) and a database that returns the saved row
    db_connector = MockDBConnector(STUDENT_ROW)
    ticket_type_repo = TicketTypeRepo(db_connector)

    # WHEN we save it
    created_ticket_type = ticket_type_repo.insert_ticket_type(TicketType("Student", 0.7, True))

    # THEN we get the ticket type with the id given by the database
    assert created_ticket_type.id == 1
    # AND the values of the ticket type are sent, but not the id (PostgreSQL creates it)
    assert db_connector.last_data["price_multiplier"] == 0.7
    assert db_connector.last_data["active"]
    assert "id" not in db_connector.last_data

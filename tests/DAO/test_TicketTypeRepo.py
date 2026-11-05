from src.Business_object.TicketType import TicketType
from src.DAO.TicketTypeRepo import TicketTypeRepo


class MockDBConnector:
    """Fake DBConnector.
    - it returns the answer we prepared (as if PostgreSQL had answered)
    - it remembers the query and the data it received, so that we can check them in the tests
    """

    def __init__(self, answer):
        self.answer = answer
        self.last_query = None
        self.last_data = None

    def sql_query(self, query, data=None, return_type="one"):
        # Remember what the repo sent
        self.last_query = query
        self.last_data = data
        # Return the prepared answer
        return self.answer

# A row of the ticket_type table, as PostgreSQL would return it
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

def make_student(id = 1) -> TicketType:
    """Create the TicketType object used in the tests."""
    return TicketType(
        id= id,
        name= "Student",
        price_multiplier= 0.7,
        active= True,
    )

# ---------- get_by_id ----------


def test_get_by_id_found():
    # GIVEN the database contains the Student ticket type
    db_connector = MockDBConnector(STUDENT_ROW)
    ticket_type_repo = TicketTypeRepo(db_connector)

    # WHEN we search it with the id of our database
    ticket_type = ticket_type_repo.get_by_id(1)

    # THEN we get the ticket type
    assert ticket_type is not None
    assert ticket_type.name == "Student"
    # AND the repo searched with the id
    assert "WHERE id" in db_connector.last_query
    assert db_connector.last_data == [1]

def test_get_by_id_not_found():
    # GIVEN the database finds nothing
    ticket_type_repo = TicketTypeRepo(MockDBConnector(None))

    # WHEN we search a ticket type / THEN we get None
    assert ticket_type_repo.get_by_id(42) is None


# ---------- get_all----------


def test_get_all_several_ticket_type():
    # GIVEN the database contains two ticket types
    ticket_type_repo = TicketTypeRepo(MockDBConnector([STUDENT_ROW, NORMAL_ROW]))

    # WHEN we list the movies
    ticket_types = ticket_type_repo.get_all()

    # THEN we get two TicketType objects, in the same order
    assert len(ticket_types) == 2
    assert ticket_types[0].name == "Student"
    assert ticket_types[1].name == "Normal"


def test_get_screening_movies_no_ticket_type():
    # GIVEN the ticket_types table is empty (PostgreSQL returns an empty list)
    ticket_type_repo = TicketTypeRepo(MockDBConnector([]))

    # WHEN we list the ticket types / THEN we get an empty list
    assert ticket_type_repo.get_all() == []


# ---------- insert ----------


def test_insert_ticket_type():
    # GIVEN a new movie (no id yet) and a database that returns the saved row
    db_connector = MockDBConnector(STUDENT_ROW)
    ticket_type_repo = TicketTypeRepo(db_connector)

    # WHEN we save it
    created_ticket_type = ticket_type_repo.insert_ticket_type(TicketType("Student", 0.7, True, id=1))

    # THEN we get the ticket type with the id given by the database
    assert created_ticket_type.id == 1
    assert created_ticket_type.name == "Student"
    # AND the repo sent an INSERT with the values of the ticket type
    assert "INSERT INTO ticket_types" in db_connector.last_query
    assert db_connector.last_data["price_multiplier"] == 0.7
    assert db_connector.last_data["active"]


# ---------- update ----------


def test_update_found():
    # GIVEN the database returns the updated row (the title was changed)
    updated_row = dict(STUDENT_ROW)
    updated_row["name"] = "ENSAI_Student"
    db_connector = MockDBConnector(updated_row)
    ticket_type_repo = TicketTypeRepo(db_connector)

    ticket_type_to_update: TicketType = make_student()
    ticket_type_to_update.name = "ENSAI_Student"

    # WHEN we update the ticket type
    updated_ticket_type: TicketType | None = ticket_type_repo.update_ticket_type(ticket_type_to_update)

    # THEN we get the updated ticket type
    assert updated_ticket_type is not None
    assert updated_ticket_type.name == "ENSAI_Student"
    # AND the repo sent an UPDATE for the right ticket type
    assert "UPDATE ticket_types" in db_connector.last_query
    assert db_connector.last_data["id"] == 1


def test_update_not_found():
    # GIVEN the ticket type does not exist (PostgreSQL updates no row and returns nothing)
    ticket_type_repo = TicketTypeRepo(MockDBConnector(None))

    # WHEN we update it / THEN we get None
    assert ticket_type_repo.update_ticket_type(make_student(id=42)) is None


# ---------- delete ----------


def test_delete_found():
    # GIVEN the database deleted the ticket type (it returns the id of the deleted row)
    db_connector = MockDBConnector(STUDENT_ROW)
    ticket_type_repo = TicketTypeRepo(db_connector)

    # WHEN we delete it / THEN we get True
    assert ticket_type_repo.delete_ticket_type(1) is True
    # AND the repo sent a DELETE for the right ticket type
    assert "DELETE FROM ticket_types" in db_connector.last_query
    assert db_connector.last_data == [1]


def test_delete_not_found():
    # GIVEN the ticket type does not exist (no row deleted, nothing returned)
    ticket_type_repo = TicketTypeRepo(MockDBConnector(None))

    # WHEN we delete it / THEN we get False
    assert ticket_type_repo.delete_ticket_type(42) is False

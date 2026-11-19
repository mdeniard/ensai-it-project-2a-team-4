import pytest

from src.Service.ScreeningService import ScreeningService

# These tests use fake repos instead of the database (like in tests/Service/test_ReservationService.py)

# ---------- Fake repos ----------


class MockScreeningRepo:
    """Fake ScreeningRepo: only the screenings 1 and 2 exist, and we remember which one was deleted."""

    def __init__(self):
        self.deleted_screening_id = None

    def delete_screening(self, screening_id):
        # The database deletes the screening only if it exists
        if screening_id in (1, 2):
            self.deleted_screening_id = screening_id
            return True
        return False


class MockReservationRepo:
    """Fake ReservationRepo: 3 tickets were sold for screening 2, none for the others."""

    def count_screening_reservations(self, screening_id):
        if screening_id == 2:
            return 3
        return 0


class UnusedRepo:
    """Fake repo for the movies and the rooms: delete_screening does not use them."""


def make_service(screening_repo):
    """Create a ScreeningService that only uses fake repos (so the real database is never used)."""
    return ScreeningService(
        screening_repo=screening_repo,
        movie_repo=UnusedRepo(),
        room_repo=UnusedRepo(),
        reservation_repo=MockReservationRepo(),
    )


# ---------- delete_screening ----------


def test_delete_screening_without_ticket_sold():
    # GIVEN screening 1 exists and no ticket was sold for it
    screening_repo = MockScreeningRepo()
    screening_service = make_service(screening_repo)

    # WHEN the administrator deletes it
    deleted = screening_service.delete_screening(1)

    # THEN the screening is deleted
    assert deleted is True
    assert screening_repo.deleted_screening_id == 1


def test_delete_screening_with_tickets_sold():
    # GIVEN 3 tickets were sold for screening 2
    screening_repo = MockScreeningRepo()
    screening_service = make_service(screening_repo)

    # WHEN the administrator deletes it / THEN ValueError
    with pytest.raises(ValueError):
        screening_service.delete_screening(2)
    # AND the screening is not deleted (its sales stay in the accounting)
    assert screening_repo.deleted_screening_id is None


def test_delete_screening_unknown():
    # GIVEN screening 99 does not exist
    screening_repo = MockScreeningRepo()
    screening_service = make_service(screening_repo)

    # WHEN the administrator deletes it / THEN we get False (the controller answers 404)
    assert screening_service.delete_screening(99) is False

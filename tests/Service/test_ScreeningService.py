from datetime import datetime, timedelta, timezone

import pytest

from src.Service.ScreeningService import ScreeningService

# These tests use fake repos instead of the database (like in tests/Service/test_ReservationService.py)

# A start time in the future, for the screenings created in the tests
NEXT_WEEK = datetime.now(timezone.utc) + timedelta(days=7)

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


# ---------- Fake repos for the new tests ----------


class MockScreeningRepoFull:
    """Fake ScreeningRepo that supports filter_screenings, room_schedule and create_screening."""

    def __init__(self):
        self.deleted_screening_id = None
        self.created_screening = None
        # Pre-configured results
        self._filter_result = []
        self._room_schedule_result = []
        self._session_available = True

    def filter_screenings(self, start_from, movie_id):
        return self._filter_result

    def room_schedule(self, room_number):
        return self._room_schedule_result

    def session_is_available(self, room_id, start_time, end_time):
        return self._session_available

    def create_screening(self, screening):
        screening.id = 1
        self.created_screening = screening
        return screening

    def delete_screening(self, screening_id):
        if screening_id in (1, 2):
            self.deleted_screening_id = screening_id
            return True
        return False


class MockMovieRepo:
    """Fake MovieRepo: only movie 10 exists (duration 120 minutes)."""

    def get_by_id(self, movie_id):
        if movie_id == 10:

            class _Movie:
                duration = 120  # minutes

            return _Movie()
        return None


class MockRoomRepo:
    """Fake RoomRepo: only room 1 exists."""

    def get_by_id(self, room_id):
        if room_id == 1:
            return object()  # any truthy value is enough
        return None


def make_full_service(screening_repo, movie_repo=None, room_repo=None):
    """Create a ScreeningService with fake repos."""
    return ScreeningService(
        screening_repo=screening_repo,
        movie_repo=movie_repo or MockMovieRepo(),
        room_repo=room_repo or MockRoomRepo(),
        reservation_repo=MockReservationRepo(),
    )


# ---------- filter_screenings ----------


def test_filter_screenings_no_filters():
    # GIVEN the repo has 2 upcoming screenings
    from src.Business_object.Screening import Screening

    screening_repo = MockScreeningRepoFull()
    screening_repo._filter_result = [
        Screening(movie_id=1, room_id=1, start_time=None, end_time=None, base_price=10.0, id=1)
    ]
    service = make_full_service(screening_repo)

    # WHEN we list the upcoming screenings without any filter
    result = service.filter_screenings()

    # THEN the repo is called and the result is returned
    assert len(result) == 1


def test_filter_screenings_with_movie_id():
    # GIVEN the repo has screenings
    screening_repo = MockScreeningRepoFull()
    screening_repo._filter_result = []
    service = make_full_service(screening_repo)

    # WHEN we filter by movie id
    result = service.filter_screenings(movie_id=10)

    # THEN the result is returned (empty in this case)
    assert result == []


def test_filter_screenings_with_future_day():
    # GIVEN the repo has screenings
    from datetime import date

    screening_repo = MockScreeningRepoFull()
    screening_repo._filter_result = []
    service = make_full_service(screening_repo)

    # WHEN we filter by a future day
    tomorrow = date.today() + timedelta(days=1)
    result = service.filter_screenings(day=tomorrow)

    # THEN the result is returned
    assert result == []


def test_filter_screenings_with_past_day_uses_now():
    # GIVEN the repo has screenings
    from datetime import date

    screening_repo = MockScreeningRepoFull()
    screening_repo._filter_result = []
    service = make_full_service(screening_repo)

    # WHEN we filter by a past day (should be replaced by "now")
    yesterday = date.today() - timedelta(days=1)
    result = service.filter_screenings(day=yesterday)

    # THEN the result is returned without error
    assert result == []


# ---------- room_schedule ----------


def test_room_schedule_returns_screenings():
    # GIVEN the repo has 1 screening for room 1
    from src.Business_object.Screening import Screening

    screening_repo = MockScreeningRepoFull()
    screening_repo._room_schedule_result = [
        Screening(movie_id=1, room_id=1, start_time=None, end_time=None, base_price=10.0, id=1),
    ]
    service = make_full_service(screening_repo)

    # WHEN we ask for the schedule of room 1
    result = service.room_schedule(1)

    # THEN we get the screenings
    assert len(result) == 1


def test_room_schedule_returns_empty_list():
    # GIVEN the repo has no screening for room 99
    screening_repo = MockScreeningRepoFull()
    screening_repo._room_schedule_result = []
    service = make_full_service(screening_repo)

    # WHEN we ask for the schedule of room 99
    result = service.room_schedule(99)

    # THEN we get an empty list
    assert result == []


# ---------- create_screening ----------


def test_create_screening_ok():
    # GIVEN movie 10 (120 min) and room 1 exist, and the room is free
    screening_repo = MockScreeningRepoFull()
    service = make_full_service(screening_repo)

    start = NEXT_WEEK

    # WHEN the administrator creates a screening
    created = service.create_screening(movie_id=10, room_id=1, start_time=start, base_price=12.5)

    # THEN the screening is saved with the correct end time (start + 120 + 20 = start + 140 min)
    assert created is screening_repo.created_screening
    expected_end = start + timedelta(minutes=140)
    assert created.end_time == expected_end
    assert created.movie_id == 10
    assert created.room_id == 1
    assert created.base_price == 12.5


def test_create_screening_base_price_zero():
    # GIVEN a valid movie and room
    screening_repo = MockScreeningRepoFull()
    service = make_full_service(screening_repo)

    start = NEXT_WEEK

    # WHEN the base price is 0 / THEN ValueError
    with pytest.raises(ValueError, match="greater than 0"):
        service.create_screening(movie_id=10, room_id=1, start_time=start, base_price=0)


def test_create_screening_base_price_negative():
    # GIVEN a valid movie and room
    screening_repo = MockScreeningRepoFull()
    service = make_full_service(screening_repo)

    start = NEXT_WEEK

    # WHEN the base price is negative / THEN ValueError
    with pytest.raises(ValueError, match="greater than 0"):
        service.create_screening(movie_id=10, room_id=1, start_time=start, base_price=-5)


def test_create_screening_in_the_past():
    # GIVEN a valid movie and room, and a start time yesterday
    screening_repo = MockScreeningRepoFull()
    service = make_full_service(screening_repo)
    yesterday = datetime.now(timezone.utc) - timedelta(days=1)

    # WHEN the administrator creates the screening / THEN ValueError and nothing is saved
    with pytest.raises(ValueError, match="in the past"):
        service.create_screening(movie_id=10, room_id=1, start_time=yesterday, base_price=10)
    assert screening_repo.created_screening is None


def test_create_screening_movie_not_found():
    # GIVEN movie 99 does not exist
    screening_repo = MockScreeningRepoFull()
    service = make_full_service(screening_repo)

    start = NEXT_WEEK

    # WHEN we create a screening for an unknown movie / THEN LookupError
    with pytest.raises(LookupError, match="Movie"):
        service.create_screening(movie_id=99, room_id=1, start_time=start, base_price=10)


def test_create_screening_room_not_found():
    # GIVEN room 99 does not exist
    screening_repo = MockScreeningRepoFull()
    service = make_full_service(screening_repo)

    start = NEXT_WEEK

    # WHEN we create a screening in an unknown room / THEN LookupError
    with pytest.raises(LookupError, match="Room"):
        service.create_screening(movie_id=10, room_id=99, start_time=start, base_price=10)


def test_create_screening_room_already_booked():
    # GIVEN the room is already booked on this time slot
    screening_repo = MockScreeningRepoFull()
    screening_repo._session_available = False
    service = make_full_service(screening_repo)

    start = NEXT_WEEK

    # WHEN we create a screening in that room / THEN ValueError
    with pytest.raises(ValueError, match="already booked"):
        service.create_screening(movie_id=10, room_id=1, start_time=start, base_price=10)

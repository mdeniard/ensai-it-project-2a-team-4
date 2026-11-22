from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from src.Service.AccountingService import AccountingService

# These tests use fake repos instead of the database (like the MockDBConnector in tests/DAO/test_UserRepo.py)

NOW = datetime.now(timezone.utc)
START = NOW - timedelta(days=2)
END = NOW - timedelta(days=1)

# ---------- Fake repos ----------


class FakeMovie:
    """Minimal movie: the service only needs its id."""

    def __init__(self, id):
        self.id = id


class MockMovieRepo:
    """Fake MovieRepo: only the movies 1, 2 and 3 exist."""

    def __init__(self):
        self.movies = {1: FakeMovie(1), 2: FakeMovie(2), 3: FakeMovie(3)}

    def get_by_id(self, movie_id):
        return self.movies.get(movie_id)

    def get_all_movies(self):
        return list(self.movies.values())


class MockReservationRepo:
    """Fake ReservationRepo:
    - movie 1 has two screenings (3 tickets for 24.00, and 2 tickets for 16.00)
    - movie 2 has one screening without any reservation
    - movie 3 has no screening at all
    We also remember the arguments of the last call.
    """

    def __init__(self):
        self.rows = {
            1: [
                {
                    "movie_id": 1,
                    "screening_id": 10,
                    "start_time": NOW - timedelta(days=1),
                    "tickets_sold": 3,
                    "revenue": Decimal("24.00"),
                },
                {
                    "movie_id": 1,
                    "screening_id": 11,
                    "start_time": NOW - timedelta(days=2),
                    "tickets_sold": 2,
                    "revenue": Decimal("16.00"),
                },
            ],
            2: [
                {
                    "movie_id": 2,
                    "screening_id": 20,
                    "start_time": NOW + timedelta(days=1),
                    "tickets_sold": 0,
                    "revenue": Decimal("0"),
                },
            ],
            3: [],
        }
        self.calls = []

    def get_accounting_by_movie(self, movie_id, start_from=None, end_at=None):
        self.calls.append((movie_id, start_from, end_at))
        return self.rows.get(movie_id, [])


def make_service(reservation_repo=None):
    """Create an AccountingService that only uses fake repos."""
    return AccountingService(
        reservation_repo=reservation_repo or MockReservationRepo(),
        movie_repo=MockMovieRepo(),
    )


# ---------- detailed_accounting_by_movie -------------
def test_detailed_accounting_by_movie_unknown():
    # GIVEN
    reservation_repo = MockReservationRepo()
    accounting_service = make_service(reservation_repo)

    # WHEN the movie does not exist
    with pytest.raises(LookupError):
        accounting_service.detailed_accounting_by_movie(movie_id=4)
    assert reservation_repo.calls == []


def test_detailed_accounting_by_movie_date_wrong():
    # GIVEN
    reservation_repo = MockReservationRepo()
    accounting_service = make_service(reservation_repo)

    # WHEN the end_date is before the start_date
    with pytest.raises(ValueError):
        accounting_service.detailed_accounting_by_movie(movie_id=1, start_from=END, end_at=START)
    assert reservation_repo.calls == []


def test_detailed_accounting_by_movie_ok():
    # GIVEN
    reservation_repo = MockReservationRepo()
    accounting_service = make_service(reservation_repo)

    # WHEN the request is OK with two screenings
    accounting = accounting_service.detailed_accounting_by_movie(1)

    # THEN the calls is saved and we get a list with one row per screening
    assert reservation_repo.calls is not None
    assert len(accounting) == 2
    assert accounting[0]["screening_id"] == 10
    assert accounting[0]["start_time"] == NOW - timedelta(days=1)
    assert accounting[0]["tickets_sold"] == 3
    assert accounting[0]["revenue"] == Decimal("24.00")
    assert accounting[1]["screening_id"] == 11
    assert accounting[1]["movie_id"] == 1
    assert accounting[0]["movie_id"] == 1


def test_detailed_accounting_by_movie_passes_the_dates_to_the_repo():
    # GIVEN
    reservation_repo = MockReservationRepo()
    accounting_service = make_service(reservation_repo)

    # WHEN we give a period
    accounting_service.detailed_accounting_by_movie(1, START, END)

    # THEN the repo receives the movie and the two dates
    assert reservation_repo.calls == [(1, START, END)]


def test_detailed_accounting_by_movie_without_dates():
    # GIVEN
    reservation_repo = MockReservationRepo()
    accounting_service = make_service(reservation_repo)

    # WHEN we give no date
    accounting_service.detailed_accounting_by_movie(1)

    # THEN the repo receives None for both dates
    assert reservation_repo.calls == [(1, None, None)]


def test_detailed_accounting_by_movie_only_one_date_is_accepted():
    # GIVEN
    reservation_repo = MockReservationRepo()
    accounting_service = make_service(reservation_repo)

    # WHEN only the start date, or only the end date, is given / THEN no error
    accounting_service.detailed_accounting_by_movie(1, start_from=START)
    accounting_service.detailed_accounting_by_movie(1, end_at=END)
    assert len(reservation_repo.calls) == 2


# ---------- get_accounting_by_movie ----------


def test_get_accounting_by_movie_computes_the_totals():
    # GIVEN a movie with 3 + 2 tickets sold, for 24.00 + 16.00
    accounting_service = make_service()

    # WHEN we ask the accounting of the movie
    result = accounting_service.get_accounting_by_movie(1)

    # THEN the totals are summed over all its screenings
    assert result == {"movie_id": 1, "total_revenue": Decimal("40.00"), "total_tickets": 5}


def test_get_accounting_by_movie_screening_without_reservation():
    # GIVEN a movie whose only screening has no reservation
    accounting_service = make_service()

    # WHEN we ask the accounting
    result = accounting_service.get_accounting_by_movie(2)

    # THEN everything is 0
    assert result["total_revenue"] == Decimal("0")
    assert result["total_tickets"] == 0


def test_get_accounting_by_movie_without_screening():
    # GIVEN a movie without any screening
    accounting_service = make_service()

    # WHEN we ask the accounting
    result = accounting_service.get_accounting_by_movie(3)

    # THEN the totals are 0 (and the revenue stays a Decimal)
    assert result == {"movie_id": 3, "total_revenue": Decimal("0"), "total_tickets": 0}
    assert isinstance(result["total_revenue"], Decimal)


def test_get_accounting_by_movie_unknown_movie():
    # GIVEN
    accounting_service = make_service()

    # WHEN the movie does not exist / THEN LookupError
    with pytest.raises(LookupError):
        accounting_service.get_accounting_by_movie(4)


def test_get_accounting_by_movie_start_after_end():
    # GIVEN
    accounting_service = make_service()

    # WHEN the start date is after the end date / THEN ValueError
    with pytest.raises(ValueError):
        accounting_service.get_accounting_by_movie(1, END, START)


# ---------- get_accounting_by_period ----------


def test_get_accounting_by_period_with_given_movies():
    # GIVEN
    accounting_service = make_service()

    # WHEN we ask for the movies 1 and 2 over a period
    result = accounting_service.get_accounting_by_period(START, END, [1, 2])

    # THEN we get one row per movie, in the same order
    assert result == [
        {"movie_id": 1, "total_revenue": Decimal("40.00"), "total_tickets": 5},
        {"movie_id": 2, "total_revenue": Decimal("0"), "total_tickets": 0},
    ]


def test_get_accounting_by_period_pass_the_dates_to_the_repo():
    # GIVEN
    reservation_repo = MockReservationRepo()
    accounting_service = make_service(reservation_repo)

    # WHEN we ask for two movies
    accounting_service.get_accounting_by_period(START, END, [1, 2])

    # THEN the repo is called once per movie with the same period
    assert reservation_repo.calls == [(1, START, END), (2, START, END)]


def test_get_accounting_by_period_all_movies_by_default():
    # GIVEN
    accounting_service = make_service()

    # WHEN no movie is given
    result = accounting_service.get_accounting_by_period(START, END)

    # THEN all the movies of the database are included
    assert [row["movie_id"] for row in result] == [1, 2, 3]


def test_get_accounting_by_period_empty_list_of_movies():
    # GIVEN
    reservation_repo = MockReservationRepo()
    accounting_service = make_service(reservation_repo)

    # WHEN the list of movies is empty (not None) / THEN nothing is computed
    assert accounting_service.get_accounting_by_period(START, END, []) == []
    assert reservation_repo.calls == []


def test_get_accounting_by_period_unknown_movie():
    # GIVEN
    accounting_service = make_service()

    # WHEN one of the movies does not exist / THEN LookupError
    with pytest.raises(LookupError):
        accounting_service.get_accounting_by_period(START, END, [1, 99])


def test_get_accounting_by_period_start_after_end():
    # GIVEN
    accounting_service = make_service()

    # WHEN the start date is after the end date / THEN ValueError
    with pytest.raises(ValueError):
        accounting_service.get_accounting_by_period(END, START, [1])

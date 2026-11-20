import pytest

from src.Business_object.Review import Review
from src.Service.ReviewService import ReviewService

# ---------- Fake repos ----------


class MockReviewRepo:
    """Fake ReviewRepo: configurable per test."""

    def __init__(self):
        self.created_review = None
        self.deleted_review = None
        self.deleted_by_id = None
        # Configurable results
        self._has_seen_movie = True
        self._existing_review = None
        self._customer_reviews = []
        self._movie_reviews = []
        self._review_by_id = None

    def has_seen_movie(self, customer_id, movie_id):
        return self._has_seen_movie

    def get_by_customer_and_movie(self, customer_id, movie_id):
        return self._existing_review

    def create_review(self, review):
        review.id = 1
        review.created_at = "2026-07-01T12:00:00"
        self.created_review = review
        return review

    def delete_review(self, movie_id, customer_id):
        self.deleted_review = (movie_id, customer_id)
        return True

    def get_customer_reviews(self, customer_id):
        return self._customer_reviews

    def get_movie_reviews(self, movie_id):
        return self._movie_reviews

    def get_by_id(self, review_id):
        return self._review_by_id

    def delete_by_id(self, review_id):
        self.deleted_by_id = review_id
        return True


class MockMovieRepo:
    """Fake MovieRepo: only movie 10 exists."""

    def __init__(self, existing_movie_ids=None):
        self.existing_movie_ids = existing_movie_ids if existing_movie_ids is not None else {10}

    def get_by_id(self, movie_id):
        if movie_id in self.existing_movie_ids:
            return object()
        return None


def make_service(review_repo=None, movie_repo=None):
    """Create a ReviewService with fake repos."""
    return ReviewService(
        review_repo=review_repo or MockReviewRepo(),
        movie_repo=movie_repo or MockMovieRepo(),
    )


# ---------- create_review ----------


def test_create_review_ok():
    # GIVEN the customer has seen movie 10, has not reviewed it yet, and gives a valid rating
    review_repo = MockReviewRepo()
    service = make_service(review_repo=review_repo)
    review = Review(customer_id=1, movie_id=10, rating=8, comment="Great film!")

    # WHEN the customer writes the review
    created = service.create_review(review)

    # THEN the review is saved with its id
    assert created is review_repo.created_review
    assert created.id == 1
    assert created.rating == 8
    assert created.comment == "Great film!"


def test_create_review_comment_stripped_to_none():
    # GIVEN the customer writes a review with a whitespace-only comment
    review_repo = MockReviewRepo()
    service = make_service(review_repo=review_repo)
    review = Review(customer_id=1, movie_id=10, rating=7, comment="   ")

    # WHEN the review is saved
    created = service.create_review(review)

    # THEN the comment is saved as None (empty comment = no comment)
    assert created.comment is None


def test_create_review_comment_stripped():
    # GIVEN the customer writes a review with a comment that has surrounding spaces
    review_repo = MockReviewRepo()
    service = make_service(review_repo=review_repo)
    review = Review(customer_id=1, movie_id=10, rating=7, comment="  Good  ")

    # WHEN the review is saved
    created = service.create_review(review)

    # THEN the comment is stripped
    assert created.comment == "Good"


def test_create_review_rating_too_low():
    # GIVEN the customer gives a rating of 0
    review_repo = MockReviewRepo()
    service = make_service(review_repo=review_repo)
    review = Review(customer_id=1, movie_id=10, rating=0, comment=None)

    # WHEN the review is submitted / THEN ValueError
    with pytest.raises(ValueError, match="between 1 and 10"):
        service.create_review(review)

    # AND nothing is saved
    assert review_repo.created_review is None


def test_create_review_rating_too_high():
    # GIVEN the customer gives a rating of 11
    review_repo = MockReviewRepo()
    service = make_service(review_repo=review_repo)
    review = Review(customer_id=1, movie_id=10, rating=11, comment=None)

    # WHEN the review is submitted / THEN ValueError
    with pytest.raises(ValueError, match="between 1 and 10"):
        service.create_review(review)

    assert review_repo.created_review is None


def test_create_review_movie_not_found():
    # GIVEN the movie does not exist
    review_repo = MockReviewRepo()
    movie_repo = MockMovieRepo(existing_movie_ids={10})
    service = make_service(review_repo=review_repo, movie_repo=movie_repo)
    review = Review(customer_id=1, movie_id=99, rating=5, comment=None)

    # WHEN the review is submitted / THEN LookupError
    with pytest.raises(LookupError, match="Movie"):
        service.create_review(review)

    assert review_repo.created_review is None


def test_create_review_has_not_seen_movie():
    # GIVEN the customer has not seen the movie (no past reservation)
    review_repo = MockReviewRepo()
    review_repo._has_seen_movie = False
    service = make_service(review_repo=review_repo)
    review = Review(customer_id=1, movie_id=10, rating=5, comment=None)

    # WHEN the review is submitted / THEN ValueError
    with pytest.raises(ValueError, match="only review a movie you have seen"):
        service.create_review(review)

    assert review_repo.created_review is None


def test_create_review_already_reviewed():
    # GIVEN the customer has already reviewed this movie
    review_repo = MockReviewRepo()
    review_repo._existing_review = Review(customer_id=1, movie_id=10, rating=7, comment="Ok", id=1)
    service = make_service(review_repo=review_repo)
    review = Review(customer_id=1, movie_id=10, rating=9, comment="Changed my mind")

    # WHEN the customer tries to review it again / THEN ValueError
    with pytest.raises(ValueError, match="already reviewed"):
        service.create_review(review)

    assert review_repo.created_review is None


# ---------- delete_review ----------


def test_delete_review_ok():
    # GIVEN the customer has a review for movie 10
    review_repo = MockReviewRepo()
    review_repo._existing_review = Review(customer_id=1, movie_id=10, rating=7, comment=None, id=1)
    service = make_service(review_repo=review_repo)

    # WHEN the customer deletes their review
    result = service.delete_review(movie_id=10, customer_id=1)

    # THEN the review is deleted
    assert result is True
    assert review_repo.deleted_review == (10, 1)


def test_delete_review_no_review_exists():
    # GIVEN the customer has no review for movie 10
    review_repo = MockReviewRepo()
    review_repo._existing_review = None
    service = make_service(review_repo=review_repo)

    # WHEN the customer tries to delete their review / THEN LookupError
    with pytest.raises(LookupError, match="no review for movie"):
        service.delete_review(movie_id=10, customer_id=1)

    assert review_repo.deleted_review is None


# ---------- get_customer_reviews ----------


def test_get_customer_reviews_returns_reviews():
    # GIVEN the customer has written 2 reviews
    review_repo = MockReviewRepo()
    review_repo._customer_reviews = [
        Review(customer_id=1, movie_id=10, rating=8, comment="Great", id=1),
        Review(customer_id=1, movie_id=11, rating=6, comment=None, id=2),
    ]
    service = make_service(review_repo=review_repo)

    # WHEN we list the customer's reviews
    result = service.get_customer_reviews(1)

    # THEN we get them
    assert len(result) == 2


def test_get_customer_reviews_returns_empty_list():
    # GIVEN the customer has written no review
    review_repo = MockReviewRepo()
    review_repo._customer_reviews = []
    service = make_service(review_repo=review_repo)

    # WHEN we list the customer's reviews / THEN we get an empty list
    assert service.get_customer_reviews(1) == []


# ---------- get_movie_reviews ----------


def test_get_movie_reviews_returns_reviews():
    # GIVEN movie 10 exists and has 1 review
    review_repo = MockReviewRepo()
    review_repo._movie_reviews = [Review(customer_id=1, movie_id=10, rating=9, comment="Best", id=1)]
    service = make_service(review_repo=review_repo)

    # WHEN we list the reviews of the movie
    result = service.get_movie_reviews(10)

    # THEN we get them
    assert len(result) == 1


def test_get_movie_reviews_returns_empty_list():
    # GIVEN movie 10 exists but has no review
    review_repo = MockReviewRepo()
    review_repo._movie_reviews = []
    service = make_service(review_repo=review_repo)

    # WHEN we list the reviews of the movie / THEN we get an empty list
    assert service.get_movie_reviews(10) == []


def test_get_movie_reviews_movie_not_found():
    # GIVEN movie 99 does not exist
    review_repo = MockReviewRepo()
    movie_repo = MockMovieRepo(existing_movie_ids={10})
    service = make_service(review_repo=review_repo, movie_repo=movie_repo)

    # WHEN we list the reviews of the movie / THEN LookupError
    with pytest.raises(LookupError, match="Movie"):
        service.get_movie_reviews(99)


# ---------- delete_review_as_admin ----------


def test_delete_review_as_admin_ok():
    # GIVEN review 5 exists
    review_repo = MockReviewRepo()
    review_repo._review_by_id = Review(customer_id=1, movie_id=10, rating=1, comment="Spam", id=5)
    service = make_service(review_repo=review_repo)

    # WHEN the admin deletes it (moderation)
    result = service.delete_review_as_admin(5)

    # THEN the review is deleted
    assert result is True
    assert review_repo.deleted_by_id == 5


def test_delete_review_as_admin_not_found():
    # GIVEN review 99 does not exist
    review_repo = MockReviewRepo()
    review_repo._review_by_id = None
    service = make_service(review_repo=review_repo)

    # WHEN the admin tries to delete it / THEN LookupError
    with pytest.raises(LookupError, match="Review"):
        service.delete_review_as_admin(99)

    assert review_repo.deleted_by_id is None

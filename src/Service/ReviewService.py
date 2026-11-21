from typing import Optional

from src.Business_object.Review import Review
from src.DAO.MovieRepo import MovieRepo
from src.DAO.ReviewRepo import ReviewRepo


class ReviewService:
    """Service that manages the reviews of the movies written by the customers."""

    def __init__(
        self,
        review_repo: Optional[ReviewRepo] = None,
        movie_repo: Optional[MovieRepo] = None,
    ) -> None:
        """Create the service.
        Args:
            review_repo (ReviewRepo, optional): Access to the reviews in the database.
            movie_repo (MovieRepo, optional): Access to the movies in the database.
                If one is not given, a new one is created.
        """
        self.review_repo = review_repo or ReviewRepo()
        self.movie_repo = movie_repo or MovieRepo()

    def create_review(self, review: Review) -> Review:
        """Write a review for a movie the customer has seen.
        The review is refused if the rating is not between 1 and 10, if the movie does not exist,
        if the customer has not seen the movie (no reservation for a screening of this movie that is
        already over) or if he has already reviewed it. An empty comment is saved as None.
        Args:
            review (Review): The review to save (customer, movie, rating and optional comment).
        Returns:
            The saved Review, with its id and its creation date.
        """
        # The rating must be between 1 and 10
        if not 1 <= review.rating <= 10:
            raise ValueError("The rating must be between 1 and 10")

        # Check that the movie exists
        if self.movie_repo.get_by_id(review.movie_id) is None:
            raise LookupError(f"Movie [{review.movie_id}] not found")

        # Check that the customer has seen the movie
        # (a reservation for a screening of this movie that is already over)
        if not self.review_repo.has_seen_movie(review.customer_id, review.movie_id):
            raise ValueError("You can only review a movie you have seen")

        # One review per customer and per movie
        if self.review_repo.get_by_customer_and_movie(review.customer_id, review.movie_id) is not None:
            raise ValueError("You have already reviewed this movie")

        # An empty comment is saved as None
        if review.comment is not None:
            review.comment = review.comment.strip() or None

        return self.review_repo.create_review(review)

    def delete_review(self, movie_id: int, customer_id: int) -> bool:
        """Delete my review of a movie.
        Args:
            movie_id (int): The database id of the movie.
            customer_id (int): The database id of the logged-in customer.
        Returns:
            True if the review was deleted. The deletion is refused if the customer
            has no review for this movie.
        """
        if self.review_repo.get_by_customer_and_movie(customer_id, movie_id) is None:
            raise LookupError(f"You have no review for movie [{movie_id}]")

        return self.review_repo.delete_review(movie_id, customer_id)

    def get_customer_reviews(self, customer_id: int) -> list[Review]:
        """List the reviews written by a customer, the most recent first.
        Args:
            customer_id (int): The database id of the customer.
        Returns:
            list[Review] of the customer, or an empty list if he has written none.
        """
        return self.review_repo.get_customer_reviews(customer_id)

    def get_movie_reviews(self, movie_id: int) -> list[Review]:
        """List the reviews of a movie, the most recent first.
        The request is refused if the movie does not exist.
        Args:
            movie_id (int): The database id of the movie.
        Returns:
            list[Review] of the movie, or an empty list if it has none.
        """
        if self.movie_repo.get_by_id(movie_id) is None:
            raise LookupError(f"Movie [{movie_id}] not found")
        return self.review_repo.get_movie_reviews(movie_id)

    def delete_review_as_admin(self, review_id: int) -> bool:
        """Delete any review, whoever wrote it (moderation by an administrator).
        Args:
            review_id (int): The database id of the review to delete.
        Returns:
            True if the review was deleted. The deletion is refused if the review does not exist.
        """
        if self.review_repo.get_by_id(review_id) is None:
            raise LookupError(f"Review [{review_id}] not found")
        return self.review_repo.delete_by_id(review_id)

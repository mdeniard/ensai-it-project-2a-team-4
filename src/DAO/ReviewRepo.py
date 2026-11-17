from typing import Optional

from src.Business_object.Review import Review

from .DBConnector import DBConnector


class ReviewRepo:
    """Repository that manages the reviews in the database (table reviews)."""

    db_connector: DBConnector

    def __init__(self, db_connector: Optional[DBConnector] = None) -> None:
        """Create the repository.
        Args:
            db_connector (DBConnector, optional): The connection to the database.
                If none is given, a new DBConnector is created.
        """
        self.db_connector = db_connector or DBConnector()

    def has_seen_movie(self, customer_id: int, movie_id: int) -> bool:
        """Check that a customer has seen a movie, meaning he has a reservation
        for a screening of this movie that is already over.
        Args:
            customer_id (int): The database id of the customer.
            movie_id (int): The database id of the movie.
        Returns:
            True if the customer has seen the movie, False otherwise.
        """
        raw = self.db_connector.sql_query(
            """
            SELECT 1
            FROM reservations r
            JOIN screenings s ON s.id = r.screening_id
            WHERE r.customer_id = %(customer_id)s
              AND s.movie_id = %(movie_id)s
              AND s.end_time <= NOW()
            LIMIT 1;
            """,
            {"customer_id": customer_id, "movie_id": movie_id},
            "one",
        )
        return raw is not None

    def get_by_id(self, id: int) -> Optional[Review]:
        """Retrieve a review by its database identifier.
        Args:
            id (int): The unique database id of the review.
        Returns:
            The Review object, or None if no review has this id.
        """
        raw_review = self.db_connector.sql_query("SELECT * FROM reviews WHERE id = %s;", [id], "one")
        if raw_review is None:
            return None
        return Review(**raw_review)

    def get_by_customer_and_movie(self, customer_id: int, movie_id: int) -> Optional[Review]:
        """Retrieve the review a customer wrote for a movie (a customer can write only one per movie).
        Args:
            customer_id (int): The database id of the customer.
            movie_id (int): The database id of the movie.
        Returns:
            The Review object, or None if the customer has not reviewed this movie.
        """
        raw_review = self.db_connector.sql_query(
            "SELECT * FROM reviews WHERE customer_id = %(customer_id)s AND movie_id = %(movie_id)s;",
            {"customer_id": customer_id, "movie_id": movie_id},
            "one",
        )
        if raw_review is None:
            return None
        return Review(**raw_review)

    def create_review(self, review: Review) -> Review:
        """Save a new review (the id and the date are given by the database).
        Args:
            review (Review): The review to save (customer, movie, rating and optional comment).
        Returns:
            The saved Review, with its id and its creation date.
        """
        raw = self.db_connector.sql_query(
            """
            INSERT INTO reviews (customer_id, movie_id, rating, comment)
            VALUES (%(customer_id)s, %(movie_id)s, %(rating)s, %(comment)s)
            RETURNING *;
            """,
            {
                "customer_id": review.customer_id,
                "movie_id": review.movie_id,
                "rating": review.rating,
                "comment": review.comment,
            },
            "one",
        )
        return Review(**raw)

    def delete_review(self, movie_id: int, customer_id: int) -> bool:
        """Delete the review a customer wrote for a movie.
        Args:
            movie_id (int): The database id of the movie.
            customer_id (int): The database id of the customer who wrote the review.
        Returns:
            True if a review was deleted, False if this customer has no review for this movie.
        """
        raw = self.db_connector.sql_query(
            """
            DELETE FROM reviews
            WHERE movie_id = %(movie_id)s
              AND customer_id = %(customer_id)s
            RETURNING id;
            """,
            {"movie_id": movie_id, "customer_id": customer_id},
            "one",
        )
        return raw is not None

    def get_customer_reviews(self, customer_id: int) -> list[Review]:
        """Retrieve all the reviews written by a customer, the most recent first.
        Args:
            customer_id (int): The database id of the customer.
        Returns:
            list[Review] of the customer, or an empty list if he has written none.
        """
        raw_reviews = self.db_connector.sql_query(
            "SELECT * FROM reviews WHERE customer_id = %s ORDER BY created_at DESC;",
            [customer_id],
            "all",
        )
        return [Review(**raw) for raw in raw_reviews or []]

    def get_movie_reviews(self, movie_id: int) -> list[Review]:
        """Retrieve all the reviews of a movie, the most recent first.
        Args:
            movie_id (int): The database id of the movie.
        Returns:
            list[Review] of the movie, or an empty list if it has none.
        """
        raw_reviews = self.db_connector.sql_query(
            "SELECT * FROM reviews WHERE movie_id = %s ORDER BY created_at DESC;",
            [movie_id],
            "all",
        )
        return [Review(**raw) for raw in raw_reviews or []]

    def delete_by_id(self, review_id: int) -> bool:
        """Delete a review whoever wrote it (used for moderation by an administrator).
        Args:
            review_id (int): The database id of the review to delete.
        Returns:
            True if a review was deleted, False if no review has this id.
        """
        raw = self.db_connector.sql_query(
            """
            DELETE FROM reviews
            WHERE id = %(id)s
            RETURNING id;
            """,
            {"id": review_id},
            "one",
        )
        return raw is not None
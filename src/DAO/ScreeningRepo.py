from datetime import datetime
from typing import Optional

from src.Business_object.Screening import Screening

from .DBConnector import DBConnector


class ScreeningRepo:
    """Repository that manages the screenings in the database (table screenings)."""

    db_connector: DBConnector

    def __init__(self, db_connector: Optional[DBConnector] = None) -> None:
        """Create the repository.
        Args:
            db_connector (DBConnector, optional): The connection to the database.
                If none is given, a new DBConnector is created.
        """
        self.db_connector = db_connector or DBConnector()

    def get_by_id(self, id: int) -> Optional[Screening]:
        """Retrieve a screening by its database identifier.
        Args:
            id (int): The unique database id of the screening.
        Returns:
            The Screening object, or None if no screening has this id.
        """
        raw_screening = self.db_connector.sql_query("SELECT * FROM screenings WHERE id = %s;", [id], "one")
        if raw_screening is None:
            return None
        return Screening(**raw_screening)

    def filter_screenings(
        self, start_from: Optional[datetime] = datetime.now(), movie_id: Optional[int] = None
    ) -> list[Screening]:
        """Retrieve the upcoming screenings, sorted by start time (50 at most).
        Args:
            start_from (datetime, optional): Only the screenings starting at this moment or later are returned.
            movie_id (int, optional): Only the screenings of this movie (its id in our database).
        Returns:
            list[Screening] of the matching screenings, or an empty list if there is none.
        """
        query = """
            SELECT * FROM screenings
            WHERE start_time >= %(start_from)s
        """
        params: dict = {"start_from": start_from}

        if movie_id is not None:
            query += " AND movie_id = %(movie_id)s"
            params["movie_id"] = movie_id

        query += " ORDER BY start_time LIMIT 50;"

        raw_screenings = self.db_connector.sql_query(query, params, "all")
        return [Screening(**raw) for raw in raw_screenings or []]

    def room_schedule(
        self,
        room_number: int,
        start_from: Optional[datetime] = None,
    ) -> list[Screening]:
        """Retrieve the upcoming screenings of a room, sorted by start time.
        Args:
            room_number (int): The number of the room (not its database id).
            start_from (datetime, optional): Only the screenings starting at this moment or later.
                If none is given, the current time is used.
        Returns:
            list[Screening] of the room, or an empty list if there is none.
        """
        if start_from is None:
            start_from = datetime.now()

        raw_screenings = self.db_connector.sql_query(
            """
            SELECT s.*
            FROM screenings s
            JOIN rooms r ON r.id = s.room_id
            WHERE r.room_number = %(room_number)s
              AND s.start_time >= %(start_from)s
            ORDER BY s.start_time;
            """,
            {"room_number": room_number, "start_from": start_from},
            "all",
        )
        return [Screening(**raw) for raw in raw_screenings or []]

    def create_screening(self, screening: Screening) -> Screening:
        """Save a new screening (the id is given by the database).
        Args:
            screening (Screening): The screening to save (movie, room, start time, end time and base price).
        Returns:
            The saved Screening, with its id.
        """
        raw = self.db_connector.sql_query(
            """
            INSERT INTO screenings (movie_id, room_id, start_time, end_time, base_price)
            VALUES (%(movie_id)s, %(room_id)s, %(start_time)s, %(end_time)s, %(base_price)s)
            RETURNING *;
            """,
            {
                "movie_id": screening.movie_id,
                "room_id": screening.room_id,
                "start_time": screening.start_time,
                "end_time": screening.end_time,
                "base_price": screening.base_price,
            },
            "one",
        )
        return Screening(**raw)

    def session_is_available(self, room_id: int, start_time: datetime, end_time: datetime) -> bool:
        """Check that a room is free during a time slot.
        Args:
            room_id (int): The database id of the room.
            start_time (datetime): The start of the time slot.
            end_time (datetime): The end of the time slot.
        Returns:
            True if the room has no screening overlapping [start_time, end_time), False otherwise.
        """
        raw = self.db_connector.sql_query(
            """
            SELECT id FROM screenings
            WHERE room_id = %(room_id)s
              AND start_time < %(end_time)s
              AND end_time > %(start_time)s
            LIMIT 1;
            """,
            {"room_id": room_id, "start_time": start_time, "end_time": end_time},
            "one",
        )
        return raw is None

    def delete_screening(self, screening_id: int) -> bool:
        """Delete a screening. Its reservations are deleted too (ON DELETE CASCADE).
        Args:
            screening_id (int): The database id of the screening to delete.
        Returns:
            True if a screening was deleted, False if no screening has this id.
        """
        raw = self.db_connector.sql_query(
            """
            DELETE FROM screenings
            WHERE id = %(id)s
            RETURNING id;
            """,
            {"id": screening_id},
            "one",
        )
        return raw is not None
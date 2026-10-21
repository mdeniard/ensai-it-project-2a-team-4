from datetime import datetime
from typing import Optional

from src.Business_object.Screening import Screening

from .DBConnector import DBConnector


class ScreeningRepo:
    db_connector: DBConnector

    def __init__(self, db_connector: Optional[DBConnector] = None) -> None:
        self.db_connector = db_connector or DBConnector()

    def get_by_id(self, id: int) -> Optional[Screening]:
        raw_screening = self.db_connector.sql_query(
            "SELECT * FROM screenings WHERE id = %s;",
            [id],
            "one"
        )
        if raw_screening is None:
            return None
        return Screening(**raw_screening)

    def filter_screenings(
        self,
        start_from: Optional[datetime] = datetime.now(),
        movie_id: Optional[int] = None
        ) -> list[Screening]:
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
        raw = self.db_connector.sql_query(
            """
            INSERT INTO screenings (movie_id, room_id, start_time, end_time)
            VALUES (%(movie_id)s, %(room_id)s, %(start_time)s, %(end_time)s)
            RETURNING *;
            """,
            {
                "movie_id": screening.movie_id,
                "room_id": screening.room_id,
                "start_time": screening.start_time,
                "end_time": screening.end_time,
            },
            "one",
        )
        return Screening(**raw)

    def session_is_available(self, room_id: int, start_time: datetime, end_time: datetime) -> bool:
        """
        False if the room already has a screening overlapping [start_time, end_time)
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
        """
        Deletes a screening by id. Returns True if a row was deleted.
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


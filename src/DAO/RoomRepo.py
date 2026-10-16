from typing import Optional

from src.Business_object.Room import Room

from .DBConnector import DBConnector


class RoomRepo:
    db_connector: DBConnector

    def __init__(self, db_connector: Optional[DBConnector] = None) -> None:
        self.db_connector = db_connector or DBConnector()

    def get_by_id(self, id: int) -> Optional[Room]:
        raw_room = self.db_connector.sql_query(
            "SELECT * FROM room WHERE id = %s;",
            [id],
            "one"
        )
        if raw_room is None:
            return None
        return Room(**raw_room)

    def get_by_number(self, room_number: int) -> Optional[Room]:
        raw_room = self.db_connector.sql_query(
            "SELECT * FROM room WHERE room_number = %s;",
            [room_number],
            "one"
        )
        if raw_room is None:
            return None
        return Room(**raw_room)

    def get_all(self) -> list[Room]:
        raw_rooms = self.db_connector.sql_query(
            "SELECT * FROM room;",
            return_type="all"
        )
        if not raw_rooms:
                    return []

        return [Room(**room_data) for room_data in raw_rooms]

    def create_room(self, room: Room) -> Room:
        raw_created_room = self.db_connector.sql_query(
            """
            INSERT INTO room (room_number, capacity)
            VALUES (%(room_number)s, %(capacity)s)
            RETURNING *;
            """,
            {
                "room_number": room.room_number,
                "capacity": room.capacity,
            },
            "one",
        )
        return Room(**raw_created_room)

    def update_room(self, room: Room) -> Optional[Room]:
        raw_updated_room = self.db_connector.sql_query(
            """
            UPDATE room
            SET room_number = %(room_number)s,
                capacity = %(capacity)s
            WHERE id = %(id)s
            RETURNING *;
            """,
            {
                "id": room.id,
                "room_number": room.room_number,
                "capacity": room.capacity
            },
            "one",
        )

        if raw_updated_room is None:
            return None

        return Room(**raw_updated_room)

    def delete_room(self, room_id: int) -> bool:
        raw_deleted_room = self.db_connector.sql_query(
            """
            DELETE FROM room
            WHERE id = %(id)s
            RETURNING id;
            """,
            {"id": room_id},
            "one",
        )
        # pyrefly: ignore
        return raw_deleted_room is not None

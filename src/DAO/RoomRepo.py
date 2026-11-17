from typing import Optional

from src.Business_object.Room import Room

from .DBConnector import DBConnector


class RoomRepo:
    """Repository that manages the rooms in the database (table rooms)."""

    db_connector: DBConnector

    def __init__(self, db_connector: Optional[DBConnector] = None) -> None:
        """Create the repository.
        Args:
            db_connector (DBConnector, optional): The connection to the database.
                If none is given, a new DBConnector is created.
        """
        self.db_connector = db_connector or DBConnector()

    def get_by_id(self, id: int) -> Optional[Room]:
        """Retrieve a room by its database identifier.
        Args:
            id (int): The unique database id of the room.
        Returns:
            The Room object, or None if no room has this id.
        """
        raw_room = self.db_connector.sql_query("SELECT * FROM rooms WHERE id = %s;", [id], "one")
        if raw_room is None:
            return None
        return Room(**raw_room)

    def get_by_number(self, room_number: int) -> Optional[Room]:
        """Retrieve a room by its room number.
        Args:
            room_number (int): The unique number of the room (not its database id).
        Returns:
            The Room object, or None if no room has this number.
        """
        raw_room = self.db_connector.sql_query("SELECT * FROM rooms WHERE room_number = %s;", [room_number], "one")
        if raw_room is None:
            return None
        return Room(**raw_room)

    def get_all(self) -> list[Room]:
        """Retrieve all the rooms of the theater.
        Returns:
            list[Room] of all the rooms, or an empty list if there is none.
        """
        raw_rooms = self.db_connector.sql_query("SELECT * FROM rooms;", return_type="all")
        if not raw_rooms:
            return []

        return [Room(**room_data) for room_data in raw_rooms]

    def create_room(self, room: Room) -> Room:
        """Save a new room (the id is given by the database).
        Args:
            room (Room): The room to save (room number and capacity).
        Returns:
            The saved Room, with its id.
        """
        raw_created_room = self.db_connector.sql_query(
            """
            INSERT INTO rooms (room_number, capacity)
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
        """Update the room number and the capacity of an existing room.
        Args:
            room (Room): The room with its new data. Its id identifies the row to update.
        Returns:
            The updated Room, or None if no room has this id.
        """
        raw_updated_room = self.db_connector.sql_query(
            """
            UPDATE rooms
            SET room_number = %(room_number)s,
                capacity = %(capacity)s
            WHERE id = %(id)s
            RETURNING *;
            """,
            {"id": room.id, "room_number": room.room_number, "capacity": room.capacity},
            "one",
        )

        if raw_updated_room is None:
            return None

        return Room(**raw_updated_room)

    def delete_room(self, room_id: int) -> bool:
        """Delete a room. Its screenings and their reservations are deleted too (ON DELETE CASCADE).
        Args:
            room_id (int): The database id of the room to delete.
        Returns:
            True if a room was deleted, False if no room has this id.
        """
        raw_deleted_room = self.db_connector.sql_query(
            """
            DELETE FROM rooms
            WHERE id = %(id)s
            RETURNING id;
            """,
            {"id": room_id},
            "one",
        )
        # pyrefly: ignore
        return raw_deleted_room is not None
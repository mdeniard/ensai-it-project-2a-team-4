from typing import TYPE_CHECKING, Optional

from src.DAO.RoomRepo import RoomRepo

if TYPE_CHECKING:
    from src.Business_object.Room import Room


class RoomService:
    def __init__(
        self,
        room_repo: Optional[RoomRepo] = None,
    ):
        """Create the service.
        Args:
            room_repo (RoomRepo, optional): Access to the rooms in the database.
                If none is given, a new RoomRepo is created.
        """
        # Access to our own database (table room)
        self.room_repo = room_repo or RoomRepo()

    def get_by_id(self, room_id: int) -> Optional[Room]:
        """Find a room by its database id.
        Args:
            room_id (int): The database id of the wanted room.
        Returns:
            The Room, or None if no room has this id.
        """
        return self.room_repo.get_by_id(room_id)

    def get_by_number(self, room_number: int) -> Optional[Room]:
        """Find a room by its room number.
        Args:
            room_number (int): The number of the wanted room (not its database id).
        Returns:
            The Room, or None if no room has this number.
        """
        return self.room_repo.get_by_number(room_number)

    def get_all(self) -> list[Room]:
        """List all the rooms of the theater.
        Returns:
            list[Room] of all the rooms, or an empty list if there is none.
        """
        return self.room_repo.get_all()

    def create_room(self, room: Room) -> Optional[Room]:
        """Create a room.
        Args:
            room (Room): The room to save (room number and capacity).
        Returns:
            The saved Room, with its id.
        """
        return self.room_repo.create_room(room)

    def update_room(self, room: Room) -> Optional[Room]:
        """Update the room number and the capacity of a room.
        Args:
            room (Room): The room with its new data. Its id identifies the one to update.
        Returns:
            The updated Room, or None if no room has this id.
        """
        return self.room_repo.update_room(room)

    def delete_room(self, room_id: int) -> bool:
        """Delete a room. Its screenings and their reservations are deleted too.
        Args:
            room_id (int): The database id of the room to delete.
        Returns:
            True if the room was deleted, False if no room has this id.
        """
        return self.room_repo.delete_room(room_id)

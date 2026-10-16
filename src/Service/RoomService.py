from typing import Optional

from src.Business_object.Room import Room
from src.DAO.RoomRepo import RoomRepo


class RoomService:
    """Service that manages rooms."""

    def __init__(
        self,
        room_repo: Optional[RoomRepo] = None,
    ):
        # Access to our own database (table room)
        self.room_repo = room_repo or RoomRepo()

    def get_by_id(self, room_id: int) -> Optional[Room]:
        """Get the room with the id
        Args:
            room_id : id of the wanted room
        """
        return self.room_repo.get_by_id(room_id)

    def get_by_number(self, room_number: int) -> Optional[Room]:
        """Get the room with the number
        Args:
            room_number : number of the wanted room
        """
        return self.room_repo.get_by_number(room_number)

    def get_all(self) -> list[Room]:
        """Get all rooms
        """
        return self.room_repo.get_all()

    def create_room(self, room: Room) -> Optional[Room]:
        """Create a room
        Args:
            room : all the data concerning the room
        """
        return self.room_repo.create_room(room)

    def update_room(self, room: Room) -> Optional[Room]:
        """Update a room
        Args:
            room : new data concerning the room
        """
        return self.room_repo.update_room(room)

    def delete_room(self, room_id: int) -> bool:
        """Delete a room
        Args:
            room_id : id of the room
        """
        return self.room_repo.delete_room(room_id)

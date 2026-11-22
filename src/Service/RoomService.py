from typing import Optional

from src.Business_object.Room import Room
from src.DAO.ReservationRepo import ReservationRepo
from src.DAO.RoomRepo import RoomRepo


class RoomService:
    """Service that manages rooms."""

    def __init__(
        self,
        room_repo: Optional[RoomRepo] = None,
        reservation_repo: Optional[ReservationRepo] = None,
    ):
        """Create the service.
        Args:
            room_repo (RoomRepo, optional): Access to the rooms in the database.
                If none is given, a new RoomRepo is created.
            reservation_repo (ReservationRepo, optional): Access to the reservations, only used before
                deleting a room. If none is given, a new ReservationRepo is created when it is needed.
        """
        # Access to our own database (table room)
        self.room_repo = room_repo or RoomRepo()
        # Access to the reservations (to protect the sales before a deletion)
        self.reservation_repo = reservation_repo

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

    def check_room(self, room: Room) -> None:
        """Check the data of a room before saving it.
        The room is refused (ValueError) if its capacity is not greater than 0,
        or if its room number is already used by another room.
        Args:
            room (Room): The room to check. Its id is None for a new room.
        """
        # A room must have at least one seat
        if room.capacity <= 0:
            raise ValueError("The capacity must be greater than 0")

        # Two rooms cannot have the same number
        # (when we update a room, it can keep its own number)
        room_with_same_number = self.room_repo.get_by_number(room.room_number)
        if room_with_same_number is not None and room_with_same_number.id != room.id:
            raise ValueError(f"Room number [{room.room_number}] is already used")

    def create_room(self, room: Room) -> Optional[Room]:
        """Create a room. It is refused if its capacity is not greater than 0
        or if its room number is already used.
        Args:
            room (Room): The room to save (room number and capacity).
        Returns:
            The saved Room, with its id.
        """
        self.check_room(room)
        return self.room_repo.create_room(room)

    def update_room(self, room: Room) -> Optional[Room]:
        """Update the room number and the capacity of a room. It is refused if the new capacity
        is not greater than 0 or if the new room number is already used by another room.
        Args:
            room (Room): The room with its new data. Its id identifies the one to update.
        Returns:
            The updated Room, or None if no room has this id.
        """
        self.check_room(room)
        return self.room_repo.update_room(room)

    def delete_room(self, room_id: int) -> bool:
        """Delete a room where no ticket was sold. Its screenings are deleted too.
        A room with tickets sold cannot be deleted: its reservations would be deleted too
        (ON DELETE CASCADE), so the sales would disappear from the accounting.
        Args:
            room_id (int): The database id of the room to delete.
        Returns:
            True if the room was deleted, False if no room has this id.
        Raises:
            ValueError if tickets were already sold for a screening of this room.
        """
        # Refuse the deletion if at least one ticket was sold in this room
        reservation_repo = self.reservation_repo or ReservationRepo()
        tickets_sold = reservation_repo.count_room_reservations(room_id)
        if tickets_sold > 0:
            raise ValueError(f"{tickets_sold} ticket(s) already sold in this room, it cannot be deleted")

        return self.room_repo.delete_room(room_id)

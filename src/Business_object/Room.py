from typing import Optional


class Room:
    """A room of the cinema, with its number and its capacity (number of seats)."""

    def __init__(self, room_number: int, capacity: int, id: Optional[int] = None):
        self.id = id
        self.room_number = room_number
        self.capacity = capacity

    def __str__(self) -> str:
        return f"Room {self.room_number} (Capacity: {self.capacity}, ID: {self.id})"

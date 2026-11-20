from pydantic import BaseModel


class RoomModel(BaseModel):
    """Body of the request to create or update a room."""

    room_number: int
    capacity: int

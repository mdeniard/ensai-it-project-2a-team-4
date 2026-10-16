from pydantic import BaseModel


class RoomModel(BaseModel):
    room_number: int
    capacity: int

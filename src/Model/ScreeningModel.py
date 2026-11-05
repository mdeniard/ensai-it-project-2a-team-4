from datetime import datetime
from zoneinfo import ZoneInfo

from pydantic import BaseModel, ConfigDict, field_validator

LOCAL_TZ = ZoneInfo("Europe/Paris")

class ScreeningModel(BaseModel):
    model_config = ConfigDict(json_schema_extra={
        "example": {"movie_id": 1, "room_id": 1, "start_time": "2026-11-05T20:00:00", "base_price": 10.0}
    })
    movie_id: int
    room_id: int
    start_time: datetime
    # Base price of a ticket for this screening (required: chosen by the administrator)
    base_price: float

    @field_validator("start_time")
    @classmethod
    def to_local_tz(cls, v: datetime) -> datetime:
        if v.tzinfo is None:
            return v.replace(tzinfo=LOCAL_TZ)
        return v

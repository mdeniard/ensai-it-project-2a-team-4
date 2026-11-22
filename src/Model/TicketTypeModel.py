from pydantic import BaseModel, ConfigDict


class TicketTypeModel(BaseModel):
    """Body of the request to create or update a ticket type.
    The price paid by the customer = base price of the screening x price_multiplier.
    """

    model_config = ConfigDict(
        json_schema_extra={"example": {"name": "Senior", "price_multiplier": 0.7, "active": True}}
    )

    name: str
    price_multiplier: float
    # False to stop selling this ticket type (it is not offered anymore when booking)
    active: bool = True

from fastapi import APIRouter, Depends, HTTPException, status

from src.App.UserController import require_admin
from src.Business_object.TicketType import TicketType
from src.Model.TicketTypeModel import TicketTypeModel
from src.Service.TicketTypeService import TicketTypeService

ticket_type_router = APIRouter(prefix="/ticket-types", tags=["Ticket types"])

admin_ticket_type_router = APIRouter(
    prefix="/admin/ticket-types",
    tags=["Ticket types"],
    dependencies=[Depends(require_admin)],
)


# ---------- Public routes ----------


@ticket_type_router.get("/", summary="Get the ticket types available for booking", status_code=status.HTTP_200_OK)
def get_active_ticket_types():
    """
    List the active ticket types, read from the database.
    The customer uses the id of one of them as `ticket_type_id` in POST /reservations.
    """
    return TicketTypeService().get_active_ticket_types()


# ---------- Admin routes ----------


@admin_ticket_type_router.get("/", summary="List all the ticket types", status_code=status.HTTP_200_OK)
def get_all_ticket_types():
    """
    List all the ticket types, the inactive ones included (administrators only).
    """
    return TicketTypeService().get_all_ticket_types()


@admin_ticket_type_router.post("/", summary="Create a ticket type", status_code=status.HTTP_201_CREATED)
def create_ticket_type(t: TicketTypeModel):
    """
    Create a ticket type. The price paid by the customer = base price of the screening x price_multiplier.
    Refused (409) if the name is empty or already used, or if the price multiplier is not greater than 0.

    Args:

    * t: the name, the price_multiplier (for example 0.7 for 30 % off) and active (true by default)
    """
    try:
        return TicketTypeService().create_ticket_type(TicketType(t.name, t.price_multiplier, t.active))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e)) from e


@admin_ticket_type_router.put("/{ticket_type_id}", summary="Update a ticket type", status_code=status.HTTP_200_OK)
def update_ticket_type(ticket_type_id: int, t: TicketTypeModel):
    """
    Update a ticket type: its name, its price multiplier, or active (false to stop selling it).
    The tickets already sold keep the price they were paid.
    Refused (409) if the name is empty or used by another ticket type, or if the price multiplier is not greater than 0.

    Args:

    * ticket_type_id: the id of the ticket type
    * t: the new name, price_multiplier and active
    """
    service = TicketTypeService()
    if service.get_by_id(ticket_type_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Ticket type [{ticket_type_id}] not found")

    try:
        return service.update_ticket_type(TicketType(t.name, t.price_multiplier, t.active, id=ticket_type_id))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e)) from e


@admin_ticket_type_router.delete(
    "/{ticket_type_id}", summary="Delete a ticket type", status_code=status.HTTP_204_NO_CONTENT
)
def delete_ticket_type(ticket_type_id: int, confirm: bool = False) -> None:
    """
    Delete a ticket type that was never sold.
    Refused (409) if tickets were already sold with it: set it as not active instead (PUT).

    Args:

    * ticket_type_id: the id of the ticket type
    * confirm: must be true to confirm the deletion (default false, the request is then refused)
    """
    if not confirm:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Confirmation required: repeat the request with confirm=True",
        )

    try:
        is_deleted = TicketTypeService().delete_ticket_type(ticket_type_id)
    except ValueError as e:
        # Tickets were already sold with this ticket type
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e)) from e

    if not is_deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Ticket type [{ticket_type_id}] not found")

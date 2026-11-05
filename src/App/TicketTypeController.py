from fastapi import APIRouter, status

from src.Service.TicketTypeService import TicketTypeService

ticket_type_router = APIRouter(prefix="/ticket-types", tags=["Ticket types"])


@ticket_type_router.get("/", summary="Get the ticket types available for booking", status_code=status.HTTP_200_OK)
def get_active_ticket_types():
    """
    List the active ticket types, read from the database.
    The customer uses the id of one of them as `ticket_type_id` in POST /reservations.
    """
    return TicketTypeService().get_active_ticket_types()

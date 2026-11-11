from fastapi import APIRouter, Depends, HTTPException, status

from src.App.UserController import require_admin
from src.Business_object.Room import Room
from src.Model.RoomModel import RoomModel
from src.Service.RoomService import RoomService

room_router = APIRouter(prefix="/rooms", tags=["Rooms"])

admin_room_router = APIRouter(
    prefix="/admin/rooms",
    tags=["Rooms"],
    dependencies=[Depends(require_admin)],
)


# ---------- Public routes ----------

@room_router.get("/{id}", summary="Get room by id", status_code=status.HTTP_200_OK)
def get_room_by_id(id: int):
    """
    Get a room of the theater.

    Args:

    * id: the id of the room in our database (not its room number)
    """
    try:
        room = RoomService().get_by_id(id)
        return room
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail="Room with id [{}] not found".format(id),
        ) from e
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid request") from e

@room_router.get("/", summary="Get all room", status_code=status.HTTP_200_OK)
def get_all_rooms():
    """
    Get all the rooms of the theater, with their room number and capacity.
    """
    try:
        rooms = RoomService().get_all()
        return rooms
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid request") from e


# ---------- Admin routes ----------

@admin_room_router.post("/", summary="Create a room", status_code=status.HTTP_201_CREATED)
def create(
    r: RoomModel,
    ):
    """
    Create a room. The room number must be unique and the capacity must be greater than 0.

    Args:

    * r: the room_number and the capacity (number of seats) of the room
    """
    try:
        created_room = RoomService().create_room(
            Room(r.room_number, r.capacity)
        )
        return created_room
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error while creating room: {str(e)}"
        ) from e

@admin_room_router.put("/{id}", summary="Update a room", status_code=status.HTTP_200_OK)
def update_room(
    id: int,
    r: RoomModel,
    ):
    """
    Update the room number and the capacity of a room.

    Args:

    * id: the id of the room in our database
    * r: the new room_number and capacity of the room
    """
    try:
        existing_room = RoomService().get_by_id(id)
        if existing_room is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Room with id [{id}] not found"
            )

        existing_room.room_number = r.room_number
        existing_room.capacity = r.capacity

        updated_room = RoomService().update_room(existing_room)
        return updated_room

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid update request"
        ) from e


# --- Route de Suppression (DELETE) ---
@admin_room_router.delete("/{id}", summary="Delete a room", status_code=status.HTTP_204_NO_CONTENT)
def delete_room(
    id: int,
    confirm: bool = False,
    ):
    """
    Delete a room, with all its screenings and their reservations.

    Args:

    * id: the id of the room in our database
    * confirm: must be true to confirm the deletion (default false, the request is then refused)
    """
    if not confirm:
        raise HTTPException(
            status_code=409,
            detail="Confirmation required: repeat the request with confirm=True",
        )
    try:
        existing_room = RoomService().get_by_id(id)
        if existing_room is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Room with id [{id}] not found"
            )

        success = RoomService().delete_room(id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete room"
            )

        return None

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid request"
        ) from e
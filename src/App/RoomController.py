from typing import Optional

from fastapi import APIRouter, HTTPException, status

from src.Business_object.Room import Room
from src.Model.RoomModel import RoomModel
from src.Service.RoomService import RoomService

room_router = APIRouter(prefix="/rooms", tags=["Rooms"])


@room_router.get("/{id}", status_code=status.HTTP_200_OK)
def get_room_by_id(id: int):
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

@room_router.get("/", status_code=status.HTTP_200_OK)
def get_all_rooms():
    try:
        rooms = RoomService().get_all()
        return rooms
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid request") from e

@room_router.post("/", status_code=status.HTTP_201_CREATED)
def create(r: RoomModel):
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

@room_router.put("/{id}", status_code=status.HTTP_200_OK)
def update_room(id: int, r: RoomModel):
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
@room_router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_room(id: int, confirm: bool = False,):
    """
    Delete a room by its id and screenings related to this room
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
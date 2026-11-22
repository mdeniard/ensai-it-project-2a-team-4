"""Tests for RoomService using unittest.mock."""

from unittest.mock import Mock, patch

import pytest

from src.Business_object.Room import Room
from src.Service.RoomService import RoomService


class TestRoomService:
    """Test all public methods of RoomService against a mocked repository."""

    def setup_method(self):
        """Create a fresh mock repo and service before every test."""
        self.mock_repo = Mock()
        # By default, no ticket was sold in the room
        self.mock_reservation_repo = Mock()
        self.mock_reservation_repo.count_room_reservations.return_value = 0
        self.service = RoomService(room_repo=self.mock_repo, reservation_repo=self.mock_reservation_repo)

    # ---------- __init__ ----------

    def test_init_uses_provided_repo(self):
        """The service must use the repository it is given."""
        assert self.service.room_repo is self.mock_repo

    @patch("src.Service.RoomService.RoomRepo")
    def test_init_creates_repo_if_none_given(self, MockRoomRepo):
        """When no repo is provided, a new RoomRepo is instantiated."""
        service = RoomService()

        MockRoomRepo.assert_called_once()
        assert service.room_repo is MockRoomRepo.return_value

    # ---------- get_by_id ----------

    def test_get_by_id_returns_room_when_found(self):
        room = Room(120, 120, id=1)
        self.mock_repo.get_by_id.return_value = room

        result = self.service.get_by_id(1)

        self.mock_repo.get_by_id.assert_called_once_with(1)
        assert result == room

    def test_get_by_id_returns_none_when_not_found(self):
        self.mock_repo.get_by_id.return_value = None

        result = self.service.get_by_id(999)

        self.mock_repo.get_by_id.assert_called_once_with(999)
        assert result is None

    # ---------- get_by_number ----------

    def test_get_by_number_returns_room_when_found(self):
        room = Room(5, 80, id=3)
        self.mock_repo.get_by_number.return_value = room

        result = self.service.get_by_number(5)

        self.mock_repo.get_by_number.assert_called_once_with(5)
        assert result == room

    def test_get_by_number_returns_none_when_not_found(self):
        self.mock_repo.get_by_number.return_value = None

        result = self.service.get_by_number(999)

        self.mock_repo.get_by_number.assert_called_once_with(999)
        assert result is None

    # ---------- get_all ----------

    def test_get_all_returns_all_rooms(self):
        rooms = [
            Room(1, 120, id=1),
            Room(2, 90, id=2),
            Room(3, 60, id=3),
        ]
        self.mock_repo.get_all.return_value = rooms

        result = self.service.get_all()

        self.mock_repo.get_all.assert_called_once()
        assert result == rooms

    def test_get_all_returns_empty_list_when_no_rooms(self):
        self.mock_repo.get_all.return_value = []

        result = self.service.get_all()

        assert result == []

    # ---------- create_room ----------

    def test_create_room_returns_saved_room(self):
        new_room = Room(10, 50)
        saved_room = Room(10, 50, id=1)
        # No room has the number 10 yet
        self.mock_repo.get_by_number.return_value = None
        self.mock_repo.create_room.return_value = saved_room

        result = self.service.create_room(new_room)

        self.mock_repo.create_room.assert_called_once_with(new_room)
        assert result == saved_room

    def test_create_room_capacity_zero_is_refused(self):
        # GIVEN a room with 0 seats
        # WHEN we create it / THEN ValueError and nothing is saved
        with pytest.raises(ValueError, match="greater than 0"):
            self.service.create_room(Room(10, 0))
        self.mock_repo.create_room.assert_not_called()

    def test_create_room_number_already_used_is_refused(self):
        # GIVEN the room number 1 is already used
        self.mock_repo.get_by_number.return_value = Room(1, 120, id=1)

        # WHEN we create another room 1 / THEN ValueError and nothing is saved
        with pytest.raises(ValueError, match="already used"):
            self.service.create_room(Room(1, 50))
        self.mock_repo.create_room.assert_not_called()

    # ---------- update_room ----------

    def test_update_room_returns_updated_room(self):
        updated_room = Room(1, 150, id=1)
        # The only room with the number 1 is the room we update
        self.mock_repo.get_by_number.return_value = Room(1, 120, id=1)
        self.mock_repo.update_room.return_value = updated_room

        result = self.service.update_room(updated_room)

        self.mock_repo.update_room.assert_called_once_with(updated_room)
        assert result == updated_room

    def test_update_room_returns_none_when_not_found(self):
        self.mock_repo.get_by_number.return_value = None
        self.mock_repo.update_room.return_value = None

        result = self.service.update_room(Room(1, 150, id=999))

        assert result is None

    def test_update_room_number_used_by_another_room_is_refused(self):
        # GIVEN the room number 2 belongs to another room (id 2)
        self.mock_repo.get_by_number.return_value = Room(2, 90, id=2)

        # WHEN room 1 takes the number 2 / THEN ValueError and nothing is saved
        with pytest.raises(ValueError, match="already used"):
            self.service.update_room(Room(2, 150, id=1))
        self.mock_repo.update_room.assert_not_called()

    def test_update_room_capacity_negative_is_refused(self):
        # WHEN the new capacity is negative / THEN ValueError and nothing is saved
        with pytest.raises(ValueError, match="greater than 0"):
            self.service.update_room(Room(1, -5, id=1))
        self.mock_repo.update_room.assert_not_called()

    # ---------- delete_room ----------

    def test_delete_room_returns_true_when_deleted(self):
        self.mock_repo.delete_room.return_value = True

        result = self.service.delete_room(1)

        self.mock_repo.delete_room.assert_called_once_with(1)
        assert result is True

    def test_delete_room_with_tickets_sold_is_refused(self):
        # GIVEN 4 tickets were sold for screenings of room 1
        self.mock_reservation_repo.count_room_reservations.return_value = 4

        # WHEN we delete it / THEN ValueError and nothing is deleted
        with pytest.raises(ValueError, match="4 ticket"):
            self.service.delete_room(1)
        self.mock_repo.delete_room.assert_not_called()

    def test_delete_room_returns_false_when_not_found(self):
        self.mock_repo.delete_room.return_value = False

        result = self.service.delete_room(999)

        assert result is False

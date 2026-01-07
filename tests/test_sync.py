# MIT License
# Copyright (c) 2024-present Léo Colombaro

"""Tests for sync module."""

import unittest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

from birthdays365.config import Config
from birthdays365.sync import BirthdaySync


class TestBirthdaySync(unittest.IsolatedAsyncioTestCase):
    """Test cases for BirthdaySync class."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = Config(
            client_id="test-client-id",
            tenant_id="test-tenant-id",
            calendar_name="TestCalendar",
        )

    @patch("birthdays365.sync.GraphAuthenticator")
    @patch("birthdays365.sync.CalendarManager")
    @patch("birthdays365.sync.ContactManager")
    async def test_sync_create_new_events(
        self, mock_contact_mgr_class, mock_cal_mgr_class, mock_auth_class
    ):
        """Test syncing with new birthday events."""
        # Mock authenticator
        mock_auth = MagicMock()
        mock_graph_client = MagicMock()
        mock_auth.get_client.return_value = mock_graph_client
        mock_auth_class.return_value = mock_auth

        # Mock calendar manager
        mock_cal_mgr = MagicMock()
        mock_cal_mgr.get_or_create_calendar = AsyncMock(return_value="calendar-123")
        mock_cal_mgr.get_existing_birthday_events = AsyncMock(return_value={})
        mock_cal_mgr.create_birthday_event = AsyncMock(return_value=True)
        mock_cal_mgr_class.return_value = mock_cal_mgr

        # Mock contact manager
        mock_contact_mgr = MagicMock()
        mock_contact_mgr.get_contacts_with_birthdays = AsyncMock(
            return_value=[
                {
                    "id": "contact-1",
                    "name": "John Doe",
                    "birthday": datetime(1990, 5, 15, tzinfo=timezone.utc),
                },
                {
                    "id": "contact-2",
                    "name": "Jane Smith",
                    "birthday": datetime(1985, 8, 20, tzinfo=timezone.utc),
                },
            ]
        )
        mock_contact_mgr_class.return_value = mock_contact_mgr

        # Execute sync
        sync = BirthdaySync(self.config)
        await sync.sync()

        # Verify calls
        mock_cal_mgr.get_or_create_calendar.assert_called_once()
        mock_cal_mgr.get_existing_birthday_events.assert_called_once_with(
            "calendar-123"
        )
        mock_contact_mgr.get_contacts_with_birthdays.assert_called_once()
        self.assertEqual(mock_cal_mgr.create_birthday_event.call_count, 2)

    @patch("birthdays365.sync.GraphAuthenticator")
    @patch("birthdays365.sync.CalendarManager")
    @patch("birthdays365.sync.ContactManager")
    async def test_sync_update_existing_events(
        self, mock_contact_mgr_class, mock_cal_mgr_class, mock_auth_class
    ):
        """Test syncing with existing events that need updating."""
        # Mock authenticator
        mock_auth = MagicMock()
        mock_graph_client = MagicMock()
        mock_auth.get_client.return_value = mock_graph_client
        mock_auth_class.return_value = mock_auth

        # Mock calendar manager with existing events
        mock_cal_mgr = MagicMock()
        mock_cal_mgr.get_or_create_calendar = AsyncMock(return_value="calendar-123")
        mock_cal_mgr.get_existing_birthday_events = AsyncMock(
            return_value={
                "John Doe": {
                    "id": "event-1",
                    "start": "2024-06-15",  # Different date
                }
            }
        )
        mock_cal_mgr.update_birthday_event = AsyncMock(return_value=True)
        mock_cal_mgr_class.return_value = mock_cal_mgr

        # Mock contact manager
        mock_contact_mgr = MagicMock()
        mock_contact_mgr.get_contacts_with_birthdays = AsyncMock(
            return_value=[
                {
                    "id": "contact-1",
                    "name": "John Doe",
                    "birthday": datetime(1990, 5, 15, tzinfo=timezone.utc),
                }
            ]
        )
        mock_contact_mgr_class.return_value = mock_contact_mgr

        # Execute sync
        sync = BirthdaySync(self.config)
        await sync.sync()

        # Verify update was called
        mock_cal_mgr.update_birthday_event.assert_called_once()

    @patch("birthdays365.sync.GraphAuthenticator")
    @patch("birthdays365.sync.CalendarManager")
    @patch("birthdays365.sync.ContactManager")
    async def test_sync_skip_up_to_date_events(
        self, mock_contact_mgr_class, mock_cal_mgr_class, mock_auth_class
    ):
        """Test syncing skips events that are already up to date."""
        # Mock authenticator
        mock_auth = MagicMock()
        mock_graph_client = MagicMock()
        mock_auth.get_client.return_value = mock_graph_client
        mock_auth_class.return_value = mock_auth

        # Mock calendar manager with existing events
        mock_cal_mgr = MagicMock()
        mock_cal_mgr.get_or_create_calendar = AsyncMock(return_value="calendar-123")
        mock_cal_mgr.get_existing_birthday_events = AsyncMock(
            return_value={
                "John Doe": {
                    "id": "event-1",
                    "start": "2024-05-15",  # Same date
                }
            }
        )
        mock_cal_mgr.update_birthday_event = AsyncMock(return_value=True)
        mock_cal_mgr.create_birthday_event = AsyncMock(return_value=True)
        mock_cal_mgr_class.return_value = mock_cal_mgr

        # Mock contact manager
        mock_contact_mgr = MagicMock()
        mock_contact_mgr.get_contacts_with_birthdays = AsyncMock(
            return_value=[
                {
                    "id": "contact-1",
                    "name": "John Doe",
                    "birthday": datetime(1990, 5, 15, tzinfo=timezone.utc),
                }
            ]
        )
        mock_contact_mgr_class.return_value = mock_contact_mgr

        # Execute sync
        sync = BirthdaySync(self.config)
        await sync.sync()

        # Verify no update or create was called
        mock_cal_mgr.update_birthday_event.assert_not_called()
        mock_cal_mgr.create_birthday_event.assert_not_called()


if __name__ == "__main__":
    unittest.main()

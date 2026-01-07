# MIT License
# Copyright (c) 2024-present Léo Colombaro

"""Tests for calendar module."""

import unittest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

from birthdays365.calendar import CalendarManager


class TestCalendarManager(unittest.IsolatedAsyncioTestCase):
    """Test cases for CalendarManager class."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_graph_client = MagicMock()
        self.calendar_manager = CalendarManager(
            self.mock_graph_client, "TestCalendar"
        )

    async def test_get_or_create_calendar_existing(self):
        """Test getting an existing calendar."""
        # Mock response with existing calendar
        mock_calendar = MagicMock()
        mock_calendar.name = "TestCalendar"
        mock_calendar.id = "calendar-123"

        mock_response = MagicMock()
        mock_response.value = [mock_calendar]

        self.mock_graph_client.me.calendars.get = AsyncMock(
            return_value=mock_response
        )

        calendar_id = await self.calendar_manager.get_or_create_calendar()

        self.assertEqual(calendar_id, "calendar-123")
        self.mock_graph_client.me.calendars.get.assert_called_once()

    async def test_get_or_create_calendar_create_new(self):
        """Test creating a new calendar when it doesn't exist."""
        # Mock response with no matching calendar
        mock_other_calendar = MagicMock()
        mock_other_calendar.name = "OtherCalendar"
        mock_other_calendar.id = "other-123"

        mock_response = MagicMock()
        mock_response.value = [mock_other_calendar]

        self.mock_graph_client.me.calendars.get = AsyncMock(
            return_value=mock_response
        )

        # Mock calendar creation
        mock_created = MagicMock()
        mock_created.id = "new-calendar-123"

        self.mock_graph_client.me.calendars.post = AsyncMock(
            return_value=mock_created
        )

        calendar_id = await self.calendar_manager.get_or_create_calendar()

        self.assertEqual(calendar_id, "new-calendar-123")
        self.mock_graph_client.me.calendars.post.assert_called_once()

    async def test_get_existing_birthday_events(self):
        """Test retrieving existing birthday events."""
        # Mock events with birthday category
        mock_event1 = MagicMock()
        mock_event1.subject = "John Doe"
        mock_event1.categories = ["Birthday"]
        mock_event1.id = "event-1"
        mock_event1.start = MagicMock()
        mock_event1.start.date_time = "2024-05-15"

        mock_event2 = MagicMock()
        mock_event2.subject = "Jane Smith"
        mock_event2.categories = ["Birthday"]
        mock_event2.id = "event-2"
        mock_event2.start = MagicMock()
        mock_event2.start.date_time = "2024-08-20"

        # Non-birthday event
        mock_event3 = MagicMock()
        mock_event3.subject = "Meeting"
        mock_event3.categories = ["Work"]
        mock_event3.id = "event-3"

        mock_response = MagicMock()
        mock_response.value = [mock_event1, mock_event2, mock_event3]

        mock_calendar = MagicMock()
        mock_calendar.events.get = AsyncMock(return_value=mock_response)
        self.mock_graph_client.me.calendars.by_calendar_id = MagicMock(
            return_value=mock_calendar
        )

        events = await self.calendar_manager.get_existing_birthday_events(
            "calendar-123"
        )

        self.assertEqual(len(events), 2)
        self.assertIn("John Doe", events)
        self.assertIn("Jane Smith", events)
        self.assertEqual(events["John Doe"]["id"], "event-1")
        self.assertEqual(events["Jane Smith"]["id"], "event-2")

    async def test_create_birthday_event(self):
        """Test creating a birthday event."""
        mock_calendar = MagicMock()
        mock_calendar.events.post = AsyncMock(return_value=MagicMock())
        self.mock_graph_client.me.calendars.by_calendar_id = MagicMock(
            return_value=mock_calendar
        )

        birthday = datetime(1990, 5, 15, tzinfo=timezone.utc)
        result = await self.calendar_manager.create_birthday_event(
            "calendar-123", "John Doe", birthday, "contact-456"
        )

        self.assertTrue(result)
        mock_calendar.events.post.assert_called_once()

        # Verify the event object passed to post
        call_args = mock_calendar.events.post.call_args
        event = call_args[0][0]

        self.assertEqual(event.subject, "John Doe")
        self.assertTrue(event.is_all_day)
        self.assertEqual(event.categories, ["Birthday"])
        self.assertIn("Age:", event.body.content)
        self.assertIn("Contact ID: contact-456", event.body.content)

    async def test_create_birthday_event_age_calculation(self):
        """Test age calculation in birthday event."""
        mock_calendar = MagicMock()
        mock_calendar.events.post = AsyncMock(return_value=MagicMock())
        self.mock_graph_client.me.calendars.by_calendar_id = MagicMock(
            return_value=mock_calendar
        )

        # Test with a birthday that already happened this year
        current_year = datetime.now(timezone.utc).year
        birthday = datetime(1990, 1, 1, tzinfo=timezone.utc)

        result = await self.calendar_manager.create_birthday_event(
            "calendar-123", "Test Person", birthday
        )

        self.assertTrue(result)

        # Verify age in description
        call_args = mock_calendar.events.post.call_args
        event = call_args[0][0]

        # Age should be calculated for next year since birthday already passed
        expected_age = (current_year + 1) - 1990
        self.assertIn(f"Age: {expected_age}", event.body.content)


if __name__ == "__main__":
    unittest.main()

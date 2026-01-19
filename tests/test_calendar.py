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
        self.calendar_manager = CalendarManager(self.mock_graph_client, "TestCalendar")

    async def test_get_or_create_calendar_existing(self):
        """Test getting an existing calendar."""
        # Mock response with existing calendar
        mock_calendar = MagicMock()
        mock_calendar.name = "TestCalendar"
        mock_calendar.id = "calendar-123"

        mock_response = MagicMock()
        mock_response.value = [mock_calendar]

        self.mock_graph_client.me.calendars.get = AsyncMock(return_value=mock_response)

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

        self.mock_graph_client.me.calendars.get = AsyncMock(return_value=mock_response)

        # Mock calendar creation
        mock_created = MagicMock()
        mock_created.id = "new-calendar-123"

        self.mock_graph_client.me.calendars.post = AsyncMock(return_value=mock_created)

        calendar_id = await self.calendar_manager.get_or_create_calendar()

        self.assertEqual(calendar_id, "new-calendar-123")
        self.mock_graph_client.me.calendars.post.assert_called_once()

    async def test_get_existing_birthday_events(self):
        """Test retrieving existing birthday events using calendar_view."""
        mock_event1 = MagicMock()
        mock_event1.subject = "John Doe"
        mock_event1.id = "event-1"
        mock_event1.start = MagicMock()
        mock_event1.start.date_time = "2024-05-15"

        mock_event2 = MagicMock()
        mock_event2.subject = "Jane Smith"
        mock_event2.id = "event-2"
        mock_event2.start = MagicMock()
        mock_event2.start.date_time = "2024-08-20"

        # Mock the first page response
        mock_response = MagicMock()
        mock_response.value = [mock_event1, mock_event2]
        mock_response.odata_next_link = None  # No pagination for this test

        # Mock the calendar_view
        mock_calendar_view = MagicMock()
        mock_calendar_view.get = AsyncMock(return_value=mock_response)

        mock_calendar = MagicMock()
        mock_calendar.calendar_view = mock_calendar_view
        self.mock_graph_client.me.calendars.by_calendar_id = MagicMock(
            return_value=mock_calendar
        )

        events = await self.calendar_manager.get_existing_birthday_events(
            "calendar-123"
        )

        self.assertEqual(2, len(events))
        self.assertIn(mock_event1, events)
        self.assertIn(mock_event2, events)

    async def test_get_existing_birthday_events_with_pagination(self):
        """Test retrieving existing birthday events with pagination."""
        # Create mock events for first page
        mock_event1 = MagicMock()
        mock_event1.subject = "John Doe"
        mock_event1.id = "event-1"

        mock_event2 = MagicMock()
        mock_event2.subject = "Jane Smith"
        mock_event2.id = "event-2"

        # Create mock events for second page
        mock_event3 = MagicMock()
        mock_event3.subject = "Bob Johnson"
        mock_event3.id = "event-3"

        # Mock the first page response with next link
        mock_response_page1 = MagicMock()
        mock_response_page1.value = [mock_event1, mock_event2]
        mock_response_page1.odata_next_link = "https://graph.microsoft.com/v1.0/next"

        # Mock the second page response
        mock_response_page2 = MagicMock()
        mock_response_page2.value = [mock_event3]
        mock_response_page2.odata_next_link = None  # No more pages

        # Mock the calendar_view to return different responses
        mock_calendar_view = MagicMock()

        # First call returns page 1
        first_call = True
        async def mock_get(*args, **kwargs):
            nonlocal first_call
            if first_call:
                first_call = False
                return mock_response_page1
            return mock_response_page2

        mock_calendar_view.get = AsyncMock(side_effect=mock_get)

        # Mock with_url to return the mock that will give page 2
        mock_next_page_view = MagicMock()
        mock_next_page_view.get = AsyncMock(return_value=mock_response_page2)
        mock_calendar_view.with_url = MagicMock(return_value=mock_next_page_view)

        mock_calendar = MagicMock()
        mock_calendar.calendar_view = mock_calendar_view
        self.mock_graph_client.me.calendars.by_calendar_id = MagicMock(
            return_value=mock_calendar
        )

        events = await self.calendar_manager.get_existing_birthday_events(
            "calendar-123"
        )

        self.assertEqual(3, len(events))
        self.assertIn(mock_event1, events)
        self.assertIn(mock_event2, events)
        self.assertIn(mock_event3, events)

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
        # Verify extended property for birthday icon is set
        self.assertIsNotNone(event.single_value_extended_properties)
        self.assertEqual(len(event.single_value_extended_properties), 1)
        self.assertEqual(event.single_value_extended_properties[0].id, "Integer {11000E07-B51B-40D6-AF21-CAA85EDAB1D0} Id 0x0027")
        self.assertEqual(event.single_value_extended_properties[0].value, "Cake")

if __name__ == "__main__":
    unittest.main()

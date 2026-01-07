# MIT License
# Copyright (c) 2024-present Léo Colombaro

"""Tests for contacts module."""

import unittest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

from birthdays365.contacts import ContactManager


class TestContactManager(unittest.IsolatedAsyncioTestCase):
    """Test cases for ContactManager class."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_graph_client = MagicMock()
        self.contact_manager = ContactManager(self.mock_graph_client)

    async def test_get_contacts_with_birthdays(self):
        """Test retrieving contacts with birthdays."""
        # Mock contacts with birthdays
        mock_contact1 = MagicMock()
        mock_contact1.id = "contact-1"
        mock_contact1.display_name = "John Doe"
        mock_contact1.birthday = datetime(1990, 5, 15, tzinfo=timezone.utc)

        mock_contact2 = MagicMock()
        mock_contact2.id = "contact-2"
        mock_contact2.display_name = "Jane Smith"
        mock_contact2.birthday = datetime(1985, 8, 20, tzinfo=timezone.utc)

        # Contact without birthday
        mock_contact3 = MagicMock()
        mock_contact3.id = "contact-3"
        mock_contact3.display_name = "No Birthday"
        mock_contact3.birthday = None

        mock_response = MagicMock()
        mock_response.value = [mock_contact1, mock_contact2, mock_contact3]

        self.mock_graph_client.me.contacts.get = AsyncMock(
            return_value=mock_response
        )

        contacts = await self.contact_manager.get_contacts_with_birthdays()

        self.assertEqual(len(contacts), 2)
        self.assertEqual(contacts[0]["id"], "contact-1")
        self.assertEqual(contacts[0]["name"], "John Doe")
        self.assertEqual(contacts[1]["id"], "contact-2")
        self.assertEqual(contacts[1]["name"], "Jane Smith")

    async def test_get_contacts_with_birthdays_empty(self):
        """Test retrieving contacts when none have birthdays."""
        mock_response = MagicMock()
        mock_response.value = []

        self.mock_graph_client.me.contacts.get = AsyncMock(
            return_value=mock_response
        )

        contacts = await self.contact_manager.get_contacts_with_birthdays()

        self.assertEqual(len(contacts), 0)

    async def test_get_contacts_with_birthdays_error(self):
        """Test error handling when retrieving contacts."""
        self.mock_graph_client.me.contacts.get = AsyncMock(
            side_effect=Exception("API Error")
        )

        contacts = await self.contact_manager.get_contacts_with_birthdays()

        # Should return empty list on error
        self.assertEqual(len(contacts), 0)


if __name__ == "__main__":
    unittest.main()

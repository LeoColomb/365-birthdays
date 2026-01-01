# MIT License
# Copyright (c) 2024-present Léo Colombaro

"""Main synchronization logic for birthdays365."""

from .auth import GraphAuthenticator
from .calendar import CalendarManager
from .config import Config
from .contacts import ContactManager


class BirthdaySync:
    """Orchestrates the birthday synchronization process."""

    def __init__(self, config: Config):
        """Initialize the sync manager.

        Args:
            config: Application configuration
        """
        self.config = config
        self.authenticator = GraphAuthenticator(config)
        self.graph_client = self.authenticator.get_client()
        self.calendar_manager = CalendarManager(self.graph_client, config.calendar_name)
        self.contact_manager = ContactManager(self.graph_client)

    async def sync(self) -> None:
        """Execute the birthday synchronization process."""
        print("Starting birthday sync...")

        # Get or create the birthday calendar
        calendar_id = await self.calendar_manager.get_or_create_calendar()
        if not calendar_id:
            print("Failed to get/create birthday calendar")
            return

        print(f"Using calendar: {self.config.calendar_name}")

        # Get existing birthday events to avoid duplicates
        existing_events = await self.calendar_manager.get_existing_birthday_events(
            calendar_id
        )
        if existing_events:
            print(f"Found {len(existing_events)} existing birthday events")

        # Get contacts with birthdays
        contacts = await self.contact_manager.get_contacts_with_birthdays()
        print(f"Found {len(contacts)} contacts with birthdays")

        # Create events for each birthday
        success_count = 0
        skipped_count = 0
        for contact in contacts:
            # Skip if event already exists
            if contact["name"] in existing_events:
                print(f"⊙ Skipped {contact['name']} (already exists)")
                skipped_count += 1
                continue

            if await self.calendar_manager.create_birthday_event(
                calendar_id, contact["name"], contact["birthday"]
            ):
                success_count += 1
                print(f"✓ Created event for {contact['name']}")
            else:
                print(f"✗ Failed to create event for {contact['name']}")

        print(
            f"\nSync complete: {success_count} created, {skipped_count} skipped, "
            f"{len(contacts)} total"
        )

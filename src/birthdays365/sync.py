# MIT License
# Copyright (c) 2024-present Léo Colombaro

"""Main synchronization logic for birthdays365."""

from datetime import datetime, timezone

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

        # Process each contact
        success_count = 0
        updated_count = 0
        skipped_count = 0
        for contact in contacts:
            contact_name = contact["name"]
            birthday = contact["birthday"]
            contact_id = contact.get("id")

            # Check if event already exists
            if contact_name in existing_events:
                # Get the existing event info
                event_info = existing_events[contact_name]
                existing_date = event_info.get("start")

                # Compare dates (month and day only)
                if birthday.tzinfo is None:
                    birthday = birthday.replace(tzinfo=timezone.utc)
                birthday_date = birthday.date()

                # Parse existing date if available
                needs_update = False
                if existing_date:
                    try:
                        # Parse the ISO date string
                        existing_date_obj = datetime.fromisoformat(
                            existing_date.replace("Z", "+00:00")
                        ).date()
                        # Compare month and day
                        if (
                            existing_date_obj.month != birthday_date.month
                            or existing_date_obj.day != birthday_date.day
                        ):
                            needs_update = True
                    except Exception:
                        # If we can't parse, assume update is needed
                        needs_update = True
                else:
                    # No date info, assume update is needed
                    needs_update = True

                if needs_update:
                    # Update the existing event
                    if await self.calendar_manager.update_birthday_event(
                        calendar_id, event_info["id"], contact_name, birthday, contact_id
                    ):
                        updated_count += 1
                        print(f"↻ Updated event for {contact_name}")
                    else:
                        print(f"✗ Failed to update event for {contact_name}")
                else:
                    print(f"⊙ Skipped {contact_name} (already up to date)")
                    skipped_count += 1
                continue

            # Create new event
            if await self.calendar_manager.create_birthday_event(
                calendar_id, contact_name, birthday, contact_id
            ):
                success_count += 1
                print(f"✓ Created event for {contact_name}")
            else:
                print(f"✗ Failed to create event for {contact_name}")

        print(
            f"\nSync complete: {success_count} created, {updated_count} updated, "
            f"{skipped_count} skipped, {len(contacts)} total"
        )

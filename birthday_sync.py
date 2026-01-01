#!/usr/bin/env python3
"""
365 Birthdays - Microsoft 365 Birthday Calendar Sync

This application reads contacts from Microsoft 365, extracts birthday information,
and creates/updates calendar events for those birthdays.
"""

import os
import sys
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from azure.identity import ClientSecretCredential
from msgraph import GraphServiceClient
from msgraph.generated.models.event import Event
from msgraph.generated.models.date_time_time_zone import DateTimeTimeZone
from msgraph.generated.models.item_body import ItemBody
from msgraph.generated.models.body_type import BodyType
from msgraph.generated.models.calendar import Calendar
from dotenv import load_dotenv


class BirthdayCalendarSync:
    """Syncs birthdays from contacts to a dedicated calendar."""

    def __init__(self):
        """Initialize the sync application with Microsoft Graph credentials."""
        load_dotenv()

        # Validate required environment variables
        self.client_id = os.getenv("CLIENT_ID")
        self.tenant_id = os.getenv("TENANT_ID")
        self.client_secret = os.getenv("CLIENT_SECRET")
        self.calendar_name = os.getenv("CALENDAR_NAME", "Birthdays")

        if not all([self.client_id, self.tenant_id, self.client_secret]):
            raise ValueError(
                "Missing required environment variables. "
                "Please set CLIENT_ID, TENANT_ID, and CLIENT_SECRET."
            )

        # Initialize Graph client
        credential = ClientSecretCredential(
            tenant_id=self.tenant_id,
            client_id=self.client_id,
            client_secret=self.client_secret,
        )
        self.graph_client = GraphServiceClient(credentials=credential)
        self.user_id = None

    async def get_authenticated_user(self) -> str:
        """Get the authenticated user's ID."""
        if self.user_id:
            return self.user_id

        # For app-only authentication, we need to specify which user to act as
        # This would typically come from configuration or command line
        # For now, we'll use 'me' which works with delegated permissions
        self.user_id = "me"
        return self.user_id

    async def get_or_create_birthday_calendar(self) -> Optional[str]:
        """Get the birthday calendar or create it if it doesn't exist."""
        user_id = await self.get_authenticated_user()

        try:
            # Get all calendars
            calendars = await self.graph_client.users.by_user_id(user_id).calendars.get()

            # Look for existing birthday calendar
            if calendars and calendars.value:
                for calendar in calendars.value:
                    if calendar.name == self.calendar_name:
                        return calendar.id

            # Create new birthday calendar
            new_calendar = Calendar()
            new_calendar.name = self.calendar_name

            created_calendar = await self.graph_client.users.by_user_id(
                user_id
            ).calendars.post(new_calendar)

            return created_calendar.id

        except Exception as e:
            print(f"Error accessing/creating calendar: {e}")
            return None

    async def get_contacts_with_birthdays(self) -> List[Dict]:
        """Retrieve all contacts that have a birthday set."""
        user_id = await self.get_authenticated_user()
        contacts_with_birthdays = []

        try:
            contacts = await self.graph_client.users.by_user_id(user_id).contacts.get()

            if contacts and contacts.value:
                for contact in contacts.value:
                    if contact.birthday:
                        contacts_with_birthdays.append(
                            {
                                "id": contact.id,
                                "name": contact.display_name,
                                "birthday": contact.birthday,
                            }
                        )

        except Exception as e:
            print(f"Error retrieving contacts: {e}")

        return contacts_with_birthdays

    async def create_birthday_event(
        self, calendar_id: str, contact_name: str, birthday: datetime
    ) -> bool:
        """Create a birthday event in the calendar."""
        user_id = await self.get_authenticated_user()

        try:
            # Create all-day event for the birthday
            # We use the current year for upcoming birthdays
            current_year = datetime.now().year
            event_date = birthday.replace(year=current_year)

            # If birthday already passed this year, schedule for next year
            if event_date < datetime.now():
                event_date = birthday.replace(year=current_year + 1)

            event = Event()
            event.subject = f"🎂 {contact_name}'s Birthday"
            event.is_all_day = True

            # Set start and end times
            start = DateTimeTimeZone()
            start.date_time = event_date.strftime("%Y-%m-%d")
            start.time_zone = "UTC"
            event.start = start

            end = DateTimeTimeZone()
            end.date_time = (event_date + timedelta(days=1)).strftime("%Y-%m-%d")
            end.time_zone = "UTC"
            event.end = end

            # Add description
            body = ItemBody()
            body.content_type = BodyType.Text
            body.content = f"Birthday of {contact_name}"
            event.body = body

            # Create the event
            await self.graph_client.users.by_user_id(user_id).calendars.by_calendar_id(
                calendar_id
            ).events.post(event)

            return True

        except Exception as e:
            print(f"Error creating birthday event for {contact_name}: {e}")
            return False

    async def sync_birthdays(self):
        """Main sync process: read contacts and create birthday events."""
        print("Starting birthday sync...")

        # Get or create the birthday calendar
        calendar_id = await self.get_or_create_birthday_calendar()
        if not calendar_id:
            print("Failed to get/create birthday calendar")
            return

        print(f"Using calendar: {self.calendar_name}")

        # Get contacts with birthdays
        contacts = await self.get_contacts_with_birthdays()
        print(f"Found {len(contacts)} contacts with birthdays")

        # Create events for each birthday
        success_count = 0
        for contact in contacts:
            if await self.create_birthday_event(
                calendar_id, contact["name"], contact["birthday"]
            ):
                success_count += 1
                print(f"✓ Created event for {contact['name']}")
            else:
                print(f"✗ Failed to create event for {contact['name']}")

        print(f"\nSync complete: {success_count}/{len(contacts)} events created")


async def main():
    """Main entry point for the application."""
    try:
        sync = BirthdayCalendarSync()
        await sync.sync_birthdays()
    except ValueError as e:
        print(f"Configuration error: {e}")
        print("\nPlease ensure you have:")
        print("1. Created a .env file based on .env.example")
        print("2. Registered an app in Microsoft Entra (Azure AD)")
        print("3. Granted the following API permissions:")
        print("   - Calendars.ReadWrite")
        print("   - Contacts.Read")
        print("   - User.Read")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())

# MIT License
# Copyright (c) 2024-present Léo Colombaro

"""Calendar operations for Microsoft Graph API."""

from datetime import datetime, timedelta, timezone

import sentry_sdk
from msgraph import GraphServiceClient
from msgraph.generated.models.body_type import BodyType
from msgraph.generated.models.calendar import Calendar
from msgraph.generated.models.date_time_time_zone import DateTimeTimeZone
from msgraph.generated.models.event import Event
from msgraph.generated.models.item_body import ItemBody
from msgraph.generated.models.patterned_recurrence import PatternedRecurrence
from msgraph.generated.models.recurrence_pattern import RecurrencePattern
from msgraph.generated.models.recurrence_pattern_type import RecurrencePatternType
from msgraph.generated.models.recurrence_range import RecurrenceRange
from msgraph.generated.models.recurrence_range_type import RecurrenceRangeType


class CalendarManager:
    """Manages calendar operations via Microsoft Graph API."""

    def __init__(
        self, graph_client: GraphServiceClient, calendar_name: str = "Birthdays"
    ):
        """Initialize the calendar manager.

        Args:
            graph_client: Authenticated GraphServiceClient instance
            calendar_name: Name of the calendar to use
        """
        self.graph_client = graph_client
        self.calendar_name = calendar_name

    async def get_or_create_calendar(self) -> str:
        """Get the birthday calendar or create it if it doesn't exist.

        Returns:
            Calendar ID if successful, None otherwise
        """
        try:
            # Get all calendars for the authenticated user
            calendars = await self.graph_client.me.calendars.get()
            # Look for existing birthday calendar
            if calendars and calendars.value:
                for calendar in calendars.value:
                    if calendar.name == self.calendar_name:
                        return calendar.id

            # Create new birthday calendar
            new_calendar = Calendar()
            new_calendar.name = self.calendar_name

            created_calendar = await self.graph_client.me.calendars.post(new_calendar)

            return created_calendar.id

        except Exception as e:
            sentry_sdk.capture_exception(e)
            raise Exception(f"Unable to access or create the calendar: {e}")

    async def get_existing_birthday_events(
        self, calendar_id: str
    ) -> dict[str, dict[str, str]]:
        """Get existing birthday events to avoid duplicates.

        Args:
            calendar_id: ID of the calendar to check

        Returns:
            Dictionary mapping contact names to event info (id and date)
        """
        existing_events = {}

        try:
            events = await self.graph_client.me.calendars.by_calendar_id(
                calendar_id
            ).events.get()

            if events and events.value:
                for event in events.value:
                    # Check if this is a birthday event by checking categories
                    if event.categories and "Birthday" in event.categories:
                        # Subject is just the contact name
                        existing_events[event.subject] = {
                            "id": event.id,
                            "start": (event.start.date_time if event.start else None),
                        }

        except Exception as e:
            sentry_sdk.capture_exception(e)
            raise Exception(f"Could not check existing events: {e}")

        return existing_events

    async def create_birthday_event(
        self,
        calendar_id: str,
        contact_name: str,
        birthday: datetime,
        contact_id: str,
    ) -> bool:
        """Create a birthday event in the calendar with a reminder and recurrence.

        Args:
            calendar_id: ID of the calendar
            contact_name: Name of the contact
            birthday: Birthday date of the contact
            contact_id: ID of the contact

        Returns:
            True if event was created successfully, False otherwise
        """
        try:
            # Create all-day event for the birthday
            # We use the current year for upcoming birthdays
            current_date = datetime.now(timezone.utc).date()
            current_year = current_date.year

            # Extract just the date part of the birthday
            if birthday.tzinfo is None:
                birthday = birthday.replace(tzinfo=timezone.utc)

            birthday_date = birthday.date()
            event_date = birthday_date.replace(year=current_year)

            # If birthday already passed this year (comparing dates only), schedule for next year
            if event_date < current_date:
                event_date = birthday_date.replace(year=current_year + 1)

            # Calculate age
            age = event_date.year - birthday_date.year

            event = Event()
            event.subject = contact_name
            event.is_all_day = True
            event.categories = ["Birthday"]

            # Set start and end dates (all-day events use date format without time)
            start = DateTimeTimeZone()
            start.date_time = event_date.isoformat()
            start.time_zone = "UTC"
            event.start = start

            end = DateTimeTimeZone()
            end_date = event_date + timedelta(days=1)
            end.date_time = end_date.isoformat()
            end.time_zone = "UTC"
            event.end = end

            # Add description with age and contact ID
            body = ItemBody()
            body.content_type = BodyType.Text
            body.content = f"Age: {age}\nContact ID: {contact_id}"
            event.body = body

            # Add reminder at event start
            event.is_reminder_on = True
            event.reminder_minutes_before_start = 0  # Reminder at event start

            # Add yearly recurrence pattern
            pattern = RecurrencePattern()
            pattern.type = RecurrencePatternType.AbsoluteYearly
            pattern.day_of_month = birthday_date.day
            pattern.month = birthday_date.month
            pattern.interval = 1

            recurrence_range = RecurrenceRange()
            recurrence_range.type = RecurrenceRangeType.NoEnd
            recurrence_range.start_date = event_date

            recurrence = PatternedRecurrence()
            recurrence.pattern = pattern
            recurrence.range = recurrence_range

            event.recurrence = recurrence

            # Create the event
            await self.graph_client.me.calendars.by_calendar_id(
                calendar_id
            ).events.post(event)

            return True

        except Exception as e:
            sentry_sdk.capture_exception(e)
            print(f"Error creating birthday event for {contact_name}: {e}")
            return False

    async def update_birthday_event(
        self,
        calendar_id: str,
        event_id: str,
        contact_name: str,
        birthday: datetime,
        contact_id: str,
    ) -> bool:
        """Update an existing birthday event if the date has changed.

        Args:
            calendar_id: ID of the calendar
            event_id: ID of the existing event
            contact_name: Name of the contact
            birthday: Birthday date of the contact
            contact_id: ID of the contact

        Returns:
            True if event was updated successfully, False otherwise
        """
        try:
            # Calculate the new event date
            current_date = datetime.now(timezone.utc).date()
            current_year = current_date.year

            if birthday.tzinfo is None:
                birthday = birthday.replace(tzinfo=timezone.utc)

            birthday_date = birthday.date()
            event_date = birthday_date.replace(year=current_year)

            # If birthday already passed this year, schedule for next year
            if event_date < current_date:
                event_date = birthday_date.replace(year=current_year + 1)

            # Calculate age
            age = event_date.year - birthday_date.year

            # Create updated event object
            event = Event()
            event.start = DateTimeTimeZone()
            event.start.date_time = event_date.isoformat()
            event.start.time_zone = "UTC"

            event.end = DateTimeTimeZone()
            end_date = event_date + timedelta(days=1)
            event.end.date_time = end_date.isoformat()
            event.end.time_zone = "UTC"

            # Update recurrence pattern
            pattern = RecurrencePattern()
            pattern.type = RecurrencePatternType.AbsoluteYearly
            pattern.day_of_month = birthday_date.day
            pattern.month = birthday_date.month
            pattern.interval = 1

            recurrence_range = RecurrenceRange()
            recurrence_range.type = RecurrenceRangeType.NoEnd
            recurrence_range.start_date = birthday_date

            recurrence = PatternedRecurrence()
            recurrence.pattern = pattern
            recurrence.range = recurrence_range

            event.recurrence = recurrence

            # Update description with age and contact ID
            body = ItemBody()
            body.content_type = BodyType.Text
            body.content = f"Age: {age}\nContact ID: {contact_id}"
            event.body = body

            # Update the event
            await (
                self.graph_client.me.calendars.by_calendar_id(calendar_id)
                .events.by_event_id(event_id)
                .patch(event)
            )

            return True

        except Exception as e:
            sentry_sdk.capture_exception(e)
            print(f"Error updating birthday event for {contact_name}: {e}")
            return False

# MIT License
# Copyright (c) 2024-present Léo Colombaro

"""Calendar operations for Microsoft Graph API."""

from datetime import datetime, timedelta, timezone

import sentry_sdk
from msgraph import GraphServiceClient
from msgraph.generated.models.calendar import Calendar
from msgraph.generated.models.date_time_time_zone import DateTimeTimeZone
from msgraph.generated.models.event import Event
from msgraph.generated.models.free_busy_status import FreeBusyStatus
from msgraph.generated.models.patterned_recurrence import PatternedRecurrence
from msgraph.generated.models.recurrence_pattern import RecurrencePattern
from msgraph.generated.models.recurrence_pattern_type import RecurrencePatternType
from msgraph.generated.models.recurrence_range import RecurrenceRange
from msgraph.generated.models.recurrence_range_type import RecurrenceRangeType
from msgraph.generated.models.single_value_legacy_extended_property import (
    SingleValueLegacyExtendedProperty,
)


class CalendarManager:
    """Manages calendar operations via Microsoft Graph API."""

    def __init__(
        self,
        graph_client: GraphServiceClient,
        calendar_name: str = "Birthdays",
        target_user_upn: str | None = None,
    ):
        """Initialize the calendar manager.

        Args:
            graph_client: Authenticated GraphServiceClient instance
            calendar_name: Name of the calendar to use
            target_user_upn: Optional user UPN for application permissions (uses /me if not provided)
        """
        self.graph_client = graph_client
        self.calendar_name = calendar_name
        self.target_user_upn = target_user_upn

    async def get_or_create_calendar(self) -> str:
        """Get the birthday calendar or create it if it doesn't exist.

        Returns:
            Calendar ID if successful, None otherwise
        """
        try:
            # Get all calendars for the authenticated user or target user
            if self.target_user_upn:
                calendars = await self.graph_client.users.by_user_id(
                    self.target_user_upn
                ).calendars.get()
            else:
                calendars = await self.graph_client.me.calendars.get()

            # Look for existing birthday calendar
            if calendars and calendars.value:
                for calendar in calendars.value:
                    if calendar.name == self.calendar_name:
                        return calendar.id

            # Create new birthday calendar
            new_calendar = Calendar()
            new_calendar.name = self.calendar_name
            new_calendar.can_edit = False
            new_calendar.is_removable = False
            new_calendar.is_tallying_responses = False

            icon_property = SingleValueLegacyExtendedProperty()
            icon_property.id = "Integer {11000E07-B51B-40D6-AF21-CAA85EDAB1D0} Id 0x0027"
            icon_property.value = "Cake"
            new_calendar.single_value_extended_properties = [icon_property]

            if self.target_user_upn:
                created_calendar = await self.graph_client.users.by_user_id(
                    self.target_user_upn
                ).calendars.post(new_calendar)
            else:
                created_calendar = await self.graph_client.me.calendars.post(
                    new_calendar
                )

            return created_calendar.id

        except Exception as e:
            sentry_sdk.capture_exception(e)
            raise Exception(f"Unable to access or create the calendar: {e}") from e

    async def get_existing_birthday_events(
        self, calendar_id: str
    ) -> list[Event]:
        """Get existing birthday events to avoid duplicates.

        Args:
            calendar_id: ID of the calendar to check

        Returns:
            List of Event objects
        """
        events = {}

        try:
            if self.target_user_upn:
                events = (
                    await self.graph_client.users.by_user_id(self.target_user_upn)
                    .calendars.by_calendar_id(calendar_id)
                    .events.get()
                )
            else:
                events = await self.graph_client.me.calendars.by_calendar_id(
                    calendar_id
                ).events.get()

        except Exception as e:
            sentry_sdk.capture_exception(e)
            raise Exception(f"Could not check existing events: {e}") from e

        return events

    def _prepare_event_data(
        self, contact_name: str, birthday: datetime, event: Event | None = None
    ) -> Event:
        """Prepare event data for birthday event creation or update.

        Args:
            contact_name: Name of the contact
            birthday: Birthday date of the contact

        Returns:
            Event object
        """
        # Calculate the event date
        current_date = datetime.now(timezone.utc).date()
        current_year = current_date.year

        # Extract just the date part of the birthday
        if birthday.tzinfo is None:
            birthday = birthday.replace(tzinfo=timezone.utc)

        birthday_date = birthday.date()
        event_date = birthday_date.replace(year=current_year)

        # If birthday already passed this year, schedule for next year
        if event_date < current_date:
            event_date = birthday_date.replace(year=current_year + 1)

        # Create event object
        if event is None:
            event = Event()
        event.subject = contact_name
        event.is_all_day = True
        event.show_as = FreeBusyStatus.Free

        # Add extended property for birthday icon (cake icon)
        # Using MAPI property for icon index
        icon_property = SingleValueLegacyExtendedProperty()
        icon_property.id = "Integer {11000E07-B51B-40D6-AF21-CAA85EDAB1D0} Id 0x0027"
        icon_property.value = "Cake"
        event.single_value_extended_properties = [icon_property]

        # Set start and end dates
        start = DateTimeTimeZone()
        start.date_time = event_date.isoformat()
        start.time_zone = "UTC"
        event.start = start

        end = DateTimeTimeZone()
        end_date = event_date + timedelta(days=1)
        end.date_time = end_date.isoformat()
        end.time_zone = "UTC"
        event.end = end

        # Add reminder at event start
        event.is_reminder_on = True
        event.reminder_minutes_before_start = -60 * 12

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

        return event

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
            event = self._prepare_event_data(contact_name, birthday)

            # Create the event
            if self.target_user_upn:
                await (
                    self.graph_client.users.by_user_id(self.target_user_upn)
                    .calendars.by_calendar_id(calendar_id)
                    .events.post(event)
                )
            else:
                await self.graph_client.me.calendars.by_calendar_id(
                    calendar_id
                ).events.post(event)

            return True

        except Exception as e:
            sentry_sdk.capture_exception(e)
            print("Error creating birthday event")
            return False

    async def update_birthday_event(
        self,
        calendar_id: str,
        event: Event,
        contact_name: str,
        birthday: datetime,
        contact_id: str,
    ) -> bool:
        """Update an existing birthday event if the date has changed.

        Args:
            calendar_id: ID of the calendar
            event: Existing event
            contact_name: Name of the contact
            birthday: Birthday date of the contact
            contact_id: ID of the contact

        Returns:
            True if event was updated successfully, False otherwise
        """
        try:
            event = self._prepare_event_data(contact_name, birthday, event)

            # Update the event
            if self.target_user_upn:
                await (
                    self.graph_client.users.by_user_id(self.target_user_upn)
                    .calendars.by_calendar_id(calendar_id)
                    .events.by_event_id(event_id)
                    .patch(event)
                )
            else:
                await (
                    self.graph_client.me.calendars.by_calendar_id(calendar_id)
                    .events.by_event_id(event_id)
                    .patch(event)
                )

            return True

        except Exception as e:
            sentry_sdk.capture_exception(e)
            print("Error updating birthday event")
            return False

# MIT License
# Copyright (c) 2024-present Léo Colombaro

"""365 Birthdays - Microsoft 365 Birthday Calendar Sync.

This package provides functionality to sync birthdays from Microsoft 365 contacts
to a dedicated calendar with reminders.
"""

__version__ = "0.1.0"

from .auth import GraphAuthenticator
from .calendar import CalendarManager
from .config import Config
from .contacts import ContactManager
from .sync import BirthdaySync

__all__ = [
    "GraphAuthenticator",
    "CalendarManager",
    "Config",
    "ContactManager",
    "BirthdaySync",
]


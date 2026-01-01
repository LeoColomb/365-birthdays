# MIT License
# Copyright (c) 2024-present Léo Colombaro

"""Command-line interface for birthdays365."""

import asyncio
import sys

from .config import Config
from .sync import BirthdaySync


def main() -> None:
    """Main entry point for the CLI application."""
    try:
        config = Config.from_env()
        sync = BirthdaySync(config)
        asyncio.run(sync.sync())
    except ValueError as e:
        print(f"Configuration error: {e}")
        print("\nPlease ensure you have:")
        print("1. Created a .env file based on .env.example")
        print("2. Registered an app in Microsoft Entra (Azure AD)")
        print("3. Granted the following API permissions:")
        print("   - Calendars.ReadWrite (Delegated)")
        print("   - Contacts.Read (Delegated)")
        print("   - User.Read (Delegated)")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

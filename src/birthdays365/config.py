# MIT License
# Copyright (c) 2024-present Léo Colombaro

"""Configuration management for birthdays365."""

import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass
class Config:
    """Application configuration."""

    client_id: str
    tenant_id: str
    calendar_name: str = "Birthdays"

    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables."""
        load_dotenv()

        client_id = os.getenv("CLIENT_ID")
        tenant_id = os.getenv("TENANT_ID")
        calendar_name = os.getenv("CALENDAR_NAME", "Birthdays")

        if not client_id or not tenant_id:
            raise ValueError(
                "Missing required environment variables. "
                "Please set CLIENT_ID and TENANT_ID."
            )

        return cls(
            client_id=client_id,
            tenant_id=tenant_id,
            calendar_name=calendar_name,
        )

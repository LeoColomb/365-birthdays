# MIT License
# Copyright (c) 2024-present Léo Colombaro

"""Authentication handling for Microsoft Graph API."""

from azure.identity import DeviceCodeCredential
from msgraph import GraphServiceClient

from .config import Config


class GraphAuthenticator:
    """Handles authentication with Microsoft Graph API."""

    SCOPES = ["Calendars.ReadWrite", "Contacts.Read", "User.Read"]

    def __init__(self, config: Config):
        """Initialize the authenticator.

        Args:
            config: Application configuration
        """
        self.config = config
        self._client = None

    def get_client(self) -> GraphServiceClient:
        """Get or create authenticated Graph client.

        Returns:
            Authenticated GraphServiceClient instance
        """
        if self._client is None:
            print(f"Logging-in...")
            credential = DeviceCodeCredential(
                client_id=self.config.client_id,
                tenant_id=self.config.tenant_id,
            )
            self._client = GraphServiceClient(
                credentials=credential, scopes=self.SCOPES
            )
            print(f"✓ Logged-in with MS Graph")

        return self._client

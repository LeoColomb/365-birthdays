# MIT License
# Copyright (c) 2024-present Léo Colombaro

"""Authentication handling for Microsoft Graph API."""

from azure.identity import ClientSecretCredential, DeviceCodeCredential
from msgraph import GraphServiceClient

from .config import Config


class GraphAuthenticator:
    """Handles authentication with Microsoft Graph API."""

    # Use .default scope which includes all delegated permissions granted in app registration
    SCOPES = ["https://graph.microsoft.com/.default"]

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
            print("Logging-in...")

            # Use client secret credential for non-interactive auth (e.g., GitHub Actions)
            if self.config.client_secret:
                print("Using client secret authentication...")
                credential = ClientSecretCredential(
                    client_id=self.config.client_id,
                    client_secret=self.config.client_secret,
                    tenant_id=self.config.tenant_id,
                )
            else:
                # Fall back to device code flow for interactive auth
                print("Using device code authentication...")
                credential = DeviceCodeCredential(
                    client_id=self.config.client_id,
                    tenant_id=self.config.tenant_id,
                )

            self._client = GraphServiceClient(
                credentials=credential, scopes=self.SCOPES
            )
            print("✓ Logged-in with MS Graph")

        return self._client

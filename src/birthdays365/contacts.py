# MIT License
# Copyright (c) 2024-present Léo Colombaro

"""Contact operations for Microsoft Graph API."""


import sentry_sdk
from msgraph import GraphServiceClient


class ContactManager:
    """Manages contact operations via Microsoft Graph API."""

    def __init__(self, graph_client: GraphServiceClient, target_user_upn: str | None = None):
        """Initialize the contact manager.

        Args:
            graph_client: Authenticated GraphServiceClient instance
            target_user_upn: Optional user UPN for application permissions (uses /me if not provided)
        """
        self.graph_client = graph_client
        self.target_user_upn = target_user_upn

    async def get_contacts_with_birthdays(self) -> list[dict]:
        """Retrieve all contacts that have a birthday set.

        Returns:
            List of dictionaries containing contact id, name, and birthday
        """
        contacts_with_birthdays = []

        try:
            # Use user-specific endpoint if target_user_upn is provided, otherwise use /me
            if self.target_user_upn:
                contacts = await self.graph_client.users.by_user_id(self.target_user_upn).contacts.get()
            else:
                contacts = await self.graph_client.me.contacts.get()

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
            sentry_sdk.capture_exception(e)
            print(f"Error retrieving contacts: {e}")

        return contacts_with_birthdays

# MIT License
# Copyright (c) 2024-present Léo Colombaro

"""Contact operations for Microsoft Graph API."""

import sentry_sdk
from msgraph import GraphServiceClient


class ContactManager:
    """Manages contact operations via Microsoft Graph API."""

    def __init__(
        self, graph_client: GraphServiceClient, target_user_upn: str | None = None
    ):
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
                request_builder = self.graph_client.users.by_user_id(
                    self.target_user_upn
                ).contacts
            else:
                request_builder = self.graph_client.me.contacts

            # Fetch all pages of contacts
            contacts_response = await request_builder.get()

            while contacts_response:
                if contacts_response.value:
                    for contact in contacts_response.value:
                        if contact.birthday:
                            contacts_with_birthdays.append(
                                {
                                    "id": contact.id,
                                    "name": contact.display_name,
                                    "birthday": contact.birthday,
                                }
                            )

                # Check if there's a next page
                if (
                    contacts_response.odata_next_link
                    and hasattr(request_builder, "with_url")
                ):
                    # Get next page
                    request_builder = request_builder.with_url(
                        contacts_response.odata_next_link
                    )
                    contacts_response = await request_builder.get()
                else:
                    # No more pages
                    break

        except Exception as e:
            sentry_sdk.capture_exception(e)
            print(f"Error retrieving contacts: {e}")

        return contacts_with_birthdays

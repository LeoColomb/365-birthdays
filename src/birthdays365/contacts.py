# MIT License
# Copyright (c) 2024-present Léo Colombaro

"""Contact operations for Microsoft Graph API."""

from typing import Dict, List

from msgraph import GraphServiceClient


class ContactManager:
    """Manages contact operations via Microsoft Graph API."""

    def __init__(self, graph_client: GraphServiceClient):
        """Initialize the contact manager.

        Args:
            graph_client: Authenticated GraphServiceClient instance
        """
        self.graph_client = graph_client

    async def get_contacts_with_birthdays(self) -> List[Dict]:
        """Retrieve all contacts that have a birthday set.

        Returns:
            List of dictionaries containing contact id, name, and birthday
        """
        contacts_with_birthdays = []

        try:
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
            print(f"Error retrieving contacts: {e}")

        return contacts_with_birthdays

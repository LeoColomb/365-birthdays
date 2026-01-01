# 365 Birthdays

> 🎂 Microsoft 365 Birthday Calendar Sync

Automatically sync birthdays from your Microsoft 365 contacts to a dedicated calendar.

## About

This Python application uses the Microsoft Graph API to:
- Read contacts from your Microsoft 365 address book
- Extract birthday information from contacts
- Create and maintain a dedicated "Birthdays" calendar
- Generate calendar events for each contact's birthday

## Prerequisites

- Python 3.8 or higher
- A Microsoft 365 account
- Access to Microsoft Entra admin center (formerly Azure AD) for app registration

## Setup

### 1. Register Application in Microsoft Entra

1. Go to the [Microsoft Entra admin center](https://entra.microsoft.com/)
2. Navigate to **Applications** > **App registrations**
3. Click **New registration**
4. Configure your app:
   - **Name**: 365 Birthdays Sync
   - **Supported account types**: Accounts in this organizational directory only (Single tenant)
   - **Redirect URI**: Leave empty for now
5. Click **Register**

### 2. Configure API Permissions

1. In your app registration, go to **API permissions**
2. Click **Add a permission**
3. Select **Microsoft Graph** > **Delegated permissions**
4. Add the following permissions:
   - `Calendars.ReadWrite` - Create and manage calendar events
   - `Contacts.Read` - Read user contacts
   - `User.Read` - Sign in and read user profile
5. Click **Add permissions**
6. Click **Grant admin consent** (requires admin privileges)

### 3. Create Client Secret

1. Go to **Certificates & secrets**
2. Click **New client secret**
3. Add a description (e.g., "Birthday Sync Secret")
4. Select an expiration period
5. Click **Add**
6. **Important**: Copy the secret value immediately (you won't be able to see it again)

### 4. Configure Environment Variables

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and fill in your values:
   - `CLIENT_ID`: Application (client) ID from your app registration
   - `TENANT_ID`: Directory (tenant) ID from your app registration
   - `CLIENT_SECRET`: The client secret value you created
   - `CALENDAR_NAME`: (Optional) Name of the calendar to create/use (default: "Birthdays")

### 5. Install Dependencies

```bash
pip install -r requirements.txt
```

## Usage

Run the birthday sync:

```bash
python birthday_sync.py
```

The application will:
1. Authenticate with Microsoft Graph using your app credentials
2. Create a "Birthdays" calendar if it doesn't exist
3. Read all contacts with birthday information
4. Create calendar events for each birthday

## Features

- ✅ Automatic calendar creation
- ✅ All-day birthday events
- ✅ Configurable calendar name
- ✅ Secure credential management via environment variables
- ✅ Uses official Microsoft Graph SDK for Python

## Security Considerations

- Never commit your `.env` file to version control
- Client secrets should be rotated regularly
- Use Azure Key Vault for production deployments
- Apply principle of least privilege for API permissions

## Troubleshooting

### Authentication Errors

If you encounter authentication errors:
1. Verify your `CLIENT_ID`, `TENANT_ID`, and `CLIENT_SECRET` are correct
2. Ensure admin consent was granted for the API permissions
3. Check that your client secret hasn't expired

### Permission Errors

If you get permission-related errors:
1. Verify all required permissions are granted in the app registration
2. Ensure admin consent is provided
3. Check that the user account has access to contacts and calendars

## Development

This project uses:
- **Python**: Primary programming language
- **Microsoft Graph SDK**: For Microsoft 365 API integration
- **Azure Identity**: For authentication with Microsoft Entra
- **python-dotenv**: For environment variable management

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT © [Léo Colombaro](https://colombaro.fr)

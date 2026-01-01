# 365 Birthdays

> 🎂 Microsoft 365 Birthday Calendar Sync

Automatically sync birthdays from your Microsoft 365 contacts to a dedicated calendar with reminders.

## About

This Python package uses the Microsoft Graph API to:
- Read contacts from your Microsoft 365 address book
- Extract birthday information from contacts
- Create and maintain a dedicated "Birthdays" calendar
- Generate calendar events for each contact's birthday
- Add reminders at 11:00 AM on the birthday

## Prerequisites

- Python 3.8 or higher
- [uv](https://docs.astral.sh/uv/) package manager
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

### 3. Configure Public Client Settings

Since this app uses device code flow for authentication:

1. Go to **Authentication** in your app registration
2. Under **Advanced settings** > **Allow public client flows**
3. Set **Enable the following mobile and desktop flows** to **Yes**
4. Click **Save**

### 4. Configure Environment Variables

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and fill in your values:
   - `CLIENT_ID`: Application (client) ID from your app registration
   - `TENANT_ID`: Directory (tenant) ID from your app registration
   - `CALENDAR_NAME`: (Optional) Name of the calendar to create/use (default: "Birthdays")

### 5. Install the Package

Using uv (recommended):

```bash
uv sync
```

Or install directly:

```bash
uv pip install -e .
```

## Usage

Run the birthday sync:

```bash
uv run birthdays365
```

Or if installed globally:

```bash
birthdays365
```

The application will:
1. Prompt you to visit a URL and enter a code to authenticate
2. After authentication, it will access your Microsoft 365 data
3. Create a "Birthdays" calendar if it doesn't exist
4. Read all contacts with birthday information
5. Check for existing birthday events to avoid duplicates
6. Create all-day calendar events for each new birthday with reminders enabled

## Package Structure

The package is organized as follows:

```
src/birthdays365/
├── __init__.py      # Package initialization and exports
├── auth.py          # Authentication handling
├── calendar.py      # Calendar operations
├── cli.py           # Command-line interface
├── config.py        # Configuration management
├── contacts.py      # Contact operations
└── sync.py          # Main synchronization logic
```

## Features

- ✅ Interactive device code authentication
- ✅ Automatic calendar creation
- ✅ All-day birthday events
- ✅ Reminders enabled for birthday events
- ✅ Duplicate detection (skip existing events)
- ✅ Configurable calendar name
- ✅ Secure credential management via environment variables
- ✅ Uses official Microsoft Graph SDK for Python
- ✅ Clean OOP architecture with modular design

## Security Considerations

- Never commit your `.env` file to version control
- Device code flow provides secure, interactive authentication
- No client secrets needed - more secure for desktop applications
- Apply principle of least privilege for API permissions
- Admin consent ensures proper authorization

## Troubleshooting

### Authentication Errors

If you encounter authentication errors:
1. Verify your `CLIENT_ID` and `TENANT_ID` are correct
2. Ensure admin consent was granted for the API permissions
3. Check that public client flows are enabled in your app registration
4. Make sure you complete the device code authentication flow

### Permission Errors

If you get permission-related errors:
1. Verify all required permissions are granted in the app registration
2. Ensure admin consent is provided
3. Check that the user account has access to contacts and calendars

## Development

This project uses:
- **Python**: Primary programming language (3.8+)
- **uv**: Fast Python package manager
- **ruff**: Fast Python linter and formatter
- **Microsoft Graph SDK**: For Microsoft 365 API integration
- **Azure Identity**: For authentication with Microsoft Entra
- **python-dotenv**: For environment variable management

### Development Setup

1. Clone the repository
2. Install uv: `pip install uv`
3. Install dependencies: `uv sync`
4. Configure your `.env` file
5. Run the application: `uv run birthdays365`

### Code Quality

Run linter and formatter:
```bash
# Check code
uv run ruff check src/

# Format code
uv run ruff format src/

# Fix auto-fixable issues
uv run ruff check --fix src/
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT © [Léo Colombaro](https://colombaro.fr)

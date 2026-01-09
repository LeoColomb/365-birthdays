# 365 Birthdays

> 🎂 Microsoft 365 Birthday Calendar Sync

Automatically sync birthdays from your Microsoft 365 contacts to a
dedicated calendar with reminders.

## About

This Python package uses the Microsoft Graph API to:

- Read contacts from your Microsoft 365 address book
- Extract birthday information from contacts
- Create and maintain a dedicated "Birthdays" calendar
- Generate calendar events for each contact's birthday
- Add reminders for birthday events

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
  - **Supported account types**: Accounts in this organizational directory
    only (Single tenant)
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
  - `CALENDAR_NAME`: (Optional) Name of the calendar to create/use
    (default: "Birthdays")

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
5. Check for existing birthday events and update them if the birthday
   date has changed
6. Create recurring all-day calendar events for each new birthday with
   reminders enabled
7. Events recur annually on the birthday date

## Package Structure

The package is organized as follows:

```text
src/birthdays365/
├── __init__.py      # Package initialization and exports
├── auth.py          # Authentication handling
├── calendar.py      # Calendar operations
├── cli.py           # Command-line interface
├── config.py        # Configuration management
├── contacts.py      # Contact operations
└── sync.py          # Main synchronization logic

tests/
├── __init__.py      # Test package initialization
├── test_calendar.py # Calendar module tests
├── test_config.py   # Configuration module tests
├── test_contacts.py # Contacts module tests
└── test_sync.py     # Synchronization logic tests
```

## Development

### Running Tests

The package includes a comprehensive test suite using pytest:

```bash
# Install development dependencies
uv sync --group dev

# Run all tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=birthdays365

# Run specific test file
uv run pytest tests/test_calendar.py
```

### Code Quality

The project uses ruff for linting and formatting:

```bash
# Check code quality
uv run ruff check src/ tests/

# Format code
uv run ruff format src/ tests/
```

### GitHub Actions Workflows

The repository includes automated workflows:

- **Tests** (`.github/workflows/test.yml`): Automatically runs the test
  suite on every push and pull request
- **Ruff** (`.github/workflows/ruff.yml`): Runs code quality checks
- **Birthday Sync** (`.github/workflows/sync.yml`): Automated daily
  birthday synchronization (requires repository secrets configuration)

To use the Birthday Sync workflow:

1. Go to your repository **Settings** > **Secrets and variables** >
   **Actions**
2. Add the following repository secrets:
   - `CLIENT_ID` - Your Microsoft Entra application (client) ID
   - `TENANT_ID` - Your Microsoft Entra directory (tenant) ID
   - `CALENDAR_NAME` (optional) - Calendar name (defaults to "Birthdays")
   - `SENTRY_DSN` (optional) - Sentry DSN for error tracking
3. The workflow runs daily at 6:00 AM UTC or can be triggered manually

## Features

- ✅ Interactive device code authentication
- ✅ Automatic calendar creation
- ✅ All-day birthday events with yearly recurrence
- ✅ Reminders enabled for birthday events
- ✅ Smart event updates when contact birthdays change
- ✅ Duplicate detection (skip existing events)
- ✅ Age calculation in event descriptions
- ✅ Contact ID tracking for easy retrieval
- ✅ Birthday category assignment using MS Graph API
- ✅ Configurable calendar name
- ✅ Sentry integration for error tracking (optional)
- ✅ Secure credential management via environment variables
- ✅ Uses official Microsoft Graph SDK for Python
- ✅ Comprehensive test suite with pytest
- ✅ Clean OOP architecture with modular design
- ✅ GitHub Actions workflows for testing and automated syncing

## Optional: Sentry Integration

To enable error tracking with Sentry:

1. Create a Sentry project at [sentry.io](https://sentry.io)
2. Get your DSN from the project settings
3. Add it to your `.env` file:

  ```bash
  SENTRY_DSN=https://your-sentry-dsn-here
  ```

When configured, all exceptions and errors will be automatically reported
to Sentry.

## Microsoft 365 Integration Guide

### What This App Does

The 365 Birthdays app integrates with your Microsoft 365 tenant to:

- Read contact information from your Microsoft 365 address book
- Extract birthday dates from contact profiles
- Create a dedicated "Birthdays" calendar in your Microsoft 365 account
- Generate recurring calendar events for each birthday
- Automatically update events if contact birthday information changes

### Required Microsoft 365 Setup

This application requires the following:

1. **Microsoft 365 Account**: A valid Microsoft 365 (formerly Office 365)
  account with access to:
  - Outlook/Exchange Online for calendar functionality
  - Microsoft Graph API access

2. **Microsoft Entra App Registration**: An app registered in Microsoft
  Entra (Azure AD) with:
  - **Application Type**: Public client application
  - **Redirect URI**: Not required for device code flow
  - **API Permissions**:
     - `Calendars.ReadWrite` (Delegated)
     - `Contacts.Read` (Delegated)
     - `User.Read` (Delegated)
   - **Admin Consent**: Granted for all permissions

3. **Public Client Flow**: Enabled in the app registration to support
   device code authentication

### How It Works

1. **Authentication**: Uses device code flow - you'll authenticate via
   browser
2. **Data Reading**: Reads contacts from your Microsoft 365 account via
   Graph API
3. **Calendar Management**: Creates/updates events in a dedicated calendar
4. **Recurrence**: Events repeat annually on the same date
5. **Smart Updates**: Detects when contact birthdays change and updates
   events accordingly

### Data Privacy

- All data stays within your Microsoft 365 tenant
- No data is sent to third-party services (except Sentry if configured)
- Authentication tokens are stored locally and managed by Microsoft's SDK
- The app only accesses data you explicitly grant permission for

### Permissions Explained

- **Calendars.ReadWrite**: Required to create and update birthday events
  in your calendar
- **Contacts.Read**: Required to read birthday information from your
  contacts
- **User.Read**: Required for basic authentication and to identify the
  logged-in user

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

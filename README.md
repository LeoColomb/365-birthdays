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

**For Interactive Use (Device Code Flow):**

1. In your app registration, go to **API permissions**
2. Click **Add a permission**
3. Select **Microsoft Graph** > **Delegated permissions**
4. Add the following permissions:
  - `Calendars.ReadWrite` - Create and manage calendar events
  - `Contacts.Read` - Read user contacts
  - `User.Read` - Sign in and read user profile
5. Click **Add permissions**
6. Click **Grant admin consent** (requires admin privileges)

**For Automated/Non-Interactive Use (Client Credentials Flow):**

For scenarios like GitHub Actions or scheduled scripts, you'll need **Application permissions** instead:

1. In your app registration, go to **API permissions**
2. Click **Add a permission**
3. Select **Microsoft Graph** > **Application permissions**
4. Add the following permissions:
  - `Calendars.ReadWrite` - Create and manage calendar events for all users
  - `Contacts.Read` - Read contacts in all mailboxes
5. Click **Add permissions**
6. Click **Grant admin consent** (requires admin privileges)

**Note:** Application permissions require admin consent and grant access to data across all users in the organization. Use with caution and follow the principle of least privilege.

### 3. Configure Authentication Method

The application supports two authentication methods:

**Option A: Device Code Flow (Interactive - Default)**

For local/interactive use:

1. Go to **Authentication** in your app registration
2. Under **Advanced settings** > **Allow public client flows**
3. Set **Enable the following mobile and desktop flows** to **Yes**
4. Click **Save**

**Option B: Client Secret Flow (Non-Interactive - for Automation)**

For automated scenarios like GitHub Actions:

1. Go to **Certificates & secrets** in your app registration
2. Under **Client secrets**, click **New client secret**
3. Add a description (e.g., "GitHub Actions Secret")
4. Choose an expiration period
5. Click **Add**
6. **Important:** Copy the secret value immediately - it won't be shown again
7. Save this value as `CLIENT_SECRET` in your environment variables

**Choosing the Right Method:**
- **Device Code Flow**: Use for local development or manual runs. Requires user interaction.
- **Client Secret Flow**: Use for CI/CD pipelines, scheduled tasks, or any non-interactive automation.

**User Context in Client Secret Flow:**

When using client credentials (client secret) with **Application permissions**, the application runs with application-level permissions and can access any user's data. You **must** specify which user's data to sync using the `TARGET_USER_UPN` environment variable.

**Setup for Client Credentials with Application Permissions:**

1. The admin must grant **Application permissions** (not Delegated):
   - `Calendars.ReadWrite` (Application)
   - `Contacts.Read` (Application)
2. Create a client secret in your app registration
3. Set the `TARGET_USER_UPN` environment variable to the user's email address (User Principal Name)
   - Example: `TARGET_USER_UPN=john.doe@company.com`
4. The application will access `/users/{TARGET_USER_UPN}/contacts` and `/users/{TARGET_USER_UPN}/calendars`

**Backward Compatibility:**

- If `TARGET_USER_UPN` is **not set**, the app uses `/me` endpoints (delegated permissions)
- This maintains backward compatibility with existing interactive setups
- For full automation in CI/CD, you **must** set `TARGET_USER_UPN`

### 4. Configure Environment Variables

1. Copy the example environment file:

  ```bash
  cp .env.example .env
  ```

2. Edit `.env` and fill in your values:
  - `CLIENT_ID`: Application (client) ID from your app registration
  - `TENANT_ID`: Directory (tenant) ID from your app registration
  - `CLIENT_SECRET`: (Optional) Client secret for non-interactive authentication. If not provided, device code flow will be used.
  - `TARGET_USER_UPN`: (Optional, but **required** when using CLIENT_SECRET with Application permissions) User's email address (e.g., user@company.com) to specify whose contacts and calendar to sync
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

- **Device Code Flow**: Provides secure, interactive authentication without storing secrets
- **Client Secret Flow**: Requires careful secret management - never commit secrets to version control
- **Client Secret Storage**: 
  - For local use: Store in `.env` file (gitignored)
  - For GitHub Actions: Use encrypted repository secrets
  - Rotate secrets regularly
- **Permissions**: Apply principle of least privilege
  - Use Delegated permissions for interactive use
  - Use Application permissions only when necessary for automation
- **Admin Consent**: Ensures proper authorization for all permissions
- **Secret Expiration**: Client secrets expire - monitor and rotate them before expiration

## Troubleshooting

### Authentication Errors

**Device Code Flow:**
1. Verify your `CLIENT_ID` and `TENANT_ID` are correct
2. Ensure admin consent was granted for the Delegated API permissions
3. Check that public client flows are enabled in your app registration
4. Make sure you complete the device code authentication flow in the browser

**Client Secret Flow:**
1. Verify `CLIENT_ID`, `TENANT_ID`, and `CLIENT_SECRET` are all correct
2. Check that the client secret hasn't expired
3. Ensure admin consent was granted for the Application API permissions
4. Verify the secret value is copied correctly (no extra spaces/characters)

### Permission Errors

If you get permission-related errors:

1. Verify all required permissions are granted in the app registration
2. Ensure admin consent is provided
3. Check that the user account has access to contacts and calendars

## Development

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

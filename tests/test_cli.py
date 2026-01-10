# MIT License
# Copyright (c) 2024-present Léo Colombaro

"""Tests for CLI module."""

from unittest.mock import Mock, patch

import pytest

from birthdays365.cli import main


def test_main_missing_env_variables():
    """Test main with missing environment variables."""
    with patch("birthdays365.cli.Config.from_env") as mock_config:
        mock_config.side_effect = ValueError("Missing required environment variables")

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 1


def test_main_with_sentry_initialization():
    """Test main initializes Sentry when DSN is provided."""
    mock_config = Mock()
    mock_config.sentry_dsn = "https://test@sentry.io/123"

    with patch("birthdays365.cli.Config.from_env", return_value=mock_config), \
         patch("birthdays365.cli.sentry_sdk.init") as mock_sentry_init, \
         patch("birthdays365.cli.BirthdaySync"), \
         patch("birthdays365.cli.asyncio.run"):

        main()

        # Verify Sentry was initialized with the DSN
        mock_sentry_init.assert_called_once_with(
            dsn="https://test@sentry.io/123"
        )


def test_main_without_sentry():
    """Test main without Sentry DSN."""
    mock_config = Mock()
    mock_config.sentry_dsn = None

    with patch("birthdays365.cli.Config.from_env", return_value=mock_config), \
         patch("birthdays365.cli.sentry_sdk.init") as mock_sentry_init, \
         patch("birthdays365.cli.BirthdaySync"), \
         patch("birthdays365.cli.asyncio.run"):

        main()

        # Verify Sentry was not initialized
        mock_sentry_init.assert_not_called()


def test_main_exception_captured_in_sentry():
    """Test that exceptions are captured in Sentry when configured."""
    mock_config = Mock()
    mock_config.sentry_dsn = "https://test@sentry.io/123"

    with patch("birthdays365.cli.Config.from_env", return_value=mock_config), \
         patch("birthdays365.cli.sentry_sdk.init"), \
         patch("birthdays365.cli.sentry_sdk.capture_exception") as mock_capture, \
         patch("birthdays365.cli.BirthdaySync"), \
         patch("birthdays365.cli.asyncio.run") as mock_run:

        # Make asyncio.run raise an exception
        test_exception = RuntimeError("Test error")
        mock_run.side_effect = test_exception

        with pytest.raises(SystemExit):
            main()

        # Verify exception was captured
        mock_capture.assert_called_once_with(test_exception)

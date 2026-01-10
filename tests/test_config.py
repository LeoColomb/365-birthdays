# MIT License
# Copyright (c) 2024-present Léo Colombaro

"""Tests for configuration module."""

import os
import unittest
from unittest.mock import patch

from birthdays365.config import Config


class TestConfig(unittest.TestCase):
    """Test cases for Config class."""

    @patch.dict(
        os.environ,
        {
            "CLIENT_ID": "test-client-id",
            "TENANT_ID": "test-tenant-id",
            "CALENDAR_NAME": "TestCalendar",
            "CLIENT_SECRET": "test-client-secret",
            "SENTRY_DSN": "https://test@sentry.io/123",
        },
    )
    def test_config_from_env(self):
        """Test configuration loading from environment variables."""
        config = Config.from_env()

        self.assertEqual(config.client_id, "test-client-id")
        self.assertEqual(config.tenant_id, "test-tenant-id")
        self.assertEqual(config.calendar_name, "TestCalendar")
        self.assertEqual(config.client_secret, "test-client-secret")
        self.assertEqual(config.sentry_dsn, "https://test@sentry.io/123")

    @patch.dict(
        os.environ,
        {
            "CLIENT_ID": "test-client-id",
            "TENANT_ID": "test-tenant-id",
        },
        clear=True,
    )
    def test_config_defaults(self):
        """Test configuration with default values."""
        config = Config.from_env()

        self.assertEqual(config.client_id, "test-client-id")
        self.assertEqual(config.tenant_id, "test-tenant-id")
        self.assertEqual(config.calendar_name, "Birthdays")  # default
        self.assertIsNone(config.client_secret)  # default
        self.assertIsNone(config.sentry_dsn)  # default

    @patch.dict(os.environ, {}, clear=True)
    def test_config_missing_required(self):
        """Test configuration with missing required values."""
        with self.assertRaises(ValueError):
            Config.from_env()


if __name__ == "__main__":
    unittest.main()

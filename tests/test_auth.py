# MIT License
# Copyright (c) 2024-present Léo Colombaro

"""Tests for auth module."""

from unittest.mock import patch

from birthdays365.auth import GraphAuthenticator
from birthdays365.config import Config


def test_graph_authenticator_initialization():
    """Test GraphAuthenticator initialization."""
    config = Config(client_id="test_client", tenant_id="test_tenant")

    authenticator = GraphAuthenticator(config)

    assert authenticator.config == config
    assert authenticator._client is None


def test_graph_authenticator_get_client_device_code():
    """Test get_client method with device code flow."""
    config = Config(client_id="test_client", tenant_id="test_tenant")

    with patch("birthdays365.auth.DeviceCodeCredential") as mock_credential, \
         patch("birthdays365.auth.GraphServiceClient") as mock_graph:

        authenticator = GraphAuthenticator(config)
        client = authenticator.get_client()

        # Verify DeviceCodeCredential was called with correct parameters
        mock_credential.assert_called_once()
        call_kwargs = mock_credential.call_args.kwargs
        assert call_kwargs["client_id"] == "test_client"
        assert call_kwargs["tenant_id"] == "test_tenant"

        # Verify GraphServiceClient was created
        mock_graph.assert_called_once()
        assert client == mock_graph.return_value


def test_graph_authenticator_get_client_client_secret():
    """Test get_client method with client secret flow."""
    config = Config(
        client_id="test_client",
        tenant_id="test_tenant",
        client_secret="test_secret"
    )

    with patch("birthdays365.auth.ClientSecretCredential") as mock_credential, \
         patch("birthdays365.auth.GraphServiceClient") as mock_graph:

        authenticator = GraphAuthenticator(config)
        client = authenticator.get_client()

        # Verify ClientSecretCredential was called with correct parameters
        mock_credential.assert_called_once()
        call_kwargs = mock_credential.call_args.kwargs
        assert call_kwargs["client_id"] == "test_client"
        assert call_kwargs["tenant_id"] == "test_tenant"
        assert call_kwargs["client_secret"] == "test_secret"

        # Verify GraphServiceClient was created
        mock_graph.assert_called_once()
        assert client == mock_graph.return_value

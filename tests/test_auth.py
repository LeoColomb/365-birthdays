# MIT License
# Copyright (c) 2024-present Léo Colombaro

"""Tests for auth module."""

from unittest.mock import Mock, patch

import pytest

from birthdays365.auth import GraphAuthenticator
from birthdays365.config import Config


def test_graph_authenticator_initialization():
    """Test GraphAuthenticator initialization."""
    config = Config(client_id="test_client", tenant_id="test_tenant")
    
    authenticator = GraphAuthenticator(config)
    
    assert authenticator.config == config
    assert authenticator._client is None


def test_graph_authenticator_get_client():
    """Test get_client method."""
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

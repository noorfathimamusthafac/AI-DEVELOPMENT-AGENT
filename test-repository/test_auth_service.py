import pytest
from auth_service import verify_credentials, get_user_profile

def test_valid_login():
    """Valid credentials must return True."""
    assert verify_credentials("alice@example.com", "alice_secret") is True

def test_invalid_password_returns_false():
    """Invalid password must return False without throwing KeyError."""
    assert verify_credentials("alice@example.com", "wrong_password") is False

def test_unknown_user_returns_false():
    """Unknown email must return False without throwing KeyError."""
    assert verify_credentials("ghost@example.com", "secret") is False

def test_get_user_profile():
    """Profile retrieval should return dictionary."""
    profile = get_user_profile("alice@example.com")
    assert profile is not None
    assert profile["name"] == "Alice Developer"

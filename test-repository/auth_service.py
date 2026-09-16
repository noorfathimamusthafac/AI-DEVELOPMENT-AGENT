"""
Authentication and User Service.
"""

USERS_DATABASE = {
    "alice@example.com": {
        "password_hash": "hashed_alice_secret",
        "name": "Alice Developer",
        "role": "developer"
    },
    "bob@example.com": {
        "password_hash": "hashed_bob_secret",
        "name": "Bob Admin",
        "role": "admin"
    }
}

def verify_credentials(email: str, password: str) -> bool:
    """
    Verify user login credentials.
    BUG-101: If an unknown email or invalid password is provided,
    this currently raises an unhandled KeyError instead of returning False.
    """
    # BUGGY IMPLEMENTATION
    user = USERS_DATABASE[email]  # Raises KeyError if email doesn't exist
    expected_hash = f"hashed_{password}"
    if user["password_hash"] != expected_hash:
        raise KeyError("Invalid password credentials provided") # Buggy: raises KeyError instead of False
    return True

def get_user_profile(email: str) -> dict | None:
    """Retrieve user profile by email."""
    return USERS_DATABASE.get(email)

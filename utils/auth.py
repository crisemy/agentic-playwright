# utils/auth.py
"""Authentication helpers for API-based and UI-based login."""
from utils.api_client import ApiClient


def login_api() -> dict:
    """Perform API login and return session cookie info.

    This is the fast path — no browser UI involved.
    Returns a dict with 'session_id' and 'username' keys.
    """
    client = ApiClient()
    try:
        result = client.login()
        return result
    finally:
        client.close()


def login_ui(page):
    """Perform login via the browser UI (Playwright).

    Used for tests that need to validate the login form itself.
    """
    from pages.login_page import LoginPage

    login_page = LoginPage(page)
    login_page.navigate()
    login_page.login()

# tests/conftest.py
import pytest
from pathlib import Path
from playwright.sync_api import sync_playwright
from utils.config_loader import Config
from pages.login_page import LoginPage

config = Config()

AUTH_STATE_PATH = Path("auth/storage_state.json")



@pytest.fixture(scope="session")
def browser_name(request):
    return request.config.getoption("--browser")


@pytest.fixture(scope="session")
def playwright_instance():
    """Start a single Playwright instance for the session"""
    with sync_playwright() as p:
        yield p


@pytest.fixture(scope="session")
def browser(playwright_instance, browser_name):
    """Launch requested browser once per session"""
    print(f"🚀 Launching {browser_name} browser...")
    b = getattr(playwright_instance, browser_name).launch(
        headless=config.headless,
        slow_mo=config.slow_mo
    )
    yield b
    b.close()


@pytest.fixture(scope="function")
def page(browser):
    """New page for each test"""
    context = browser.new_context()
    page = context.new_page()
    yield page
    page.close()
    context.close()


@pytest.fixture(scope="session")
def storage_state(browser):
    """Create or load saved authentication state using the existing browser"""
    needs_creation = (
        not AUTH_STATE_PATH.exists() or
        AUTH_STATE_PATH.stat().st_size == 0
    )
    if needs_creation:
        print("🔄 Creating new storage state (first-time login)...")
        AUTH_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)

        context = browser.new_context()
        page = context.new_page()

        login_page = LoginPage(page)
        login_page.navigate()
        login_page.login()

        context.storage_state(path=AUTH_STATE_PATH)
        print(f"✅ Storage state saved to {AUTH_STATE_PATH}")

        page.close()
        context.close()

    return str(AUTH_STATE_PATH)


@pytest.fixture(scope="function")
def logged_in_page(browser, storage_state):
    """Fast login using saved storage state"""
    context = browser.new_context(storage_state=storage_state)
    page = context.new_page()
    page.goto(config.base_url, wait_until="networkidle")
    print("🚀 Using saved storage state for fast login")
    yield page
    page.close()
    context.close()
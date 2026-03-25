# pages/base_page.py
from playwright.sync_api import Page
from utils.config_loader import Config
from utils.grok_client import GrokClient
import datetime

config = Config()
grok = GrokClient()

class BasePage:
    """Base class for all Page Objects with self-healing capability"""
    def __init__(self, page: Page):
        self.page = page
        self.timeout = config.timeout

    def navigate(self, url: str = None):
        """Navigate to URL (uses base_url from config if none provided)"""
        final_url = url or config.base_url
        self.page.goto(final_url, wait_until="networkidle", timeout=self.timeout)
        print(f"✅ Navigated to: {final_url}")

    def take_screenshot(self, name: str = "screenshot"):
        """Take and save screenshot with timestamp"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        path = f"screenshots/{name}_{timestamp}.png"
        self.page.screenshot(path=path)
        print(f"📸 Screenshot saved: {path}")

    def wait_for(self, selector: str):
        """Wait for element with basic timeout"""
        self.page.wait_for_selector(selector, timeout=self.timeout)

    def smart_locator(self, original_selector: str, element_description: str):
        """Return a healed locator using Grok if needed"""
        healed = grok.heal_locator(self.page, original_selector, element_description)
        return self.page.locator(healed)
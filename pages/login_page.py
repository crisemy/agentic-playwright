# pages/login_page.py
from pages.base_page import BasePage
from utils.config_loader import Config

config = Config()

class LoginPage(BasePage):
    """Page Object for Login page with self-healing locators"""
    def __init__(self, page):
        super().__init__(page)
        self.username = None
        self.password = None
        self.login_btn = None
        self.error_msg = None
        self._init_locators()

    def _init_locators(self):
        """Initialize locators (lazy — no DOM check at this point)"""
        self.username = self.page.locator("#user-name")
        self.password = self.page.locator("#password")
        self.login_btn = self.page.locator("#login-button")
        self.error_msg = self.page.locator("h3[data-test='error']")

    def login(self, username: str = None, password: str = None):
        """Perform login"""
        user = config.get_user() if not username else {"username": username, "password": password}
        self.username.fill(user["username"])
        self.password.fill(user["password"])
        self.login_btn.click()
        print(f"🔑 Login performed with user: {user['username']}")
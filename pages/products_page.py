# pages/products_page.py
"""Page Object for the Products (inventory) page served by the mock API."""
from playwright.sync_api import Page
from pages.base_page import BasePage
from utils.config_loader import Config

config = Config()


class ProductsPage(BasePage):
    """Page Object for the inventory / product listing page."""

    def __init__(self, page: Page):
        super().__init__(page)
        self._init_locators()

    def _init_locators(self):
        self.products_grid = self.page.locator("#products-grid")
        self.product_cards = self.page.locator(".product-card")
        self.cart_badge = self.page.locator("#cart-badge")
        self.sort_select = self.page.locator("#sort-select")

    def navigate(self, url: str = None):
        """Navigate to the inventory page."""
        final_url = url or f"{config.mock_api_url}/inventory.html"
        super().navigate(final_url)

    def is_on_inventory_page(self) -> bool:
        """Guard assertion — confirms we are on the inventory page."""
        return "inventory" in self.page.url

    def get_product_count(self) -> int:
        """Return the number of visible product cards."""
        return self.product_cards.count()

    def get_product_titles(self) -> list[str]:
        """Return all product titles visible on the page."""
        titles = []
        for i in range(1, self.get_product_count() + 1):
            locator = self.page.locator(f"#product-title-{i}")
            if locator.count() > 0:
                titles.append(locator.inner_text())
        return titles

    def get_product_prices(self) -> list[float]:
        """Return all product prices as floats."""
        prices = []
        for i in range(1, self.get_product_count() + 1):
            locator = self.page.locator(f"#product-price-{i}")
            if locator.count() > 0:
                text = locator.inner_text().replace("$", "").strip()
                prices.append(float(text))
        return prices

    def get_cart_count(self) -> int:
        """Return the current cart badge count."""
        text = self.cart_badge.inner_text()
        return int(text) if text.isdigit() else 0

    def add_to_cart(self, index: int):
        """Click the 'Add to Cart' button for the product at 1-based index."""
        btn = self.page.locator(f"#add-to-cart-btn-{index}")
        btn.click()

    def sort_by(self, option: str):
        """Sort products by the given option: az, za, lohi, hilo."""
        self.sort_select.select_option(option)

    def go_to_cart(self):
        """Navigate to the cart page."""
        self.page.locator(".cart-link").click()

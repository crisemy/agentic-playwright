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

    def _product_title_locator(self, index: int):
        return self.smart_locator(
            f"#product-title-{index}",
            f"Product title for product at index {index}"
        )

    def _product_price_locator(self, index: int):
        return self.smart_locator(
            f"#product-price-{index}",
            f"Product price for product at index {index}"
        )

    def _add_to_cart_btn_locator(self, index: int):
        return self.smart_locator(
            f"#add-to-cart-btn-{index}",
            f"'Add to Cart' button for product at index {index}"
        )

    def navigate(self, url: str = None):
        """Navigate to the inventory page."""
        final_url = url or f"{config.mock_api_url}/inventory.html"
        super().navigate(final_url)

    def is_on_inventory_page(self) -> bool:
        """Guard assertion — confirms we are on the inventory page."""
        return "inventory" in self.page.url

    def get_product_count(self) -> int:
        """Return the number of visible product cards."""
        grid = self.smart_locator("#products-grid", "Products grid container")
        return grid.locator(".product-card").count()

    def get_product_titles(self) -> list[str]:
        """Return all product titles visible on the page."""
        titles = []
        for i in range(1, self.get_product_count() + 1):
            locator = self._product_title_locator(i)
            if locator.count() > 0:
                titles.append(locator.inner_text())
        return titles

    def get_product_prices(self) -> list[float]:
        """Return all product prices as floats."""
        prices = []
        for i in range(1, self.get_product_count() + 1):
            locator = self._product_price_locator(i)
            if locator.count() > 0:
                text = locator.inner_text().replace("$", "").strip()
                prices.append(float(text))
        return prices

    def get_cart_count(self) -> int:
        """Return the current cart badge count."""
        badge = self.smart_locator("#cart-badge", "Shopping cart badge count")
        text = badge.inner_text()
        return int(text) if text.isdigit() else 0

    def add_to_cart(self, index: int):
        """Click the 'Add to Cart' button for the product at 1-based index."""
        btn = self._add_to_cart_btn_locator(index)
        btn.click()

    def sort_by(self, option: str):
        """Sort products by the given option: az, za, lohi, hilo."""
        sort_select = self.smart_locator("#sort-select", "Product sort dropdown")
        sort_select.select_option(option)

    def go_to_cart(self):
        """Navigate to the cart page."""
        cart_link = self.smart_locator(".cart-link", "Shopping cart link")
        cart_link.click()

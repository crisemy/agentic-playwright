# tests/test_products.py
"""Product listing tests — all use api_logged_in_page fixture."""
import pytest
from pages.products_page import ProductsPage


def test_inventory_page_loads(api_logged_in_page):
    """Verify the inventory page loads with the expected URL and page title."""
    products_page = ProductsPage(api_logged_in_page)
    products_page.navigate()

    assert products_page.is_on_inventory_page(), (
        f"Expected URL to contain 'inventory', got: {api_logged_in_page.url}"
    )
    assert "Swag Labs" in api_logged_in_page.title()
    products_page.take_screenshot("inventory_page_loads")


def test_product_list_has_items(api_logged_in_page):
    """Assert that at least one product card is visible on the page."""
    products_page = ProductsPage(api_logged_in_page)
    products_page.navigate()

    count = products_page.get_product_count()
    assert count > 0, f"Expected products but found {count}"
    products_page.take_screenshot("product_list_has_items")


def test_product_titles_are_visible(api_logged_in_page):
    """Assert all product titles are visible and non-empty."""
    products_page = ProductsPage(api_logged_in_page)
    products_page.navigate()

    titles = products_page.get_product_titles()
    assert len(titles) > 0, "Expected at least one product title"
    for title in titles:
        assert len(title.strip()) > 0, "Found an empty product title"
    products_page.take_screenshot("product_titles_visible")


def test_add_product_to_cart(api_logged_in_page):
    """Click 'Add to Cart' on the first product and assert cart badge is 1."""
    products_page = ProductsPage(api_logged_in_page)
    products_page.navigate()

    assert products_page.get_cart_count() == 0, "Cart should start empty"
    products_page.add_to_cart(index=1)
    assert products_page.get_cart_count() == 1, "Cart badge should be 1 after adding item"
    products_page.take_screenshot("add_product_to_cart")

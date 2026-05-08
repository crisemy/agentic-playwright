# utils/api_client.py
"""HTTP client for the mock API server."""
from utils.config_loader import Config
import httpx

config = Config()


class ApiClient:
    """Lightweight HTTP client for mock API operations."""

    def __init__(self, base_url: str = None):
        self.base_url = base_url or config.mock_api_url
        self._client = httpx.Client(base_url=self.base_url, timeout=10.0)
        self._session_cookie = None

    def close(self):
        self._client.close()

    def login(self, username: str = None, password: str = None) -> dict:
        """POST /login — returns session cookie info."""
        user = config.get_user() if not username else {"username": username, "password": password}
        response = self._client.post(
            "/login",
            data={"username": user["username"], "password": user["password"]},
        )
        response.raise_for_status()
        self._session_cookie = response.cookies.get("session_id")
        return {"session_id": self._session_cookie, "username": user["username"]}

    def get_products(self) -> list[dict]:
        """GET /products — returns the product catalog."""
        response = self._client.get("/products")
        response.raise_for_status()
        return response.json()

    def get_cart(self) -> dict:
        """GET /cart — returns current cart contents."""
        cookies = {"session_id": self._session_cookie} if self._session_cookie else {}
        response = self._client.get("/cart", cookies=cookies)
        response.raise_for_status()
        return response.json()

    def add_to_cart(self, product_id: str) -> dict:
        """POST /cart — adds a product to the cart."""
        cookies = {"session_id": self._session_cookie} if self._session_cookie else {}
        response = self._client.post(
            "/cart",
            json={"product_id": product_id},
            cookies=cookies,
        )
        response.raise_for_status()
        return response.json()

    def clear_cart(self) -> dict:
        """DELETE /cart — clears the cart."""
        cookies = {"session_id": self._session_cookie} if self._session_cookie else {}
        response = self._client.delete("/cart", cookies=cookies)
        response.raise_for_status()
        return response.json()

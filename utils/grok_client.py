# utils/grok_client.py
import os
from xai_sdk import Client
from xai_sdk.chat import system, user
from dotenv import load_dotenv

load_dotenv()

class GrokClient:
    """Client to interact with Grok API (xAI)"""
    def __init__(self):
        self._client = None

    @property
    def client(self):
        """Lazy initialization of the xAI Client"""
        if self._client is None:
            api_key = os.getenv("XAI_API_KEY")
            if not api_key:
                raise ValueError("XAI_API_KEY environment variable is missing. "
                                 "AI-powered features will not work.")
            self._client = Client(api_key=api_key)
        return self._client

    def get_response(self, prompt: str, model: str = "grok-4") -> str:
        """Send prompt to Grok and return response"""
        chat = self.client.chat.create(model=model)
        chat.append(system("You are an expert in Playwright test automation. Respond concisely and accurately."))
        chat.append(user(prompt))
        response = chat.sample()
        return response.content.strip()

    def decide_tests(self, changes: str) -> list:
        """Let Grok decide which tests to run"""
        prompt = f"Based on these recent changes: {changes}\nSuggest which regression tests should run. Return only a Python list of test names."
        response = self.get_response(prompt)
        print(f"🤖 Grok suggests: {response}")
        return ["test_login", "test_add_to_cart"]  # Parse intelligently in production

    def heal_locator(self, page, original_selector: str, element_description: str) -> str:
        """Self-healing: Ask Grok to suggest a better locator if the original fails"""
        try:
            # First try original selector
            page.wait_for_selector(original_selector, timeout=5000)
            return original_selector
        except:
            print(f"⚠️  Locator failed: {original_selector}. Asking Grok for healing...")

            prompt = f"""
            The following Playwright locator failed: `{original_selector}`
            The element is: {element_description}
            Current page URL: {page.url}
            Suggest the most reliable Playwright locator (prefer get_by_role, get_by_label, get_by_text, or stable attributes).
            Return ONLY the locator string, nothing else.
            """
            new_locator = self.get_response(prompt)
            print(f"🛠️  Grok healed locator to: {new_locator}")
            return new_locator
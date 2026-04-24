# utils/grok_client.py
"""Grok client for AI-powered self-healing locators and LLM calls."""
import os
import re
from typing import Optional

from dotenv import load_dotenv
from crewai import LLM

load_dotenv()


SYSTEM_PROMPT = """You are a Playwright CSS selector expert. Given a broken CSS selector, the page's HTML DOM snapshot, and a human-readable description of the element, return a WORKING CSS selector that will uniquely find that element.

Rules:
- Return ONLY the CSS selector string — no explanation, no markdown, no code blocks
- The selector must be a valid CSS selector that works with Playwright's page.locator()
- Prefer #id and data-test-* attributes when available
- Use compound selectors if needed (e.g., "button[id='add-to-cart-btn-1']")
- If the element cannot be found in the DOM, return the original selector unchanged
- Do NOT guess — only use attributes you can see in the provided HTML
"""


class GrokClient:
    """Unified Grok client used by both self-healing and CrewAI agents."""

    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY") or os.getenv("XAI_API_KEY")
        self._available = False

        if self.api_key:
            os.environ["GROQ_API_KEY"] = self.api_key
            self.llm = LLM(
                model="groq/llama-3.1-8b-instant",
                api_key=self.api_key,
                base_url="https://api.groq.com/openai/v1",
            )
            self._available = True
        else:
            print("⚠️  [Grok] API key not found — self-healing is disabled. Set GROQ_API_KEY in .env to enable.")
            self.llm = None

    def heal_locator(self, page, original_selector: str, element_description: str) -> str:
        """Attempt to heal a broken CSS selector using the LLM.

        Sends the original selector, element description, and a DOM snapshot
        to Groq and returns the corrected CSS selector.
        Falls back to the original selector if healing is unavailable or fails.
        """
        if not self._available:
            return original_selector

        try:
            # Capture a focused DOM snapshot — grab the page HTML
            html_snapshot = page.content()
            # Trim to a reasonable size for the LLM context window
            html_snapshot = self._trim_snapshot(html_snapshot, max_chars=15000)

            user_prompt = (
                f"Original (broken) selector: {original_selector}\n"
                f"Element description: {element_description}\n"
                f"Page HTML DOM snapshot (first {len(html_snapshot)} chars):\n"
                f"{html_snapshot}"
            )

            response = self.llm.call(
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ]
            )

            # Strip any markdown formatting the LLM might add
            healed = self._strip_markdown(str(response).strip())
            print(f"🔧 [Grok] Selector healed: '{original_selector}' → '{healed}'")
            return healed

        except Exception as exc:
            print(f"⚠️  [Grok] Healing failed ({exc}), falling back to original selector")
            return original_selector

    def _trim_snapshot(self, html: str, max_chars: int = 15000) -> str:
        """Trim HTML snapshot to fit within the context window."""
        if len(html) <= max_chars:
            return html
        return html[:max_chars] + "\n... [trimmed]"

    def _strip_markdown(self, text: str) -> str:
        """Remove markdown code fences if the LLM wrapped the selector."""
        text = text.strip()
        text = re.sub(r"^```(?:css|html)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
        return text.strip()

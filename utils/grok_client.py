# utils/grok_client.py
import os
import asyncio
from dotenv import load_dotenv
from crewai import LLM  # Import CrewAI's LLM wrapper

load_dotenv()

class GrokClient:
    """Unified Grok client used by both direct calls and CrewAI agents"""
    
    def __init__(self):
        self.api_key = os.getenv("XAI_API_KEY")
        
        # --- Preventive Validation ---
        if not self.api_key:
            raise ValueError(
                "\n❌ ERROR: XAI_API_KEY is missing! \n"
                "Please configure 'XAI_API_KEY' as a GitHub Action Secret or set it in your .env file.\n"
                "Get your key at: https://console.x.ai/"
            )
        
        # Ensure it's in the environment for internal calls too
        os.environ["XAI_API_KEY"] = self.api_key

        # CrewAI-compatible LLM wrapper
        # Using "openai/xai" prefix because xAI is OpenAI-compatible (more stable provider in LiteLLM)
        self.llm = LLM(
            model="openai/grok-4",   # or "openai/grok-beta"
            api_key=self.api_key,
            base_url="https://api.x.ai/v1"
        )

    # === Direct async calls (kept for your existing self-healing) ===
    async def get_response(self, prompt: str) -> str:
        # For backward compatibility with your existing code
        # CrewAI's LLM can also be called directly if needed
        chat = self.llm  # You can wrap further if needed
        # Simple implementation – in production you can extend with full chat history
        response = await asyncio.to_thread(self.llm.call, prompt)  # or use proper async if available
        return str(response).strip()

    async def heal_locator(self, page, original_selector: str, element_description: str) -> str:
        # ... (your existing self-healing logic remains unchanged)
        pass  # Keep your previous implementation here

    # Expose the LLM for CrewAI agents
    def get_llm(self):
        return self.llm
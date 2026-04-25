# agents/predictive_selector.py
import subprocess
from utils.grok_client import GrokClient

class PredictiveSelector:
    """Uses LLM to decide which tests to run based on code changes."""
    
    def __init__(self):
        self.grok = GrokClient()
        self.llm = self.grok.get_llm()

    def get_git_diff(self, branch: str = "main") -> str:
        """Get the diff between current branch and target branch."""
        try:
            result = subprocess.run(
                ["git", "diff", branch], 
                capture_output=True, 
                text=True, 
                check=True
            )
            return result.stdout
        except Exception as e:
            return f"Error getting git diff: {e}"

    def select_tests(self, diff_content: str) -> list[str]:
        """Ask Grok to identify relevant test files based on the diff."""
        if not diff_content.strip():
            return ["tests/test_login.py", "tests/test_products.py"] # Default to all if no diff
            
        prompt = f"""
        Analyze the following git diff and identify which Playwright tests are most likely affected.
        Available tests:
        - tests/test_login.py (Authentication, UI login)
        - tests/test_products.py (Product list, Cart, Mock API integration)
        
        Git Diff:
        {diff_content[:10000]}
        
        Return ONLY a comma-separated list of test file paths that should be executed.
        If unsure, include both.
        """
        
        if not self.grok._available:
            return ["tests/test_login.py", "tests/test_products.py"]
            
        response = self.llm.call(prompt)
        test_list = [t.strip() for t in str(response).split(",")]
        return test_list

if __name__ == "__main__":
    selector = PredictiveSelector()
    print("🔍 Analyzing changes...")
    diff = selector.get_git_diff()
    recommended = selector.select_tests(diff)
    print(f"🚀 Recommended tests to run: {recommended}")

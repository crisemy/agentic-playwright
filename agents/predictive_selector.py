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
            # If no diff, we might be on a clean branch, return all major tests
            return ["tests/test_login.py", "tests/test_products.py"]
            
        prompt = f"""
        [CRITICAL: RETURN ONLY FILE PATHS]
        Analyze the following git diff and identify which Playwright tests are most likely affected.
        
        Available tests to choose from:
        - tests/test_login.py
        - tests/test_products.py
        
        Git Diff:
        {diff_content[:10000]}
        
        Instructions:
        1. Identify which test files are affected by the changes in the diff.
        2. Return ONLY a comma-separated list of the file paths.
        3. Do NOT include any explanations, reasoning, or extra text.
        4. If unsure, include both.
        
        Example Output:
        tests/test_login.py, tests/test_products.py
        """
        
        if not self.grok._available:
            return ["tests/test_login.py", "tests/test_products.py"]
            
        response = str(self.llm.call(prompt)).strip()
        
        # Robust parsing: Remove common AI formatting (backticks, dashes, dots)
        clean_response = response.replace("`", "").replace("- ", "").replace("* ", "")
        raw_list = [t.strip() for t in clean_response.replace("\n", ",").split(",")]
        
        test_list = []
        for t in raw_list:
            t = t.strip()
            if t.endswith(".py") and "tests/" in t:
                test_list.append(t)
        
        # Fallback if parsing failed completely
        if not test_list:
            if "login" in response.lower(): test_list.append("tests/test_login.py")
            if "product" in response.lower(): test_list.append("tests/test_products.py")
            
        return list(set(test_list)) # Remove duplicates

if __name__ == "__main__":
    selector = PredictiveSelector()
    print("Analyzing changes...")
    diff = selector.get_git_diff()
    recommended = selector.select_tests(diff)
    print(f"Recommended tests to run: {recommended}")

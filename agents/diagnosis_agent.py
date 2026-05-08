# agents/diagnosis_agent.py
import os
from typing import Optional
from utils.grok_client import GrokClient
from crewai import Agent, Task, Crew

class DiagnosisAgent:
    """Specialized agent for Root Cause Analysis (RCA) of test failures."""
    
    def __init__(self):
        self.grok = GrokClient()
        self.llm = self.grok.get_llm()
        
    def get_agent(self) -> Agent:
        return Agent(
            role="Test Failure Diagnostician",
            goal="Analyze tracebacks and DOM snapshots to provide precise root cause analysis and code fixes.",
            backstory=(
                "You are a master of debugging Playwright tests. You can look at a "
                "Python traceback and a DOM snapshot and immediately identify if the "
                "failure is due to a race condition, a changed locator, a backend API error, "
                "or a functional bug in the application."
            ),
            llm=self.llm,
            verbose=True
        )

    def analyze_failure(self, traceback: str, dom_snapshot: str, original_test_code: str) -> str:
        """Run a diagnostic task on a specific test failure."""
        
        diagnostic_task = Task(
            description=(
                f"Analyze the following test failure:\n\n"
                f"### Traceback:\n{traceback}\n\n"
                f"### Original Test Code:\n{original_test_code}\n\n"
                f"### DOM Snapshot (at failure):\n{dom_snapshot[:5000]}...\n\n"
                "Determine the root cause. If it is a locator issue, suggest the new CSS selector. "
                "If it is a timing issue, suggest better wait conditions. "
                "Return a structured report with: Root Cause, Suggested Fix, and Confidence Level."
            ),
            expected_output="A detailed diagnostic report with Root Cause and Suggested Fix.",
            agent=self.get_agent()
        )
        
        crew = Crew(
            agents=[self.get_agent()],
            tasks=[diagnostic_task],
            verbose=True
        )
        
        return crew.kickoff()

if __name__ == "__main__":
    # Example usage
    diagnostician = DiagnosisAgent()
    # Mock data for demonstration
    sample_traceback = "TimeoutError: waiting for selector '#login-button'"
    sample_dom = "<html><body><button id='btn-login-new'>Login</button></body></html>"
    sample_code = "page.click('#login-button')"
    
    print("Running diagnostic analysis...")
    result = diagnostician.analyze_failure(sample_traceback, sample_dom, sample_code)
    print(result)

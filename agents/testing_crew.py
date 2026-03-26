# agents/testing_crew.py
from crewai import Agent, Task, Crew, Process
from crewai.tools import tool
from utils.grok_client import GrokClient
from pages.login_page import LoginPage
from utils.config_loader import Config
from playwright.async_api import async_playwright
import asyncio
import os

config = Config()
grok_client = GrokClient()
llm = grok_client.get_llm()   # Reuse your existing GrokClient

# ====================== Tools ======================
@tool("Execute Playwright Test")
def execute_playwright_test(test_name: str, target_url: str) -> str:
    """Executes a real UI test using the existing Playwright POM framework."""
    try:
        async def run():
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=config.headless)
                context = await browser.new_context()
                page = await context.new_page()
                
                login_page = LoginPage(page)
                await login_page.navigate(target_url)
                await login_page.login()
                
                result = f"✅ {test_name} PASSED → Final URL: {page.url}"
                await browser.close()
                return result
        return asyncio.run(run())
    except Exception as e:
        return f"❌ {test_name} FAILED: {str(e)}"

@tool("Generate New Test Code")
def generate_new_test_code(feature_description: str) -> str:
    """Generates a new Playwright test file or Page Object method using Grok."""
    prompt = f"""
    You are an expert Playwright + Python automation engineer.
    Generate clean, async, POM-style code for the following new feature:
    {feature_description}
    
    Return only the complete Python code (test function or new Page Object method).
    Use the existing BasePage and LoginPage style from the project.
    """
    # Use GrokClient's LLM
    response = llm.call(prompt)   # synchronous call inside tool is fine for CrewAI
    return str(response)

# ====================== Agents (all using your GrokClient) ======================
test_decider = Agent(
    role="Test Strategy Decider",
    goal="Analyze changes and decide the minimal, high-value regression test suite",
    backstory="Senior QA Architect focused on risk-based testing.",
    llm=llm,
    verbose=True,
    allow_delegation=True
)

test_executor = Agent(
    role="Test Executor Agent",
    goal="Reliably run UI tests in real browsers and return clear results",
    backstory="Precise automation engineer specialized in Playwright.",
    tools=[execute_playwright_test],
    llm=llm,
    verbose=True
)

test_generator = Agent(
    role="Test Generator Agent",
    goal="Create new automated tests or Page Object methods when gaps are identified",
    backstory="Creative and experienced test automation developer.",
    tools=[generate_new_test_code],
    llm=llm,
    verbose=True
)

result_analyzer = Agent(
    role="Results Analyst & Improver",
    goal="Analyze outcomes, detect issues, and recommend self-healing or new tests",
    backstory="Detail-oriented QA analyst focused on quality improvement.",
    llm=llm,
    verbose=True
)

# ====================== Tasks ======================
decide_task = Task(
    description="Recent changes: '{changes}'. Decide which tests must run and any potential gaps.",
    expected_output="List of tests to execute + any new test ideas.",
    agent=test_decider
)

execute_task = Task(
    description="Execute the decided tests on URL: {url}",
    expected_output="Detailed PASS/FAIL results for each test.",
    agent=test_executor,
    context=[decide_task]
)

generate_task = Task(
    description="If gaps were found, generate new test code for: {feature_gap}",
    expected_output="Complete, ready-to-use Python test code.",
    agent=test_generator,
    context=[decide_task]
)

analyze_task = Task(
    description="Analyze all execution results and generated code. Provide summary and recommendations.",
    expected_output="Final report with insights and improvement suggestions.",
    agent=result_analyzer,
    context=[execute_task, generate_task]
)

# ====================== The Crew (Swarm) ======================
testing_crew = Crew(
    agents=[test_decider, test_executor, test_generator, result_analyzer],
    tasks=[decide_task, execute_task, generate_task, analyze_task],
    process=Process.hierarchical,      # Manager coordinates the swarm
    manager_llm=llm,
    verbose=True,
    memory=True,
    planning=True
)

async def run_full_agentic_swarm(changes: str = "Login and checkout flows were updated", url: str = None):
    target_url = url or config.base_url
    print("🚀 Starting Agentic Testing Swarm with Grok-powered CrewAI...\n")
    
    result = testing_crew.kickoff(inputs={
        "changes": changes,
        "url": target_url,
        "feature_gap": "Any missing coverage in authentication or new UI elements"
    })
    
    print("\n🎉 Agentic Testing Swarm Finished!")
    print("="*80)
    print(result)
    return result

if __name__ == "__main__":
    asyncio.run(run_full_agentic_swarm())
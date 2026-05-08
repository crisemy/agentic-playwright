# agents/testing_crew.py
from crewai import Agent, Task, Crew, Process
from crewai.tools import tool
from playwright.sync_api import sync_playwright

from pages.login_page import LoginPage
from utils.config_loader import Config
from utils.grok_client import GrokClient
from agents.chaos_agent import ChaosAgent

config = Config()
grok_client = GrokClient()
llm = grok_client.get_llm()   # Reuse your existing GrokClient

# Shared chaos agent instance — controlled by crew tools
_chaos_agent = ChaosAgent(mutation_rate=1.0)

# ====================== Tools ======================
@tool("Execute Playwright Test")
def execute_playwright_test(test_name: str, target_url: str) -> str:
    """Executes a real UI test using the existing Playwright POM framework."""
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=config.headless,
                slow_mo=config.slow_mo
            )
            context = browser.new_context()
            page = context.new_page()

            login_page = LoginPage(page)
            login_page.navigate(target_url)
            login_page.login()

            result = f"✅ {test_name} PASSED -> Final URL: {page.url}"

            page.close()
            context.close()
            browser.close()
            return result
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
    response = llm.call(prompt)
    return str(response)

@tool("Inject Locator Chaos")
def inject_locator_chaos(mutation_rate: float = 1.0) -> str:
    """Inject random locator mutations into the mock server HTML template.

    This simulates a volatile UI where CSS IDs change between test runs,
    forcing the self-healing locator system to recover automatically.

    Args:
        mutation_rate: How many locators to break (0.0 to 1.0). Default 1.0 = break all.

    Returns:
        Summary of mutations applied.
    """
    global _chaos_agent
    _chaos_agent = ChaosAgent(mutation_rate=mutation_rate)
    mutations = _chaos_agent.inject_chaos()
    if not mutations:
        return "No mutations applied."
    return "\n".join(mutations)

@tool("Restore Locator Chaos")
def restore_locator_chaos() -> str:
    """Restore the mock server template to its original state after chaos testing."""
    global _chaos_agent
    _chaos_agent.restore()
    return "Template restored."

# ====================== Agents (all using your GrokClient) ======================
test_decider = Agent(
    role="Test Strategy Decider",
    goal="Analyze changes and decide the minimal, high-value regression test suite",
    backstory="Senior QA Architect focused on risk-based testing.",
    llm=llm,
    verbose=True,
    allow_delegation=True,
    max_rpm=2
)

test_executor = Agent(
    role="Test Executor Agent",
    goal="Reliably run UI tests in real browsers and return clear results",
    backstory="Precise automation engineer specialized in Playwright.",
    tools=[execute_playwright_test],
    llm=llm,
    verbose=True,
    max_rpm=2
)

test_generator = Agent(
    role="Test Generator Agent",
    goal="Create new automated tests or Page Object methods when gaps are identified",
    backstory="Creative and experienced test automation developer.",
    tools=[generate_new_test_code],
    llm=llm,
    verbose=True,
    max_rpm=2
)

result_analyzer = Agent(
    role="Results Analyst & Improver",
    goal="Analyze outcomes, detect issues, and recommend self-healing or new tests",
    backstory="Detail-oriented QA analyst focused on quality improvement.",
    llm=llm,
    verbose=True,
    max_rpm=2
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
    planning_llm=llm,
    verbose=True,
    memory=False,
    planning=False,
    max_rpm=2
)

def run_full_agentic_swarm(
    changes: str = "Login and checkout flows were updated",
    url: str = None,
    inject_chaos: bool = False,
    mutation_rate: float = 1.0
):
    """Run the full agentic testing swarm.

    Args:
        changes: Description of code changes for the decider agent.
        url: Target URL override.
        inject_chaos: If True, inject locator chaos before running tests.
        mutation_rate: Chaos mutation rate (0.0-1.0) if inject_chaos is True.
    """
    global _chaos_agent

    target_url = url or config.base_url

    if inject_chaos:
        print("💥 [ChaosAgent] Injecting locator chaos before swarm run...")
        _chaos_agent = ChaosAgent(mutation_rate=mutation_rate)
        _chaos_agent.inject_chaos()

    print("🚀 Starting Agentic Testing Swarm with Grok-powered CrewAI...\n")

    result = testing_crew.kickoff(inputs={
        "changes": changes,
        "url": target_url,
        "feature_gap": "Any missing coverage in authentication or new UI elements"
    })

    print("\n🎉 Agentic Testing Swarm Finished!")
    print("=" * 80)
    print(result)

    if inject_chaos:
        print("\n♻️  Restoring template after chaos run...")
        _chaos_agent.restore()

    return result

if __name__ == "__main__":
    run_full_agentic_swarm()

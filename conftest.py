# conftest.py (root) — registers global CLI options before arg parsing
import pytest
from agents.predictive_selector import PredictiveSelector
from agents.diagnosis_agent import DiagnosisAgent
from utils.dashboard_manager import DashboardManager
def pytest_addoption(parser):
    """Add --browser option to select browser: chromium, firefox, webkit"""
    parser.addoption(
        "--browser",
        action="store",
        default="chromium",
        help="Browser to run tests with: chromium, firefox, or webkit"
    )

def pytest_collection_modifyitems(session, config, items):
    """Predictive Test Selection using LLM"""
    print("\n🧠 [QA-Cortex] Analyzing git diff to select tests...")
    selector = PredictiveSelector()
    diff = selector.get_git_diff()
    
    if diff and diff.strip():
        # Ask LLM which tests to run
        recommended = selector.select_tests(diff)
        print(f"🎯 [QA-Cortex] Recommended tests: {recommended}")
        
        selected = []
        deselected = []
        for item in items:
            # Check if any part of the item path matches a recommended test
            # Remove whitespace and ensure clean string matching
            if any(rec.strip() in item.nodeid for rec in recommended if rec.strip()):
                selected.append(item)
            else:
                deselected.append(item)
                
        if deselected:
            items[:] = selected
            config.hook.pytest_deselected(items=deselected)
            DashboardManager.log_thought("PredictiveSelector", f"Git diff analyzed. Selected {len(selected)} tests, skipped {len(deselected)}.")
    else:
        print("⏭️ [QA-Cortex] No git diff found. Running all tests.")
        DashboardManager.log_thought("PredictiveSelector", "No code changes detected. Running full test suite.")

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Hook to capture test failures and trigger Root Cause Analysis."""
    outcome = yield
    rep = outcome.get_result()
    
    # We only care about actual test failures
    if rep.when == "call" and rep.failed:
        page = None
        for fixture_name in ["page", "logged_in_page", "api_logged_in_page"]:
            if fixture_name in item.funcargs:
                page = item.funcargs[fixture_name]
                break
                
        dom_snapshot = "DOM snapshot not available"
        if page:
            try:
                dom_snapshot = page.content()
            except Exception:
                pass
                
        # Extract the test code (source)
        try:
            import inspect
            source_lines, _ = inspect.getsourcelines(item.function)
            test_code = "".join(source_lines)
        except Exception:
            test_code = "Could not extract test source."
            
        traceback_str = rep.longreprtext
        
        print(f"\n🚑 [QA-Cortex] Test '{item.name}' failed! Triggering Root Cause Analysis...")
        DashboardManager.log_thought("DiagnosisAgent", f"Analyzing failure in {item.name}...")
        
        try:
            diagnostician = DiagnosisAgent()
            report = diagnostician.analyze_failure(
                traceback=traceback_str, 
                dom_snapshot=dom_snapshot, 
                original_test_code=test_code
            )
            print(f"\n📊 [Diagnosis Report]\n{report}\n")
            DashboardManager.log_thought("DiagnosisAgent", f"RCA Complete for {item.name}:\n{report}")
        except Exception as e:
            print(f"⚠️ RCA Agent failed: {e}")
            DashboardManager.log_thought("DiagnosisAgent", f"Failed to analyze {item.name}: {e}")

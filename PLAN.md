# agentic-playwright — Iteration Plan

---

## Iteration 2

**Branch:** `iteration2-MockAPIServer-APIAuth-ProductsTests`

### Goal
Establish a FastAPI mock server with full auth API, replace the login fixture to use API-based auth, create the `ProductsPage` page object, and write product list tests.

### Tasks

| # | Task | Phases | Status |
|---|---|---|---|
| Task 1 | Phase 1 — Mock API Server | `mock_api/main.py`, `mock_api/products.py`, `mock_api/server.py`, `mock_api/requirements.txt`, `mock_api/templates/inventory.html` | ✅ Done (Iteration 2) |
| Task 2 | Phase 2 — Auth Abstraction | `utils/api_client.py`, `utils/auth.py`, modify `tests/conftest.py` | ✅ Done (Iteration 2) |
| Task 3 | Phase 3 — Products Page Object | `pages/products_page.py` | ✅ Done (Iteration 2) |
| Task 4 | Phase 4 — Products Tests | `tests/test_products.py` | ✅ Done (Iteration 2) |
| Task 5 | Phase 5 — Run & Validate | `pytest tests/test_products.py -v` on chromium + firefox, regression check | ✅ Done (Iteration 2) |
| Task 6 | Phase 6 — README Update | Document mock server setup, how to run it, how to run tests | ✅ Done (Iteration 2) |

---

## Iteration 3

**Branch:** `iteration3-SelfHealing-ChaosAgent`

### Goal
Implement the `grok_client.py` LLM-based locator healing, build an intelligent Chaos Agent that randomly breaks locators before runs, and update README.

### Tasks

| # | Task | Phases | Status |
|---|---|---|---|
| Task 7 | Phase 1 — Self-Healing Implementation | Implement `utils/grok_client.py`, wire `smart_locator()` in `pages/base_page.py` | ✅ Done |
| Task 8 | Phase 2 — Chaos Agent | `agents/chaos_agent.py`, wire into `agents/testing_crew.py` | ✅ Done |
| Task 9 | Phase 3 — Run & Validate | Self-healing + chaos agent end-to-end test | ✅ Done |
| Task 10 | Phase 4 — README Final Update | Full restructure: Architecture diagram, Self-Healing section, Chaos Agent section, API Auth section, Getting Started | ✅ Done |

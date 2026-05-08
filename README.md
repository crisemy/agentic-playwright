# Playwright POM Framework with AI Self-Healing

[![Python](https://img.shields.io/badge/Python-3.12-blue)](https://www.python.org/)
[![Playwright](https://img.shields.io/badge/Playwright-1.58-2EAD33)](https://playwright.dev/python/)
[![pytest](https://img.shields.io/badge/pytest-9.0-0A9EDC)](https://docs.pytest.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A modern, production-grade test automation framework built with **Playwright** (Python), following the **Page Object Model (POM)** pattern, **API-based authentication**, and **AI-powered self-healing** locators.

---

## Features

- **Page Object Model** with clean separation of concerns
- **Dual authentication**: UI login (SauceDemo) and API login (mock server)
- **Fast API login** — ~100ms auth via session cookie, no browser UI involved
- **Mock API server** — self-contained backend for product/cart operations
- **Self-healing locators** powered by Grok AI *(heal_locator stub — active in Iteration 3)*
- **Multi-browser support**: Chromium, Firefox
- **Parallel test execution** with `pytest-xdist`
- **Professional GitHub Actions CI/CD** with matrix strategy

---

## Tech Stack

- **Playwright** (Sync API)
- **Python 3.12**
- **FastAPI** — mock API server for auth + products
- **httpx** — HTTP client for API login
- **pytest** + **pytest-xdist** + **pytest-html**
- **Grok API** (xAI) — for self-healing *(Iteration 3)*
- **YAML** configuration
- **GitHub Actions**

---

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│  Test Machine                                                │
│                                                              │
│  ┌────────────────────┐       ┌───────────────────────────┐  │
│  │  Mock API Server   │◄──────│   Playwright Tests        │  │
│  │  (FastAPI :8000)   │       │   (this framework)        │  │
│  │                    │       │                           │  │
│  │  POST /login       │       │  1. API login → cookie    │  │
│  │  GET  /products    │       │  2. UI: product page      │  │
│  │  POST /cart        │       │  3. Self-healing (Iter 3) │  │
│  │  GET  /inventory.html      │                           │  │
│  └────────────────────┘       └───────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

---

## Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/crisemy/agentic-playwright.git
cd agentic-playwright
```

### 2. Create and activate virtual environment
```bash
python -m venv .venv
source .venv/Scripts/activate  # Windows Git Bash / macOS/Linux
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
pip install -r mock_api/requirements.txt
playwright install chromium firefox --with-deps
```

### 4. Configure environment

Create a `.env` file in the root of the project:
```bash
XAI_API_KEY=your_xai_api_key_here
```

### 5. Start the mock API server

In a separate terminal:
```bash
python -m mock_api.server
```
The server starts at **http://127.0.0.1:8000**.

### 6. Run tests

```bash
# All tests (product tests via mock API, login tests via SauceDemo)
pytest

# Product tests only (requires mock API server running)
pytest tests/test_products.py -v --browser chromium
pytest tests/test_products.py -v --browser firefox

# Login tests only (targets SauceDemo — no mock API needed)
pytest tests/test_login.py -v --browser chromium

# Run with HTML report
pytest --html=reports/report.html --self-contained-html
```

---

## Project Structure

```
agentic-playwright/
├── config/
│   └── config.yaml                # External config (URLs, timeouts, users)
├── mock_api/
│   ├── main.py                    # FastAPI app (login, products, cart endpoints)
│   ├── products.py                # In-memory product catalog
│   ├── server.py                  # uvicorn entry point
│   ├── requirements.txt           # fastapi, uvicorn, jinja2
│   └── templates/
│       └── inventory.html         # Product listing page HTML
├── pages/
│   ├── base_page.py               # Base POM class with self-healing
│   ├── login_page.py               # SauceDemo login page
│   └── products_page.py            # Mock API inventory page
├── tests/
│   ├── conftest.py                # Fixtures: browser, page, api_logged_in_page
│   ├── test_login.py              # Login tests (UI — SauceDemo)
│   └── test_products.py           # Product tests (API auth — mock API)
├── utils/
│   ├── api_client.py              # httpx client for mock API
│   ├── auth.py                    # login_api() / login_ui() helpers
│   ├── config_loader.py           # YAML config loader
│   └── grok_client.py             # Grok API client (self-healing stub)
├── agents/
│   └── testing_crew.py            # CrewAI multi-agent swarm
├── .github/workflows/
│   └── ci.yml                    # CI/CD pipeline
├── requirements.txt
├── pytest.ini
└── README.md
```

---

## Authentication

The framework supports two login strategies:

| Fixture | Target | Auth Method | Use Case |
|---|---|---|---|
| `logged_in_page` | SauceDemo (saucedemo.com) | UI via Playwright | Login form validation, SauceDemo tests |
| `api_logged_in_page` | Mock API (localhost:8000) | API via httpx + cookie injection | Product/cart tests, fast auth |

**Why API login?**
- ~100ms vs ~2-5s per login
- More reliable — no DOM flakiness
- Standard practice for real-world applications in 2026

---

## Fixtures

| Fixture | Scope | Description |
|---|---|---|
| `browser` | session | Single browser instance per session |
| `page` | function | New blank page per test |
| `storage_state` | session | Saved SauceDemo auth state |
| `logged_in_page` | function | SauceDemo login via storage state |
| `api_logged_in_page` | function | Mock API login via httpx + cookie |

---

## CI/CD Status

[![CI](https://github.com/crisemy/agentic-playwright/actions/workflows/ci.yml/badge.svg)](https://github.com/crisemy/agentic-playwright/actions/workflows/ci.yml)

Tests run automatically on every push on Chromium and Firefox.

---

## License

MIT License – Feel free to use this project in your portfolio or commercial work.

---

## Author

**Cristian N.**

QA Engineer with 20+ years of experience in software testing and automation.

Research interests:
- Experimental QA engineering
- QA Architecture
- Reliability testing
- AI-assisted quality assurance

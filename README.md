# Playwright POM Framework with Grok AI

[![Python](https://img.shields.io/badge/Python-3.12-blue)](https://www.python.org/)
[![Playwright](https://img.shields.io/badge/Playwright-1.58-2EAD33)](https://playwright.dev/python/)
[![pytest](https://img.shields.io/badge/pytest-9.0-0A9EDC)](https://docs.pytest.org/)
[![xAI Grok](https://img.shields.io/badge/xAI-Grok-black)](https://x.ai/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A modern, production-grade test automation framework built with **Playwright** (Python), following the **Page Object Model (POM)** pattern and enhanced with **AI-powered self-healing** using **Grok API** from xAI.

---

## Features

- **Page Object Model** with clean separation of concerns
- **Self-healing locators** powered by Grok AI
- **External configuration** via YAML (no hard-coded values)
- **Fast login** using Playwright Storage State
- **Multi-browser support**: Chromium, Firefox, WebKit
- **Parallel test execution** with `pytest-xdist`
- **Grok API integration** for intelligent test decisions and locator healing
- **Professional GitHub Actions CI/CD** with matrix strategy (runs on all 3 browsers)
- Ready for portfolio & real-world projects

---

## Tech Stack

- **Playwright** (Sync API)
- **Python 3.12**
- **pytest** + **pytest-xdist** + **pytest-html**
- **Grok API** (xAI)
- **YAML** configuration
- **GitHub Actions**

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
source .venv/Scripts/activate  # Windows Git Bash
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
playwright install chromium firefox webkit --with-deps
```

### 4. Configure environment

Create a `.env` file in the root of the project:
```bash
XAI_API_KEY=your_xai_api_key_here
```

### 5. Run tests locally
```bash
# Run on default browser (Chromium) in parallel
pytest

# Run with HTML report
pytest --html=reports/report.html --self-contained-html

# Run on specific browser
pytest --browser firefox
pytest --browser webkit
```

---

## Project Structure
```
agentic-playwright/
├── config/config.yaml              # External configuration (URLs, timeouts, etc.)
├── pages/
│   ├── base_page.py                # Base class with self-healing capability
│   └── login_page.py               # Example Page Object
├── tests/
│   ├── conftest.py                 # Fixtures, browser setup, storage state
│   └── test_login.py
├── utils/
│   ├── config_loader.py            # YAML config loader
│   └── grok_client.py              # Grok API client
├── .github/workflows/ci.yml        # Multi-browser CI/CD pipeline
├── requirements.txt
├── pytest.ini
└── README.md
```

---

## Key Capabilities

- **Self-Healing Locators**: Automatically asks Grok for a better locator when an element can't be found
- **Storage State**: Save login once and reuse authentication across tests (faster runs)
- **Agentic Testing**: Grok can decide which tests to run based on recent code changes
- **Multi-Browser CI**: Tests run automatically on Chromium, Firefox, and WebKit on every push

---

## CI/CD Status

[![CI](https://github.com/crisemy/agentic-playwright/actions/workflows/ci.yml/badge.svg)](https://github.com/crisemy/agentic-playwright/actions/workflows/ci.yml)

Tests run automatically on every push and pull request across 3 browsers.

---

## License

MIT License – Feel free to use this project in your portfolio or commercial work.

---

## Author

**Cristian N.**

QA Engineer with 20+ years of experience in software testing and automation.

MSc Candidate in Data Science & Artificial Intelligence.

Research interests:
- Experimental QA engineering
- QA Architecture
- Reliability testing
- AI-assisted quality assurance
- Data-driven software stability analysis
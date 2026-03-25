# Playwright Async POM Framework with Grok AI

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.38%2B-FF4B4B)](https://streamlit.io/)
[![Groq](https://img.shields.io/badge/Groq-Llama%203.3-orange)](https://groq.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A modern, production-grade **asynchronous** test automation framework built with **Playwright** (Python), following the **Page Object Model (POM)** pattern and enhanced with **AI-powered self-healing** using **Grok API** from xAI.

---

## Features

- **Fully Asynchronous** architecture (`async_playwright`)
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

- **Playwright** (Async)
- **Python 3.12**
- **pytest** + **pytest-xdist** + **pytest-html**
- **Grok API** (xAI)
- **YAML** configuration
- **GitHub Actions**

---

## Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/playwright-pom-grok-async.git
cd playwright-pom-grok-async
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
playwright install chromium firefox webkit --with-deps
```

### 3. Configure environment
```bash
cp .env.example .env
```

Note: Add your Grok API key in the .env file (You should create a .env file in the root of your project): 
```bash
XAI_API_KEY=your_xai_api_key_here
```

### 4. Run tests locally
```bash
# Run on default browser (Chromium) in parallel
pytest

# Run on specific browser
pytest --browser firefox
pytest --browser webkit

# Run on all browsers sequentially
pytest --browser chromium --browser firefox --browser webkit
```

## Project Structure
```bash
playwright-pom-grok-async/
├── config/config.yaml              # External configuration
├── pages/
│   ├── base_page.py                # Base class with self-healing
│   └── login_page.py               # Example Page Object
├── tests/
│   ├── conftest.py                 # Async fixtures + storage state
│   └── test_login.py
├── utils/
│   ├── config_loader.py
│   └── grok_client.py              # Grok API client
├── auth/storage_state.json         # Saved login state (auto-generated)
├── .github/workflows/ci.yml        # Multi-browser CI/CD
├── screenshots/
├── reports/
├── requirements.txt
├── pytest.ini
└── README.md
```
## Key Capabilities
- Self-Healing Locators: Automatically asks Grok for better locators when elements change
- Storage State: Login once, reuse authentication across tests (much faster)
- Agentic Testing: Grok can decide which tests to run based on code changes
- Multi-Browser CI: Runs tests automatically on Chromium, Firefox, and WebKit

## CI/CD Status
<img src="https://github.com/yourusername/playwright-pom-grok-async/workflows/Playwright%20Async%20Tests%20-%20Multi-Browser%20CI/badge.svg" alt="CI Status">

Tests run automatically on every push and pull request across 3 browsers.


## License
MIT License – Feel free to use this project in your portfolio or commercial work.

## Author

Cristian N.

QA Engineer with 20+ years of experience in software testing and automation.

MSc Candidate in Data Science & Artificial Intelligence.

Research interests include:

* Experimental QA engineering
* QA Architecture
* Reliability testing
* AI-assisted quality assurance
* Data-driven software stability analysis
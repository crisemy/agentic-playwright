# conftest.py (root) — registers global CLI options before arg parsing
def pytest_addoption(parser):
    """Add --browser option to select browser: chromium, firefox, webkit"""
    parser.addoption(
        "--browser",
        action="store",
        default="chromium",
        help="Browser to run tests with: chromium, firefox, or webkit"
    )

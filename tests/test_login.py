# tests/test_login.py
import pytest
from pages.login_page import LoginPage

def test_successful_login(page):
    """Test successful login with standard user"""
    login_page = LoginPage(page)
    login_page.navigate()
    login_page.login()
    assert "inventory" in page.url
    login_page.take_screenshot("login_success")

def test_locked_user(page):
    """Test locked user error (does not use storage state)"""
    login_page = LoginPage(page)
    login_page.navigate()
    login_page.login(username="locked_out_user", password="secret_sauce")
    
    assert "Epic sadface" in login_page.error_msg.inner_text()
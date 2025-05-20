import pytest
from playwright.sync_api import sync_playwright

@pytest.fixture(scope="function")
def page():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://www.letskodeit.com/practice")
        try:
            yield page
        finally:
            browser.close()

def test_01_enter_your_name(page):
    """01 - Enter 'Naren' in name field"""
    page.locator("input[placeholder='Enter Your Name']").fill("Naren")
    assert page.locator("input[placeholder='Enter Your Name']").input_value() == "Naren"

def test_02_hide_show(page):
    """02 - Hide and Show textbox"""
    page.locator("input#hide-textbox").click()
    page.locator("input#show-textbox").click()
    assert page.locator("input#displayed-text").is_visible()


def test_03_enable_disable(page):
    """03 - Enable and Disable"""
    page.locator("input[value='Enable']").click()
    page.locator("input[value='Disable']").click()
    assert page.locator("input#enabled-example-input").is_disabled()


def test_04_multi_select(page):
    """04 - Select 'apple' from multi-select"""
    page.locator("#multiple-select-example").select_option("apple")
    assert page.locator("#multiple-select-example").evaluate("e => e.value") == "apple"

def test_05_dropdown_select(page):
    """05 - Select 'honda' from dropdown"""
    page.locator("#carselect").select_option("honda")
    assert page.locator("#carselect").evaluate("e => e.value") == "honda"

def test_06_auto_suggest(page):
    """06 - Fill 'How?' in auto-suggest"""
    auto_input = page.locator("input#autosuggest")
    auto_input.fill("How?")
    auto_input.press("Enter")
    assert auto_input.input_value() == "How?"


import re
from playwright.sync_api import Playwright, sync_playwright, expect


def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://www.letskodeit.com/practice")
    page.get_by_role("textbox", name="Enter Your Name").click()
    page.get_by_role("textbox", name="Enter Your Name").fill("Naren")
    page.get_by_role("textbox", name="Enter Your Name").press("Enter")
    page.get_by_role("button", name="Hide").click()
    page.get_by_role("button", name="Show").click()
    page.get_by_role("button", name="Enable").click()
    page.get_by_role("button", name="Disable").click()
    page.locator("#multiple-select-example").select_option("apple")
    page.locator("#carselect").select_option("honda")
    page.get_by_role("textbox", name="Start Typing...").click()
    page.get_by_role("textbox", name="Start Typing...").fill("How?")
    page.get_by_role("textbox", name="Start Typing...").press("Enter")
    page.close()

    # ---------------------
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)

import os
import pytest
from playwright.sync_api import sync_playwright, Error

def test_google_screenshot():
    screenshot_path = "example.png"
    browser = None

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            page.goto("https://www.google.com")
            page.screenshot(path=screenshot_path)
            print("Screenshot was taken.")
    except Error as e:
        pytest.fail(f"[Possible Playwright Error] {e}")
    except Exception as e:
        pytest.fail(f"[Unexpected Error with Script] {e}")
    finally:
        if browser:
            try:
                browser.close()
            except Exception:
                pass  # browser may not have opened properly

    # Formal test assertion
    assert os.path.exists(screenshot_path), "Screenshot was not created."



import re
from playwright.sync_api import Page, expect

def test_has_title(page: Page):
    page.goto("https://playwright.dev/")
    expect(page).to_have_title(re.compile("Playwright"))

def test_get_started_link(page: Page):
    page.goto("https://playwright.dev/")
    page.get_by_role("link", name="Get started").click()
    expect(page.get_by_role("heading", name="Installation")).to_be_visible()
    
def test_playwright_search_input(page: Page):
    page.goto("https://playwright.dev/python")
    page.get_by_role("button", name="Search").click()
    page.get_by_role("searchbox").fill("testing")
    expect(page.get_by_role("searchbox")).to_have_value(re.compile("testing"))
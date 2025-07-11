from playwright.sync_api import sync_playwright

# playwright codegen <URL>

import pdb

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        url = 'http://yahoo.com'
        page.goto(url)

        page.wait_for_url(url=url, wait_until="networkidle")
        page.locator("#MainContent_MasterCombo_ob_CboMasterComboTB").click()
        page.get_by_text("SOME VALUE").click()

        page.locator("input[name=\"ctl00$MainContent$txtStartDate0\"]").fill("Some text")

        # page.screenshot(path="screenshot.png")

        print(page.title())
        browser.close()


if __name__ == "__main__":
    main()
from playwright.sync_api import sync_playwright

# playwright codegen <URL>

import pdb

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        url = 'http://dbsportal/Home/UTILITIES/Restore_database.aspx'
        page.goto(url)

        page.wait_for_url(url=url, wait_until="networkidle")
        page.locator("#MainContent_MasterCombo_ob_CboMasterComboTB").click()
        page.get_by_text("MUREXDW ( PWSELSOPSDW003,1433)").click()

        page.wait_for_url(url=url, wait_until="networkidle")
        page.locator("input[name=\"ctl00$MainContent$ComboBox1$ob_CboComboBox1TB\"]").click()
        page.locator("b").filter(has_text="FinancingMurex").click()

        page.wait_for_url(url=url, wait_until="networkidle")
        page.locator("input[name=\"ctl00$MainContent$ComboBox2$ob_CboComboBox2TB\"]").click()
        page.get_by_text("MUREXDWSQLDEV").click()

        page.locator("input[name=\"ctl00$MainContent$ComboBox3$ob_CboComboBox3TB\"]").click()
        page.get_by_role("listitem").filter(has_text="FinancingMurexFinancingMurex").locator("b").click()
        page.locator("input[name=\"ctl00$MainContent$ComboBox3$ob_CboComboBox3TB\"]").press("Enter")

        page.locator("input[name=\"ctl00$MainContent$txtStartDate0\"]").fill("financingdev@mlp.com")

        # page.locator(".ob_iBOv").first.click()
        page.screenshot(path="screenshot.png")

        pdb.set_trace()
        print(page.title())
        browser.close()


if __name__ == "__main__":
    main()
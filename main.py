from playwright.sync_api import sync_playwright, Playwright


def get_code(order_number, size, first_name, last_name, phone_number, email):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless = False, slow_mo=500)
        page = browser.new_page()
        page.goto("https://szybkiezwroty.pl/en/PacketaGroup")
        page.get_by_role("button", name= "ODRZUĆ WSZYSKO").click()
        page.locator("#orderNumber").fill("95814250")
        page.locator("#description").fill(order_number)
        page.locator('div[aria-label="Reason for returning"]').click()
        page.get_by_role("option", name="Other reason").click()
        page.locator("#personal-name").fill(str(first_name))
        page.locator("#personal-lastname").fill(str(last_name))
        page.locator("#personal-number").fill(str(phone_number))
        page.locator("#personal-email").fill(str(email))
        if size != "s":
            page.get_by_text("Edit").nth(1).click()
            if size == "m":
                page.get_by_text("Medium").click()
            elif size == "l":
                page.get_by_text("Large").click()
            page.get_by_text("Save").click

### input only for testing purposes, to not create unnecessary return shipments
        input("pressing enter submits the return")
        page.get_by_text("Submit return").click()
        code = page.locator('span[aria-labelledby="qrCodeTitle"]').inner_text().strip()
        browser.close()
        return code


if __name__ == "__main__":
    print(get_code("V-12345678","s", "Martin", "Okruhlica", 734930294, "info@najada.cz"))
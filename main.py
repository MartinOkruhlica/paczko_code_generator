from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import time

app = FastAPI()

PAGE_TIMEOUT_MS = 20_000
NAVIGATION_TIMEOUT_MS = 20_000
MAX_RETRIES = 2


class CodeRequest(BaseModel):
    order_number: str
    size: str
    first_name: str
    last_name: str
    phone_number: str
    email: EmailStr

def get_code(order_number, size, first_name, last_name, phone_number, email):
    attempt = 0
    last_error = None

    while attempt <= MAX_RETRIES:
        attempt += 1
        browser = None

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(
                    headless=True,
                    args=["--no-sandbox", "--disable-dev-shm-usage"]
                )

                context = browser.new_context()
                page = context.new_page()

                page.set_default_timeout(PAGE_TIMEOUT_MS)
                page.set_default_navigation_timeout(NAVIGATION_TIMEOUT_MS)

                page.goto("https://szybkiezwroty.pl/en/PacketaGroup")

                try:
                    page.get_by_role("button", name="ODRZUĆ WSZYSKO").click(timeout=5000)
                except Exception:
                    pass

                page.locator("#orderNumber").fill(order_number)
                page.locator("#description").fill(order_number)

                page.locator('div[aria-label="Reason for returning"]').click()
                page.get_by_role("option", name="Other reason").click()

                page.locator("#personal-name").fill(first_name)
                page.locator("#personal-lastname").fill(last_name)
                page.locator("#personal-number").fill(phone_number)
                page.locator("#personal-email").fill(email)

                if size != "s":
                    page.get_by_text("Edit").nth(1).click()
                    if size == "m":
                        page.get_by_text("Medium").click()
                    elif size == "l":
                        page.get_by_text("Large").click()
                    page.get_by_text("Save").click()
                page.get_by_text("Submit return").click()
                code_locator = page.locator('span[aria-labelledby="qrCodeTitle"]')
                code_locator.wait_for(timeout=PAGE_TIMEOUT_MS)
                code = code_locator.inner_text().strip()
                return code

        except PlaywrightTimeoutError as e:
            last_error = f"Timeout error: {str(e)}"

        except Exception as e:
            last_error = f"Unexpected error: {str(e)}"

        finally:
            if browser:
                try:
                    browser.close()
                except Exception:
                    pass
        time.sleep(1)
    raise RuntimeError(last_error or "Unknown failure")

@app.post("/pl-return-shipment-code")
def code_endpoint(payload: CodeRequest):
    try:
        code = get_code(
            payload.order_number,
            payload.size,
            payload.first_name,
            payload.last_name,
            payload.phone_number,
            payload.email
        )

        return {"code": code}
    except RuntimeError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate return code: {str(e)}"
        )
import re
from playwright.sync_api import Playwright, sync_playwright, expect


def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://patentcenter.uspto.gov/")
    page.get_by_role("link", name="Sign in").click()
    page.goto("https://auth.uspto.gov/oauth2/aus4qv50b0BRaFZMp4h7/v1/authorize?client_id=0oab0p19a3U5fd4mP4h7&code_challenge=0NEiKEzVfLw91MqCFoFw5I0S1S1-4hbPa3BnUflqw_k&code_challenge_method=S256&nonce=FlqywoVV3x2saS2VV8wQr6uvEQ7PYT5D1UkcMhTIl0pAeyaBMuJR6hNtr3XGRaMP&redirect_uri=https%3A%2F%2Fpatentcenter.uspto.gov%2Flogin%2Fcallback&response_type=code&state=TXY9MJ4frGp825F7tR9wrwGpMGWVVOd3HMLatZFlxqSSnzQoHiKqQ5JC1G4MccH9&scope=openid%20profile%20offline_access%20uspto.patent.patentcenter.application.read%20uspto.patent.patentcenter.application.write")
    page.get_by_role("textbox", name="Email address").click()
    page.get_by_role("textbox", name="Email address").fill("DSfiling@porus-ip.com")
    page.get_by_role("button", name="下一步").click()
    page.get_by_role("textbox", name="密码").click()
    page.get_by_role("textbox", name="密码").fill("metisIP@2023")
    page.get_by_role("button", name="验证").click()
    page.get_by_role("link", name="选择输入 Okta Verify 应用程序中的代码。").click()
    page.get_by_role("textbox", name="从Okta Verify 应用输入代码").fill("629223")
    page.get_by_role("button", name="验证").click()
    page.goto("https://patentcenter.uspto.gov/")
    page.get_by_role("button", name="description New submission").click()
    page.get_by_role("button", name="description New submission").click()
    page.get_by_role("link", name="Utility Nonprovisional").click()
    page.locator("#drDwn_practitioner").select_option("1: Object")
    page.get_by_role("link", name="Select").nth(1).click()
    page.get_by_text("Browse files").click()
    page.get_by_text("Browse files").set_input_files("2026-06-25-ADS-20664-0113US00.pdf")
    page.get_by_role("button", name="Continue").click()
    page.get_by_text("Browse files").click()
    page.get_by_role("button", name="Browse files").set_input_files(["Signed_Declaration-6M201-H001US00.pdf", "2026-07-10-Spec-6M201-H001US00.docx", "2026-07-10-Transmittal-6M201-H001US00.pdf", "2026-07-10-FIGS-6M201-H001US00.pdf", "2026-07-10-POA-6M201-H001US00.pdf"])
    page.get_by_role("button", name="Save progress").click()

    # ---------------------
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)

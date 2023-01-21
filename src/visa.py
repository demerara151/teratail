"""
selenium 入力ボックスの要素が見つからない
https://teratail.com/questions/2ir4j74anuefal#reply-mxmine38u4ivvl)
"""
# type: ignore
import asyncio

from playwright.async_api import async_playwright

url = (
    "https://usa.visa.com/support/consumer/travel-support/"
    "exchange-rate-calculator.html"
)
amount = "58742"


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(url)
        await page.get_by_placeholder("Enter amount").fill(amount)

        await page.get_by_role(
            "button", name="Open from currency list drop down menu."
        ).click()
        await page.locator("#listbox-item-2").click()
        await page.get_by_role(
            "button", name="Open to currency list drop down menu."
        ).click()
        await page.locator("#listbox-item-0").click()

        await page.get_by_role("button", name=" Calculate Conversion ").click()

        print(await page.locator("h2.vs-h2").nth(1).text_content())
        print(await page.locator("dm-calculator div").nth(45).text_content())

        await browser.close()


asyncio.run(main())

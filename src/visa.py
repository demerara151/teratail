# type: ignore
"""
selenium 入力ボックスの要素が見つからない
https://teratail.com/questions/2ir4j74anuefal#reply-mxmine38u4ivvl)
"""
import asyncio
from dataclasses import dataclass

from playwright.async_api import async_playwright
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chromium.options import ChromiumOptions
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager


@dataclass(slots=True)
class Spider:
    url: str = (
        "https://usa.visa.com/support/consumer/travel-support/"
        "exchange-rate-calculator.html"
    )

    def fetch_with_selenium(self, amount: int) -> None:
        """
        Fetch the data using selenium.
        """
        service: Service = Service(
            executable_path=ChromeDriverManager().install()
        )
        options: ChromiumOptions = ChromiumOptions()
        options.add_argument("headless")

        browser = webdriver.Chrome(service=service, options=options)
        browser.implicitly_wait(5)
        browser.get(self.url)

        # Get the shadow root from shadow DOM
        shadow = browser.find_element(By.XPATH, "//dm-calculator").shadow_root

        # Input number of amount
        shadow.find_element(By.ID, "input_amount_paid").send_keys(str(amount))

        # Select country
        shadow.find_element(
            By.CSS_SELECTOR, "#combobox-from > button:nth-child(2)"
        ).click()
        shadow.find_element(By.CSS_SELECTOR, "li#listbox-item-2").click()

        shadow.find_element(
            By.CSS_SELECTOR, "#combobox-to > button:nth-child(2)"
        ).click()
        shadow.find_element(By.CSS_SELECTOR, "li#listbox-item-0").click()

        # Press the calculation button
        shadow.find_element(By.CSS_SELECTOR, ".vs-btn-primary").click()

        # Calculation result
        result: str = shadow.find_element(By.CLASS_NAME, "vs-h2").text
        print(f"\n{result}\n")

        # Additional information
        for i in range(2, 4):
            selector: str = f"p.vs-margin-0:nth-child({i})"
            print(shadow.find_element(By.CSS_SELECTOR, selector).text)
        print(
            shadow.find_element(By.CSS_SELECTOR, "p.vs-text:nth-child(4)").text
        )

        print("\nSuccess!")

        browser.close()

    async def fetch_with_pw(self, amount: int) -> None:
        """
        Fetch the data using playwright.
        """
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.goto(self.url)
            await page.get_by_placeholder("Enter amount").fill(str(amount))

            await page.get_by_role(
                "button", name="Open from currency list drop down menu."
            ).click()
            await page.locator("#listbox-item-2").click()
            await page.get_by_role(
                "button", name="Open to currency list drop down menu."
            ).click()
            await page.locator("#listbox-item-0").click()

            await page.get_by_role(
                "button", name=" Calculate Conversion "
            ).click()

            print(await page.locator("h2.vs-h2").nth(1).text_content())
            print(
                await page.locator("dm-calculator div").nth(45).text_content()
            )

            await browser.close()


if __name__ == "__main__":
    spider = Spider()
    # spider.fetch_with_selenium(10000)
    asyncio.run(spider.fetch_with_pw(10000))

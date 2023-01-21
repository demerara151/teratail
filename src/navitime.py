"""
Pythonでselenium 次のページをクリック
https://teratail.com/questions/pgd3cgpf1toqit
"""
# type: ignore
import asyncio

from playwright.async_api import async_playwright

url: str = "https://www.navitime.co.jp/category/0805/11324/"


async def main(url: str) -> None:
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(url)
        # find out total pages
        # add query to url
        # select url element
        # extract and gather url
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main(url))

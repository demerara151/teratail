"""
Pythonでselenium 次のページをクリック
https://teratail.com/questions/pgd3cgpf1toqit
"""
import asyncio

from playwright.async_api import async_playwright

url: str = "https://www.navitime.co.jp/category/0805/11324?page={}"


async def main(url: str) -> None:
    page_number: int = 1
    query: str = "poi?spot"
    result: list[str] = []
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        while True:
            res = await page.goto(url.format(page_number))

            if res is None or res.status == 404:
                print("End of the pages.")
                await browser.close()
                break
            elif res is not None and res.status == 200:
                result.extend(
                    [
                        link
                        for link in [
                            await anchor.get_attribute("href")
                            for anchor in await page.get_by_role("link").all()
                        ]
                        if link is not None
                        if query in link
                    ]
                )
                page_number += 1
                continue
            else:
                print("[Error]: Something's happened.")
                await browser.close()
                break

        print(result)


if __name__ == "__main__":
    asyncio.run(main(url))

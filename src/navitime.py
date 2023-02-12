"""
Pythonでselenium 次のページをクリック
https://teratail.com/questions/pgd3cgpf1toqit
"""
import asyncio
from dataclasses import dataclass, field
from pprint import pprint

import httpx
from playwright.async_api import async_playwright
from selectolax.parser import HTMLParser


@dataclass(slots=True)
class Spider:
    url: str = "https://www.navitime.co.jp/category/0805/11324?page={}"
    page_number: int = 1
    query: str = "poi?spot"
    result: list[str] = field(default_factory=list[str])
    limit: int = 200  # ページの最大数の想定

    async def fetch(self) -> None:
        """
        httpx と selectolax を使う手法

        URL のページナンバーを 1 つずつ増やしていって 404 が返ってきたらプロセスを終了する
        """
        async with httpx.AsyncClient(
            headers={
                "Accept": "text/html",
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; rv:109.0)"
                    " Gecko/20100101 Firefox/109.0"
                ),
            }
        ) as client:
            while self.page_number < self.limit:
                url = self.url.format(self.page_number)

                # 初めに HEAD request を投げてステータスコードを確認
                response_header: httpx.Response = await client.head(url)
                if response_header.status_code == 404:
                    print("End of the pages.")
                    break
                elif response_header.status_code == 200:
                    response: httpx.Response = await client.get(url)
                    tree = HTMLParser(response.content)
                    self.result.extend(
                        [
                            link
                            for link in [
                                node.attributes["href"]
                                for node in tree.css("a")
                            ]
                            if link is not None
                            if self.query in link
                        ]
                    )
                    self.page_number += 1
                    continue
                else:
                    print(f"Status: {response_header.status_code}")
                    break

        pprint(self.result)

    async def crawl(self) -> None:
        """
        playwright を使う手法

        URL のページナンバーを 1 つずつ増やしていって 404 が返ってきたらブラウザを閉じる
        """
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()

            # while True はちょっと怖いので
            while self.page_number < self.limit:
                res = await page.goto(self.url.format(self.page_number))

                if res is None or res.status == 404:
                    print("End of the pages.")
                    await browser.close()
                    break
                elif res and res.status == 200:
                    self.result.extend(
                        [
                            link
                            for link in [
                                await anchor.get_attribute("href")
                                for anchor in await page.get_by_role(
                                    "link"
                                ).all()
                            ]
                            if link is not None
                            if self.query in link
                        ]
                    )
                    self.page_number += 1
                    continue
                else:
                    print(
                        "[Error]: Something's happened.\n"
                        f" Status: {res.status}"
                    )
                    await browser.close()
                    break

            pprint(self.result)


if __name__ == "__main__":
    spider = Spider()
    asyncio.run(spider.fetch())
    # asyncio.run(spider.crawl())

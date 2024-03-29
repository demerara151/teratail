"""
[Python selenium]　driver.find_elementsによる<button>要素の読込
https://teratail.com/questions/s25iuek3rwu5s9
"""
import json
import time
from dataclasses import dataclass
from typing import Any

import httpx
from selectolax.parser import HTMLParser
from selenium import webdriver
from selenium.webdriver.common.by import By


class ScriptNotFoundError(Exception):
    ...


@dataclass(slots=True, frozen=True)
class YahooComment:
    base_url: str = "https://news.yahoo.co.jp"

    @property
    def _client(self) -> httpx.Client:
        return httpx.Client(
            base_url=self.base_url,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0)"
                    " Gecko/20100101 Firefox/119.0"
                )
            },
        )

    @property
    def _driver(self) -> webdriver.Chrome:
        # options = webdriver.ChromeOptions()
        # options.add_argument("headless=new")
        driver = webdriver.Chrome()
        driver.implicitly_wait(10)
        return driver

    def fetch(self, url: str) -> HTMLParser:
        "Fetch HTML and return HTML tree."
        with self._client as client:
            resp = client.get(url)
            return HTMLParser(resp.text)

    def get_comment_url(self, news_url: str) -> str:
        "Parse json script and return comment page url."
        tree = self.fetch(news_url)

        if node := tree.css_first("body > script:nth-child(6)"):
            # `window.__PRELOADED_STATE__ = ` を prefix として除外しても効果がなかったため
            page_data = json.loads(node.text().split(sep="= ")[1])
            return page_data["commentShort"]["commentUrl"]
        else:
            raise ScriptNotFoundError("No json script founds.")

    def get_comments(self, comment_url: str) -> None:
        "Parse json script and print comments."
        tree = self.fetch(comment_url)

        if node := tree.css_first("body > script:nth-child(4)"):
            json_data = json.loads(node.text().split(sep="= ")[1])

            # コメンテーターによるコメント
            commentator_comments: list[dict[str, Any]] = json_data[
                "commentFull"
            ]["commentatorComment"]
            for comment in commentator_comments:
                print(comment["text"], sep="\n")

            # ユーザーによるコメント
            user_comment_list: list[dict[str, Any]] = json_data["commentFull"][
                "userCommentList"
            ]
            for comment in user_comment_list:
                print(comment["text"], sep="\n")
        else:
            raise ScriptNotFoundError("No json script founds.")

    def get_reply(self, url: str):
        # cSpell: disable
        "Get reply comments by clicking reply buttons with selenium."
        with self._driver as driver:
            driver.get(f"{self.base_url}/{url}")
            # 問題の箇所
            buttons = driver.find_elements(
                By.CSS_SELECTOR, "article > div > div > button"
            )
            for i, button in enumerate(buttons):
                if i % 2 == 0:
                    time.sleep(0.2)
                    button.click()
            # ページソースの取得が速すぎると最後の返信が展開されていない事があるため
            time.sleep(1)
            html = driver.page_source

        # 取得したソースから返信部分のコメントを取得
        tree = HTMLParser(html)
        reply_nodes = tree.css(".ReplyCommentItem__Comment-cBkaA-D.gdnYJE")
        for node in reply_nodes:
            print(node.text())


if __name__ == "__main__":
    news_url = "https://news.yahoo.co.jp/pickup/6481785"
    yahoo = YahooComment()
    url = yahoo.get_comment_url(news_url)
    print(url)
    yahoo.get_reply(url)

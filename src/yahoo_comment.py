"""
[Python selenium]　driver.find_elementsによる<button>要素の読込
https://teratail.com/questions/s25iuek3rwu5s9
"""
import json
from dataclasses import dataclass
from typing import Any

import httpx
from selectolax.parser import HTMLParser


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


if __name__ == "__main__":
    news_url = "https://news.yahoo.co.jp/pickup/6479600"
    yahoo = YahooComment()
    url = yahoo.get_comment_url(news_url)
    print(url)
    yahoo.get_comments(url)

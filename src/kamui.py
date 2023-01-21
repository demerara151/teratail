"""
seleniumでスクレイピング。ある部分が取れない
https://teratail.com/questions/kwcuzshawbpplv
"""
import asyncio

import httpx

# 開発者ツールのネットワークタブから、API のアドレスを取得
url: str = (
    "https://app.kamuitracker.com/kamunavi/v1/channels/"
    "search?date=20230121&page={}"
)
pages = range(1, 1593)


async def fetch(page: int) -> None:
    "該当の URL にリクエストを送信し、返ってきた値を TSV に書き込む"

    async with httpx.AsyncClient(
        headers={
            "Accept": "application/json",
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; rv:109.0)"
                " Gecko/20100101 Firefox/109.0"
            ),
        },
        timeout=10.0,
    ) as client:
        res = await client.get(url.format(page))
        res.raise_for_status()
        json = res.json()
        await asyncio.sleep(1)

        # チャンネル名にコンマが含まれていることがあるため、CSV ではなく TSV を使用
        with open(f"database/{page:04}_ranking.tsv", "w") as f:
            for item in json["item"]:
                f.write(f'{item["rank"]}\t{item["title"]}\n')


async def main() -> None:
    """
    並列処理で加速
    複数のファイルに分かれることになるが、後から結合すればいい
    """
    async with asyncio.TaskGroup() as tg:
        for page in pages:
            tg.create_task(fetch(page))


if __name__ == "__main__":
    asyncio.run(main())

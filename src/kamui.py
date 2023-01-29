"""
seleniumでスクレイピング。ある部分が取れない
https://teratail.com/questions/kwcuzshawbpplv
"""
import asyncio
import csv

import httpx

# 開発者ツールのネットワークタブから、API のアドレスを取得
url: str = (
    "https://app.kamuitracker.com/kamunavi/v1/channels/"
    "search?date=20230121&page={}"
)
pages = range(1, 1593)


async def fetch(page: int) -> list[tuple[int, str]]:
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

        return [(item["rank"], item["title"]) for item in json["item"]]


async def main() -> list[list[tuple[int, str]]]:
    results: list[asyncio.Task[list[tuple[int, str]]]] = []
    async with asyncio.TaskGroup() as tg:
        for page in pages:
            task = tg.create_task(fetch(page))
            results.append(task)
    return [task.result() for task in results]


if __name__ == "__main__":
    results = asyncio.run(main())
    results.sort()
    for res in results:
        with open("ranking.csv", "a", newline="") as file:
            # use tab string instead of comma
            # because some channel name has comma
            csv_out = csv.writer(file, delimiter="\t")
            csv_out.writerow(["rank", "channel"])
            csv_out.writerows(res)

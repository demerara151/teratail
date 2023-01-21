"[seleniumでスクレイピング。ある部分が取れない](https://teratail.com/questions/kwcuzshawbpplv)"
import asyncio

import httpx

url: str = (
    "https://app.kamuitracker.com/kamunavi/v1/channels/"
    "search?date=20230121&page={}"
)
pages = range(100, 201)


async def fetch(page: int) -> None:
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
        # await asyncio.sleep(0.5)

        with open(f"database/{page:04}_ranking.tsv", "w") as f:
            for item in json["item"]:
                f.write(f'{item["rank"]}\t{item["title"]}\n')


async def main() -> None:
    async with asyncio.TaskGroup() as tg:
        for page in pages:
            tg.create_task(fetch(page))


if __name__ == "__main__":
    asyncio.run(main())

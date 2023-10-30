"""
seleniumでスクレイピング。ある部分が取れない
https://teratail.com/questions/kwcuzshawbpplv
"""
import asyncio
from dataclasses import dataclass

import httpx


@dataclass(slots=True, frozen=True)
class Kamui:
    pages = range(1, 1593)

    async def fetch(self, page_number: int) -> list[tuple[int, str]]:
        # cSpell: disable
        async with httpx.AsyncClient(
            headers={
                "Accept": "application/json",
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; rv:109.0)"
                    " Gecko/20100101 Firefox/119.0"
                ),
            },
            timeout=10.0,
            base_url="https://app.kamuitracker.com",
        ) as client:
            response = await client.get(
                url="kamunavi/v1/channels/search",
                params={"date": "20231030", "page": page_number},
            )
            response.raise_for_status()
            json = response.json()
            await asyncio.sleep(1)

            return [(item["rank"], item["title"]) for item in json["item"]]

    async def main(self) -> list[list[tuple[int, str]]]:
        async with asyncio.TaskGroup() as tg:
            tasks = [
                tg.create_task(self.fetch(page_number))
                for page_number in self.pages
            ]
        return [task.result() for task in tasks]


if __name__ == "__main__":
    import csv

    kamui = Kamui()
    results = asyncio.run(kamui.main())
    results.sort()

    with open("ranking.csv", "a", newline="") as file:
        # use tab string instead of comma
        # because some channel name has comma
        csv_writer = csv.writer(file, delimiter="\t")
        csv_writer.writerow(["rank", "channel"])

        [csv_writer.writerows(result) for result in results]

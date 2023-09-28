"""
python スクレイピング　取得できないclassがある場合
https://teratail.com/questions/4q669m13gir32t
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pprint import pprint
from typing import Any

import httpx
from pydantic import BaseModel


class Project(BaseModel):
    id: int
    collected_money: int
    collected_supporter: int
    expiration_date: int
    time_left_label: str
    percent: int
    image_url: str
    title: str
    url: str
    is_new: bool
    is_store_opening: bool
    has_target_money: bool
    has_expiration: bool
    is_accepting_support: bool
    hide_collected_money: bool
    returns: list[Any]
    is_new_store_opening: bool


class Pagination(BaseModel):
    page: int
    per_page: int
    total: int


class Response(BaseModel):
    projects: list[Project]
    pagination: Pagination


@dataclass(slots=True)
class Makuake:
    _base_url: str = (
        "https://api.makuake.com/v2/projects"
        "?page={}&per_page={}&type=most-funded"
    )
    _headers: dict[str, str] = field(
        default_factory=lambda: {
            "Accept": "application/json",
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; rv:109.0)"
                " Gecko/20100101 Firefox/109.0"
            ),
        },
    )

    def fetch(self, *, page: int = 1, per_page: int = 15) -> httpx.Response:
        if not 0 < per_page < 101:
            raise ValueError(f"Item number should be 1 to 100: {per_page = }")
        url = self._base_url.format(page, per_page)
        response = httpx.get(url=url, headers=self._headers)
        response.raise_for_status()
        return response

    def parse_json(self, resp: httpx.Response) -> list[dict[str, str]]:
        json = Response(**resp.json())
        return [
            {
                "タイトル": project.title,
                "応援購入総額": f"{project.collected_money:,}円",
                "サポーター": f"{project.collected_supporter:,}人",
            }
            for project in json.projects
        ]


if __name__ == "__main__":
    makuake = Makuake()
    response = makuake.fetch(page=3, per_page=100)
    database = makuake.parse_json(response)
    pprint(database)

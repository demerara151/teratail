"""
python スクレイピング　取得できないclassがある場合
https://teratail.com/questions/4q669m13gir32t
"""
from __future__ import annotations

from dataclasses import dataclass
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
    url: str

    def fetch(self) -> list[dict[str, str]]:
        res = httpx.get(self.url)
        res.raise_for_status()
        json = Response(**res.json())
        results: list[dict[str, str]] = []
        for project in json.projects:
            project_info = {
                "タイトル": project.title,
                "応援購入総額": f"{project.collected_money:,}円",
                "サポーター": f"{project.collected_supporter:,}人",
            }
            results.append(project_info)
        return results


if __name__ == "__main__":
    url: str = (
        "https://api.makuake.com/v2/projects"
        "?page=1&per_page=100&type=most-funded"
    )
    makuake = Makuake(url)
    database = makuake.fetch()
    pprint(database)

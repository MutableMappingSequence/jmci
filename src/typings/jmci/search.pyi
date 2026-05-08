# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# pyright: reportMissingTypeStubs = false
from __future__ import annotations

from collections.abc import Callable
from collections.abc import Iterable
from dataclasses import dataclass
from enum import Enum
from typing import Any
from typing import Optional
from typing import SupportsIndex

from jmcomic import JmApiClient
from jmcomic import JmHtmlClient


class SearchType(Enum):
    all: int
    default: int
    work: int
    author: int
    tag: int
    actor: int


class OrderBy(Enum):
    latest: str
    default: str
    view: str
    picture: str
    like: str
    score: str
    comments: str
    month_ranking: str
    week_ranking: str
    day_ranking: str


class FilterTime(Enum):
    all: str
    default: str
    month: str
    week: str
    day: str
    today: str


class Category(Enum):
    all: str
    default: str
    doujin: str
    single: str
    short: str
    others: str
    korea: str
    america: str
    cosplay: str
    c3D: str
    english_site: str


class SubCategory(Enum):
    none: None
    default: None
    chinese: str
    japanese: str
    doujin_CG: str
    doujin_chinese: str
    doujin_japanese: str
    single_chinese: str
    single_japanese: str
    single_youth: str
    short_chinese: str
    short_japanese: str
    others_others: str
    others_3D: str
    others_cosplay: str


class SearchOption:
    def __init__(
        self,
        keyword: str,
        searching_type: SearchType,
        page: int,
        order_by: OrderBy,
        filter_time: FilterTime,
        category: Category,
        sub_category: Optional[SubCategory] = None,
    ) -> None: ...
    
    @classmethod
    def options_from_keyword(cls, keyword: str) -> SearchOption: ...
    def as_keyword_arguments(self) -> dict[str, Any]: ...


@dataclass(slots=True)
class SearchResult:
    id: str
    title: str
    tags: list[str]


class Search:
    def __init__(
        self,
        keyword: str,
        client: Optional[JmApiClient | JmHtmlClient] = None
    ) -> None: ...
    def searching(self, type: SearchType) -> Search: ...
    def pages(self, pages: Iterable[int]) -> Search: ...
    def keyword(self, keyword: str) -> Search: ...
    def order_by(self, order_by: OrderBy) -> Search: ...
    def filter_time(self, filter_time: FilterTime) -> Search: ...
    def category(self, category: Category) -> Search: ...
    def sub_category(self, sub_category: SubCategory) -> Search: ...
    def process(self) -> list[SearchResult]: ...
    def process_select[T](self, converter: Callable[[SearchResult], T]) -> list[T]: ...
    def where(self, filter: Callable[[SearchResult], bool]) -> Search: ...
    def sort(
        self, 
        key: Callable[[SearchResult], Any],
        reversed: bool = False
    ) -> Search: ...
    def reverse(self) -> Search: ...
    def join(
        self,
        iterable: Iterable[SearchResult],
        filter1: Callable[[SearchResult], bool] = lambda _: True,
        filter2: Callable[[SearchResult], bool] = lambda _: True,
    ) -> Search: ...
    def pop_handler(self, index: SupportsIndex = -1) -> Search: ...
    @property
    def handlers(self) -> list[Callable[[list[SearchResult]], list[SearchResult]]]: ...

# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# pyright: reportMissingTypeStubs = false

"""
Search utilities of jmci.

This module provides a fluent search API for JM Comic clients.
It includes enums for search options, helpers for building options, and
interfaces for getting, filtering and processing results.
"""

from __future__ import annotations

from collections.abc import Callable
from collections.abc import Iterable
from dataclasses import dataclass
from enum import Enum
from functools import reduce
from typing import Any
from typing import Optional
from typing import SupportsIndex

from beartype import beartype
from jmcomic import JmApiClient
from jmcomic import JmHtmlClient
from jmcomic import JmMagicConstants
from jmcomic import JmOption

from .logger import log
from .logger import table


__all__ = [
    "SearchType",
    "OrderBy",
    "FilterTime",
    "Category",
    "SubCategory",
    "SearchOption",
    "SearchResult",
    "Search",
]


class SearchType(Enum):
    """An enum class enumerating search types."""

    all = default = 0
    """Default searching (searching all)."""

    work = 1
    """Search for works that match the search keyword."""

    author = 2
    """Search for albums by the specified author."""

    tag = 3
    """Search for albums with the specified tag(s)."""

    actor = 4
    """Search for albums featuring the specified actor(s)."""


class OrderBy(Enum):
    """An enum class enumerating how to order the results."""

    latest = default = JmMagicConstants.ORDER_BY_LATEST
    """Order by publication time. Latest first."""

    view = JmMagicConstants.ORDER_BY_VIEW
    """Order by views. Most viewed first."""

    picture = JmMagicConstants.ORDER_BY_PICTURE
    """Order by picture count. Most pictures first."""

    like = JmMagicConstants.ORDER_BY_LIKE
    """Order by likes."""

    score = JmMagicConstants.ORDER_BY_SCORE
    """Order by scores. Highest first."""

    comments = JmMagicConstants.ORDER_BY_COMMENT
    """Order by comment count. Most comments first."""

    month_ranking = JmMagicConstants.ORDER_MONTH_RANKING
    """Monthly ranking. Highest first."""

    week_ranking = JmMagicConstants.ORDER_WEEK_RANKING
    """Weekly ranking. Highest first."""

    day_ranking = JmMagicConstants.ORDER_DAY_RANKING
    """Daily ranking. Highest first."""


class FilterTime(Enum):
    """An enum class enumerating how to filter results by publication time."""

    all = default = JmMagicConstants.TIME_ALL
    """No filter (all time)."""

    month = JmMagicConstants.TIME_MONTH
    """The latest month."""

    week = JmMagicConstants.TIME_WEEK
    """The latest week."""

    day = today = JmMagicConstants.TIME_TODAY
    """The latest day (today)."""


class Category(Enum):
    """An enum class enumerating categories used when searching."""

    all = default = JmMagicConstants.CATEGORY_ALL
    """Default category (all)."""

    doujin = JmMagicConstants.CATEGORY_DOUJIN
    """Doujin category."""

    single = JmMagicConstants.CATEGORY_SINGLE
    """Single category."""

    short = JmMagicConstants.CATEGORY_SHORT
    """Short category."""

    others = JmMagicConstants.CATEGORY_ANOTHER
    """Others category."""

    korea = JmMagicConstants.CATEGORY_HANMAN
    """Korea category."""

    america = JmMagicConstants.CATEGORY_HANMAN
    """America category."""

    cosplay = JmMagicConstants.CATEGORY_DOUJIN_COSPLAY
    """Cosplay category."""

    c3D = JmMagicConstants.CATEGORY_3D
    """3D category."""

    english_site = JmMagicConstants.CATEGORY_ENGLISH_SITE
    """English site category."""


class SubCategory(Enum):
    """An enum class enumerating sub categories used when searching."""

    none = default = None
    """Default subcategory (none)."""

    chinese = JmMagicConstants.SUB_CHINESE
    """Chinese subcategory."""

    japanese = JmMagicConstants.SUB_JAPANESE
    """Japanese subcategory."""

    doujin_CG = JmMagicConstants.SUB_DOUJIN_CG
    """Doujin CG subcategory."""

    doujin_chinese = JmMagicConstants.SUB_DOUJIN_CHINESE
    """Doujin Chinese subcategory."""

    doujin_japanese = JmMagicConstants.SUB_SHORT_JAPANESE
    """Doujin Japanese subcategory."""

    single_chinese = JmMagicConstants.SUB_SINGLE_CHINESE
    """Single Chinese subcategory."""

    single_japanese = JmMagicConstants.SUB_SINGLE_JAPANESE
    """Single Japanese subcategory."""

    single_youth = JmMagicConstants.SUB_SINGLE_YOUTH
    """Single Youth subcategory."""

    short_chinese = JmMagicConstants.SUB_SHORT_CHINESE
    """Short Chinese subcategory."""

    short_japanese = JmMagicConstants.SUB_SHORT_JAPANESE
    """Short Japanese subcategory."""

    others_others = JmMagicConstants.SUB_ANOTHER_OTHER
    """Others Others subcategory."""

    others_3D = JmMagicConstants.SUB_ANOTHER_3D
    """Others 3D subcategory."""

    others_cosplay = JmMagicConstants.SUB_ANOTHER_COSPLAY
    """Others Cosplay subcategory."""


# fmt: off
# Adding docs for enum members (not necessary)

SearchType.default.__doc__ = "Default. Same as `SearchType.all`"
SearchType.all.__doc__ = "Default searching (searching all)."
SearchType.work.__doc__ = "Search for works that match the search keyword."
SearchType.author.__doc__ = "Search for albums by the specified author."
SearchType.tag.__doc__ = "Search for albums with the specified tag(s)."
SearchType.actor.__doc__ = "Search for albums featuring the specified actor(s)."

OrderBy.default.__doc__ = "Default. Same as `OrderBy.latest`."
OrderBy.latest.__doc__ = "Order by publication time. Latest first."
OrderBy.view.__doc__ = "Order by views. Most viewed first."
OrderBy.picture.__doc__ = "Order by picture count. Most pictures first."
OrderBy.like.__doc__ = "Order by likes."
OrderBy.score.__doc__ = "Order by scores. Highest first."
OrderBy.comments.__doc__ = "Order by comment count. Most comments first."
OrderBy.month_ranking.__doc__ = "Monthly ranking. Highest first."
OrderBy.week_ranking.__doc__ = "Weekly ranking. Highest first."
OrderBy.day_ranking.__doc__ = "Daily ranking. Highest first."

FilterTime.default.__doc__ = "Default. Same as `FilterTime.all`."
FilterTime.all.__doc__ = "No filter (all time)."
FilterTime.month.__doc__ = "The latest month."
FilterTime.week.__doc__ = "The latest week."
FilterTime.day.__doc__ = "The latest day (today)."

Category.default.__doc__ = "Default. Same as `Category.all`."
Category.all.__doc__ = "Default category (all)."
Category.doujin.__doc__ = "Doujin category."
Category.single.__doc__ = "Single category."
Category.short.__doc__ = "Short category."
Category.others.__doc__ = "Others category."
Category.korea.__doc__ = "Korea category."
Category.america.__doc__ = "America category."
Category.cosplay.__doc__ = "Cosplay category."
Category.c3D.__doc__ = "3D category."
Category.english_site.__doc__ = "English site category."

SubCategory.default.__doc__ = "Default. Same as `SubCategory.none`."
SubCategory.none.__doc__ = "Default subcategory (none)."
SubCategory.chinese.__doc__ = "Chinese subcategory."
SubCategory.japanese.__doc__ = "Japanese subcategory."
SubCategory.doujin_CG.__doc__ = "Doujin CG subcategory."
SubCategory.doujin_chinese.__doc__ = "Doujin Chinese subcategory."
SubCategory.doujin_japanese.__doc__ = "Doujin Japanese subcategory."
SubCategory.single_chinese.__doc__ = "Single Chinese subcategory."
SubCategory.single_japanese.__doc__ = "Single Japanese subcategory."
SubCategory.single_youth.__doc__ = "Single Youth subcategory."
SubCategory.short_chinese.__doc__ = "Short Chinese subcategory."
SubCategory.short_japanese.__doc__ = "Short Japanese subcategory."
SubCategory.others_others.__doc__ = "Others Others subcategory."
SubCategory.others_3D.__doc__ = "Others 3D subcategory."
SubCategory.others_cosplay.__doc__ = "Others Cosplay subcategory."

# fmt: on


@beartype
class SearchOption:
    """A class representing search options for JM Comic searches."""

    def __init__(
        self,
        keyword: str,
        searching_type: SearchType,
        page: int,
        order_by: OrderBy,
        filter_time: FilterTime,
        category: Category,
        sub_category: Optional[SubCategory] = None,
    ) -> None:
        """
        Initialize a SearchOption instance.

        Args:
            keyword (str): The search keyword.
            searching_type (SearchingType): The type of search to perform.
            page (int): The page number for pagination.
            order_by (OrderBy): The ordering criteria for results.
            filter_time (FilterTime): The time filter for results.
            category (Category): The main category to search in.
            sub_category (SubCategory, optional): The subcategory to search in, optional.
        """
        self.keyword = keyword
        self.searching_type = searching_type
        self.page = page
        self.order_by = order_by
        self.filter_time = filter_time
        self.category = category
        self.sub_category = sub_category

    @classmethod
    def options_from_keyword(cls, keyword: str) -> SearchOption:
        """
        Create a SearchOption with a custom search keyword and default search type.

        Args:
            keyword (str): The search keyword.

        Returns:
            SearchOption: A SearchOption instance with default settings.
        """
        return SearchOption(
            keyword,
            SearchType.default,
            1,
            OrderBy.default,
            FilterTime.default,
            Category.all,
            None,
        )

    def as_keyword_arguments(self) -> dict[str, Any]:
        """
        Return keyword arguments for jmcomic.JmcomicClient.search.

        Returns:
            dict[str, Any]: A dict with search parameters.
        """
        return {
            "search_query": self.keyword,
            "main_tag": self.searching_type.value,
            "page": self.page,
            "order_by": self.order_by.value,
            "time": self.filter_time.value,
            "category": self.category.value,
            "sub_category": (
                self.sub_category.value if self.sub_category is not None else None
            ),
        }


@beartype
@dataclass(slots=True)
class SearchResult:
    """A dataclass representing a search result item."""

    id: str
    title: str
    tags: list[str]


@beartype
class Search:
    """A fluent API class for performing searches on JM Comic."""

    def __init__(
        self, keyword: str, client: Optional[JmApiClient | JmHtmlClient] = None
    ) -> None:
        """
        Initialize a search process.

        Args:
            keyword (str): The initial search keyword.
            client (JmHtmlClient | JmApiClient, optional):
                The JM Comic client to use for searching.
                Default to None to create a new client automatically.
        """
        self.__client = (
            client
            if client is not None
            else JmOption.default().new_jm_client()  # type: ignore
        )
        self.__handlers: list[Callable[[list[SearchResult]], list[SearchResult]]] = []

        # Search options defines here.
        self.__option_keyword: str = keyword
        self.__option_pages: Iterable[int] = [1]
        self.__option_searching: SearchType = SearchType.default
        self.__option_order_by: OrderBy = OrderBy.default
        self.__option_filter_time: FilterTime = FilterTime.default
        self.__option_category: Category = Category.default
        self.__option_sub_category: SubCategory = SubCategory.default

    # =============== Search Option Modifying ===============
    def searching(self, type: SearchType) -> Search:
        """
        Set the search type.

        Args:
            type (SearchingType): The SearchingType to use.

        Returns:
            Search: Self for method chaining.
        """
        self.__option_searching = type
        return self

    def pages(self, pages: Iterable[int]) -> Search:
        """
        Set the pages to search.

        Args:
            pages (Iterable[int]): An iterable of page numbers.

        Returns:
            Search: Self for method chaining.
        """
        self.__option_pages = pages
        return self

    def keyword(self, keyword: str) -> Search:
        """
        Set the search keyword.

        Args:
            keyword (str): The search keyword.

        Returns:
            Search: Self for method chaining.
        """
        self.__option_keyword = keyword
        return self

    def order_by(self, order_by: OrderBy) -> Search:
        """
        Set the ordering criteria.

        Args:
            order_by (OrderBy): The OrderBy enum value.

        Returns:
            Search: Self for method chaining.
        """
        self.__option_order_by = order_by
        return self

    def filter_time(self, filter_time: FilterTime) -> Search:
        """
        Set the time filter.

        Args:
            filter_time (FilterTime): The FilterTime enum value.

        Returns:
            Search: Self for method chaining.
        """
        self.__option_filter_time = filter_time
        return self

    def category(self, category: Category) -> Search:
        """
        Set the category.

        Args:
            category (Category): The Category enum value.

        Returns:
            Search: Self for method chaining.
        """
        self.__option_category = category
        return self

    def sub_category(self, sub_category: SubCategory) -> Search:
        """
        Set the subcategory.

        Args:
            sub_category (SubCategory): The SubCategory enum value.

        Returns:
            Search: Self for method chaining.
        """
        self.__option_sub_category = sub_category
        return self

    # =============== Processing ===============
    def process(self) -> list[SearchResult]:
        """
        Execute the search and return the results.

        Returns:
            list[SearchResult]: A list of SearchResult instances.
        """
        log(
            "INFO",
            "Search.process",
            "Process start. Here is the search options specified.",
            table(
                ["Option", "Value"],
                ["Keyword", self.__option_keyword],
                ["Searching", self.__option_searching.name],
                ["Order By", self.__option_searching.name],
                ["Filter Time", self.__option_filter_time.name],
                ["Category", self.__option_category.name],
                ["Sub Category", self.__option_sub_category.name],
                border_style="blue",
            ),
        )
        pages: list[SearchResult] = []
        for pageid in self.__option_pages:
            log("INFO", "Search.process", f"Now searching page {pageid}.")
            option = SearchOption(
                self.__option_keyword,
                self.__option_searching,
                pageid,
                self.__option_order_by,
                self.__option_filter_time,
                self.__option_category,
                self.__option_sub_category,
            )
            page = self.__client.search(**option.as_keyword_arguments())
            pages.extend(SearchResult(*res) for res in page.iter_id_title_tag())
        log("INFO", "Search.process", "Results returned. Now applying handlers.")
        result = reduce(lambda value, func: func(value), self.__handlers, pages)
        log(
            "INFO",
            "Search.process",
            "Handlers applying finished. Result returning now.",
        )
        return result

    def process_select[T](self, converter: Callable[[SearchResult], T]) -> list[T]:
        """
        Execute the search and apply a converter to each result.

        Args:
            converter (Callable[[SearchResult], T]): A callable to convert SearchResult to another type.

        Returns:
            list[T]: A list of converted results.
        """  # noqa: E501
        ret = [converter(r) for r in self.process()]
        log("INFO", "Search.process_select", "Selectors applied. Result returning now.")
        return ret

    # =============== Search Result Handling ===============
    def where(self, filter: Callable[[SearchResult], bool]) -> Search:
        """
        Add a filter to the search results.

        Args:
            filter (Callable[[SearchResult], bool]): A callable that returns True for results to keep.

        Returns:
            Search: Self for method chaining.
        """  # noqa: E501
        self.__handlers.append(lambda rs: [r for r in rs if filter(r)])
        return self

    def sort(
        self, key: Callable[[SearchResult], Any], reversed: bool = False
    ) -> Search:
        """
        Sort the search results.

        Args:
            key (Callable[[SearchResult], Any]): A callable to extract sort key from SearchResult.
            reversed (bool, optional): Whether to sort in reverse order. Defaults to False.

        Returns:
            Search: Self for method chaining.
        """  # noqa: E501
        self.__handlers.append(lambda rs: sorted(rs, key=key, reverse=reversed))
        return self

    def reverse(self) -> Search:
        """
        Reverse the order of search results.

        Returns:
            Search: Self for method chaining.
        """
        self.__handlers.append(lambda rs: rs[::-1])
        return self

    def join(
        self,
        iterable: Iterable[SearchResult],
        filter1: Callable[[SearchResult], bool] = lambda _: True,
        filter2: Callable[[SearchResult], bool] = lambda _: True,
    ) -> Search:
        """
        Join another iterable of SearchResult to the current results.

        Args:
            iterable (Iterable[SearchResult]): The iterable to join.
            filter1 (Callable[[SearchResult], bool], optional): Filter for current results. Defaults to lambda _: True.
            filter2 (Callable[[SearchResult], bool], optional): Filter for the joined iterable. Defaults to lambda _: True.

        Returns:
            Search: Self for method chaining.
        """  # noqa: E501
        self.__handlers.append(
            lambda rs: [r for r in rs if filter1(r)]
            + [r for r in iterable if filter2(r)]
        )
        return self

    # =============== Handlers Controlling ===============
    def pop_handler(self, index: SupportsIndex = -1) -> Search:
        """
        Remove a handler from the handler list.

        Args:
            index (SupportsIndex, optional): The index of the handler to remove. Defaults to -1.

        Returns:
            Search: Self for method chaining.
        """  # noqa: E501
        self.__handlers.pop(index)
        return self

    @property
    def handlers(self) -> list[Callable[[list[SearchResult]], list[SearchResult]]]:
        """
        Get the list of result handlers.

        Returns:
            list[Callable[[list[SearchResult]], list[SearchResult]]]: A list of callables that process SearchResult lists.
        """  # noqa: E501
        return self.__handlers


if __name__ == "__main__":
    result = (
        Search("星野")
        .order_by(OrderBy.default)
        .pages(range(1, 4))
        .where(lambda r: r.id.startswith("14"))
        .sort(lambda r: len(r.title))
        .reverse()
        .process_select(lambda r: r.title)
    )
    print(result)

    # Method chain is SO GRACE, isn't it :]   <-- idk what is this either :)

# !/usr/bin/env python3
# -*- coding: utf-8 -*-
def search(
    keyword: str,
    pages: list[int] = [1],
    search_type: str = "all",
    order_by: str = "latest",
    filter_time: str = "all",
    category: str = "all",
    sub_category: str = "none",
) -> None: ...

def download(
    album_ids: list[int],
    directory: str = "jmci_downloads",
    jpg: bool = False,
    pictures: int = 50,
    export_format: list[str] = ["folder"],
    cover: bool = False
) -> None: ...

def main() -> None: ...

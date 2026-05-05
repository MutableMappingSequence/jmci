# !/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CLI support for jmci.
This CLI based on typer for simple search and download demands.
"""

from __future__ import annotations

import os
from typing import Annotated

from rich.align import Align
from rich.console import Console
from rich.panel import Panel
from rich.table import Column
from rich.table import Table
from typer import Argument
from typer import Option
from typer import Typer
from typer import rich_utils

from .download import Download
from .download import ExportFormat
from .logger import format_exception
from .logger import log
from .search import Category
from .search import FilterTime
from .search import OrderBy
from .search import Search
from .search import SearchType
from .search import SubCategory
from .utils import get_enum_member
from .utils import truncate_string


rich_utils.STYLE_USAGE = "bold #6A71FF"
rich_utils.STYLE_USAGE_COMMAND = "bold #9191FF"
rich_utils.STYLE_COMMANDS_TABLE_FIRST_COLUMN = rich_utils.STYLE_OPTION = "bold #6A71FF"
rich_utils.STYLE_SWITCH = "bold #9671FF"
rich_utils.STYLE_COMMANDS_PANEL_BORDER = rich_utils.STYLE_OPTIONS_PANEL_BORDER = "#9898FF"
rich_utils.STYLE_HELPTEXT_FIRST_LINE \
    = rich_utils.STYLE_HELPTEXT \
    = rich_utils.STYLE_OPTION_HELP \
    = "#BDBDFF"
rich_utils.STYLE_METAVAR = rich_utils.STYLE_METAVAR_SEPARATOR = "bold #C34BFF"
rich_utils.STYLE_REQUIRED_LONG = rich_utils.STYLE_REQUIRED_SHORT = "#9E64FF"
rich_utils.STYLE_OPTION_DEFAULT = "#DC8DFF"


console = Console(highlight=False)
app = Typer(help="CLI tool of jmci.", no_args_is_help=True)


@app.command(
    short_help="Search for albums.",
    help="""
Search for albums.
You can specify the search options by using the options.
Use --help to learn about availible values for each option.
""",
    no_args_is_help=True
)
def search(
    keyword: Annotated[
        str,
        Argument(help="The search keyword.")
    ],
    pages: Annotated[
        list[int],
        Option(
            ..., "--pages",
            help="Specify the page numbers for pagination."
        )
    ] = [1],
    search_type: Annotated[
        str,
        Option(
            ..., "--search-type",
            help=(
                "Specify the search type. "
                f"Support types: {', '.join(SearchType._member_names_)}."
            )
        )
    ] = "all",
    order_by: Annotated[
        str,
        Option(
            ..., "--order-by",
            help=(
                "Specify how to order the results. "
                f"Support order methods: {', '.join(OrderBy._member_names_)}."
            )
        )
    ] = "latest",
    filter_time: Annotated[
        str,
        Option(
            ..., "--filter-time",
            help=(
                "Specify how to filter results by publication time. "
                f"Support filters: {', '.join(FilterTime._member_names_)}."
            )
        )
    ] = "all",
    category: Annotated[
        str,
        Option(
            ..., "--category",
            help=(
                "Specify the category used when searching. "
                f"Support categories: {', '.join(Category._member_names_)}."
            )
        )
    ] = "all",
    sub_category: Annotated[
        str,
        Option(
            ..., "--sub-category",
            help=(
                "Specify the sub category used when searching. "
                f"Support sub categories: {', '.join(SubCategory._member_names_)}."
            )
        )
    ] = "none"
) -> None:
    try:
        option_search_type = get_enum_member(SearchType, search_type)
        option_order_by = get_enum_member(OrderBy, order_by)
        option_filter_time = get_enum_member(FilterTime, filter_time)
        option_category = get_enum_member(Category, category)
        option_sub_category = get_enum_member(SubCategory, sub_category)
    except KeyError as e:
        enum_name, name = e.args
        return console.print(
            Panel(
                "[magenta]Option Input Error: [/]"
                f"[red]Invalid value '{name}' for option '{enum_name}'.[/]",
                title="Error",
                title_align="left",
                border_style="red",
            )
        )
    results = (
        Search(keyword)
        .searching(option_search_type)
        .pages(pages)
        .order_by(option_order_by)
        .filter_time(option_filter_time)
        .category(option_category)
        .sub_category(option_sub_category)
        .process()
    )
    result_table = Table(
        Column(Align.center("Album Title")),
        Column(Align.center("Album Id")),
        Column(Align.center("Album Tags")),
        title="Search Result",
        title_style="bold #6A71FF",
        border_style="#6A71FF",
        expand=True
    )
    for res in results:
        result_table.add_row(
            Align.left(truncate_string(res.title, console.width // 2)),
            Align.center(res.id),
            Align.center(', '.join(res.tags) if res.tags else "/"),
            style="#BDBDFF"
        )
    console.print(result_table)


@app.command(
    short_help="Download albums by album ids.",
    help="""
Search for albums.
You can specify the search options by using the options.
""",
    no_args_is_help=True
)
def download(
    album_ids: Annotated[
        list[int],
        Argument(help="The album IDs to download")
    ],
    directory: Annotated[
        str,
        Option(
            ..., "--directory",
            help=(
                "The directory to save the downloaded albums. "
                "Defaults to 'jmci_downloads'"
            )
        )
    ] = "jmci_downloads",
    jpg: Annotated[
        bool,
        Option(
            ..., "--jpg", "-j",
            help="Enable automatic picture-to-JPG converting."
        )
    ] = False,
    pictures: Annotated[
        int,
        Option(
            ..., "--pictures",
            min=1, max=50, clamp=True,
            help=(
                "Specify how many pictures can be download each time. "
                "Minimum to 1 while maximum to 50. "
                "If your input is out of range, "
                "it will be force corrected to the limit value."
            )
        )
    ] = 50,
    export_format: Annotated[
        list[str],
        Option(
            ..., "-e", "--export-format",
            help=(
                "Specify the export format for downloaded albums."
                f"Support formats: {', '.join(ExportFormat._member_names_)}."
            )
        )
    ] = ["folder"],
    cover: Annotated[
        bool,
        Option(
            ..., "-c", "--cover",
            help="Download the album covers."
        )
    ] = False
) -> None:
    try:
        expf = get_enum_member(ExportFormat, export_format.pop())
        for f in export_format:
            expf |= get_enum_member(ExportFormat, f)
    except KeyError as e:
        enum_name, name = e.args
        return console.print(
            Panel(
                "[magenta]Option Input Error: [/]"
                f"[red]Invalid value '{name}' for option '{enum_name}'.[/]",
                title="Error",
                title_align="left",
                border_style="red",
            )
        )
    process = (
        Download(album_ids)
        .directory(directory)
        .pictures(pictures)
        .export_format(expf)
    )
    if jpg:
        process = process.jpg()
    if cover:
        process.process_download_cover()
    else:
        process.process()
    console.print(
        Panel(
            "[#BDBDFF]Successfully download album(s) "
            f"[#9898FF]{', '.join(str(id) for id in album_ids)}[/] "
            f"to [#9898FF]{os.path.abspath(directory)}.[/][/]",
            title="Success",
            title_align="left",
            border_style="#6A71FF",
            expand=True
        )
    )


def main() -> None:
    try:
        app()
    except Exception as e:
        log(
            "ERROR",
            "cli",
            f"Unhandled exception.\n{format_exception(e)}\n"
            "Raise an issue on github with the output and the error message."
        )


if __name__ == "__main__":
    main()

    # I've done this prooooooooooojecttttttttttttttttt!!!!!!!!!!!!!!!!!!!! :)

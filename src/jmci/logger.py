# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# pyright: reportMissingTypeStubs = false

"""
Logging utilites for jmci.

This module is used to internal logging.
You'd better import `enable_logging` to enable/disable logging only.
"""

from __future__ import annotations

import re
from collections.abc import Iterable
from datetime import datetime
from traceback import extract_tb
from typing import Any
from typing import Literal
from typing import Optional

from beartype import beartype
from jmcomic import JmModuleConfig
from jmcomic import default_jm_logging as __default_jm_logging  # type: ignore
from rich.align import Align
from rich.columns import Columns
from rich.console import Console
from rich.console import RenderableType
from rich.table import Column
from rich.table import Table


__all__ = ["enable_logging"]


logging: bool = True
_console = Console(highlight=False)


@beartype
def enable_logging(enable: bool = False) -> None:
    """
    Set whether to enable logging.

    Args:
        enable (bool, optional): Whether to enable logging. Defaults to False.
    """
    global logging
    logging = enable
    JmModuleConfig.FLAG_ENABLE_JM_LOG = enable


def log(
    level: Literal["INFO", "WARNING", "ERROR"],
    master: str,
    msg: str,
    *extra: RenderableType,
) -> None:
    if not logging:
        return
    match level:
        case "INFO":
            color = "[blue]"
        case "WARNING":
            color = "[yellow]"
        case "ERROR":
            color = "[red]"
    _console.print(
        Columns(
            [
                Align.left(
                    f"[bold]{color}[{level}][/] [magenta]<{master}>[/][/] "
                    f"[green]{msg}[/]"
                ),
                Align.right(
                    f"[dim]{datetime.now().strftime('(%d/%m/%Y %H:%M:%S.%f)')}[/]"
                ),
            ],
            expand=True,
        ),
        *extra,
    )


def table(*lines: Iterable[Any], border_style: str) -> Table:
    iterlines = iter(lines)
    table = Table(
        *(Column(i, justify="center") for i in next(iterlines)),
        border_style=border_style,
    )
    for line in iterlines:
        table.add_row(*(Align.center(i) for i in line))
    return table


@beartype
def format_exception(exc: Exception) -> str:
    """
    Format an exception.

    Args:
        exc (Exception): The exception to format.

    Returns:
        str: Formatted exception (rich style).
    """
    return (
        f"[magenta][bold]{exc.__class__.__name__}:[/] {exc!s}[/]\n"
        + "\n".join(
            f"    [red]in {stack.filename} "
            f"(at line {stack.lineno}): "
            f"[dim]{stack.line}[/][/]"
            for stack in extract_tb(exc.__traceback__)
        )
    )


__RE_NEW_OLD_DOMAINS = re.compile(r"\(new\)\[(?P<new>.*)\].*\[(?P<old>.*)\]")
__RE_DOMAIN = re.compile(r"\'(.+)\'")
__RE_PHOTO_PROCESS = re.compile(r"\((?P<id>\d+)\[(?P<finished>\d+)/(?P<total>\d+)\]\)")
__RE_PROCESS = re.compile(r"\[(?P<finished>\d+)/(?P<total>\d+)\]")


# Override the original logger of jmcomic.
def jmcomic_log(
    topic: str, msg: str | Exception, e: Optional[Exception] = None
) -> None:
    if isinstance(msg, Exception):
        return log(
            "ERROR",
            "logger & jmcomic",
            f"Unknown exception from jmcomic.\n{format_exception(msg)}\n"
            "This exception is properly a problem from jmcomic."
            "We recommend you to raise an issue on github."
        )
    if isinstance(e, Exception):
        return log(
            "ERROR",
            "logger & jmcomic",
            f"Unknown exception from jmcomic.\n{format_exception(e)}\n"
            "This exception is properly a problem from jmcomic."
            "We recommend you to raise an issue on github."
        )
    match topic:
        case "api.update_domain.success":
            new_old = __RE_NEW_OLD_DOMAINS.search(msg)   # Get the domain list first.
            if new_old is None:
                return __default_jm_logging(topic, msg, e)  # pyright: ignore[reportArgumentType] # noqa: E501
            new_old = new_old.groupdict()
            news, olds = new_old["new"], new_old["old"]
            # Use __RE_DOMAIN to get all the domains.
            log(
                "INFO",
                "jmcomic.update_domain",
                f"New domain found: {', '.join(f'"{n}"' for n in __RE_DOMAIN.findall(news))}.",   # noqa: E501
            )
            log(
                "WARNING",
                "jmcomic.update_domain",
                "These old domains were replaced by new domains: "
                f"{', '.join(f'"{n}"' for n in __RE_DOMAIN.findall(olds))}.",
            )
        case "api":
            log("INFO", "jmcomic", f"Connected [dark_green]{msg}[/].")
        case "photo.before":
            process = __RE_PHOTO_PROCESS.search(msg)   # Get the domain list first.
            if process is None:
                return __default_jm_logging(topic, msg, e)  # pyright: ignore[reportArgumentType] # noqa: E501
            process = process.groupdict()
            id_, finished, total = process["id"], process["finished"], process["total"]
            log(
                "INFO",
                "jmcomic",
                f"Now downloading character {finished} of album {id_!r} "
                f"(total {total})."
            )
        case "photo.after":
            process = __RE_PHOTO_PROCESS.search(msg)   # Get the domain list first.
            if process is None:
                return __default_jm_logging(topic, msg, e)  # pyright: ignore[reportArgumentType] # noqa: E501
            process = process.groupdict()
            id_, finished, total = process["id"], process["finished"], process["total"]
            log(
                "INFO",
                "jmcomic",
                f"Finished downloading character {finished} of album {id_!r} "
                f"(total {total})."
            )
        case "image.before":
            process = __RE_PROCESS.search(msg)   # Get the domain list first.
            if process is None:
                return __default_jm_logging(topic, msg, e)  # pyright: ignore[reportArgumentType] # noqa: E501
            process = process.groupdict()
            finished, total = process["finished"], process["total"]
            log("INFO", "jmcomic", f"Downloading picture {finished} / {total}.")
        case "image.after":
            process = __RE_PROCESS.search(msg)   # Get the domain list first.
            if process is None:
                return __default_jm_logging(topic, msg, e)  # pyright: ignore[reportArgumentType] # noqa: E501
            process = process.groupdict()
            finished, total = process["finished"], process["total"]
            log("INFO", "jmcomic", f"Finished downloading picture {finished}.")
        case "album.before":
            process = __RE_PROCESS.search(msg)   # Get the domain list first.
            if process is None:
                return __default_jm_logging(topic, msg, e)  # pyright: ignore[reportArgumentType] # noqa: E501
            id_ = process.groupdict()["id"]
            log("INFO", "jmcomic", f"Successfully got album {id_!r}.")
        case "album.after":
            process = __RE_PROCESS.search(msg)   # Get the domain list first.
            if process is None:
                return __default_jm_logging(topic, msg, e)  # pyright: ignore[reportArgumentType] # noqa: E501
            id_ = process.groupdict()["id"]
            log("INFO", "jmcomic", f"Successfullty downloaded album {id_}.")
        case "req.error":
            log("ERROR", "jmcomic", "Failed to perform.")
        case "req.retry":
            log("INFO", "jmcomic", "Now retrying.")
        case _:
            log(
                "WARNING",
                "logger",
                f"Log topic unhandled {topic!r}. Using default jmcomic logger now. "
                "If you see this message, "
                "you can copy the log and raise an issue on github."
            )
            print(topic, msg, e)  # pyright: ignore[reportArgumentType]


JmModuleConfig.EXECUTOR_LOG = jmcomic_log  # pyright: ignore[reportAttributeAccessIssue]


# Y were U here. Anyway, STAR my project pls :)

# !/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

from collections.abc import Iterable
from typing import Any
from typing import Literal
from typing import Optional

from rich.console import RenderableType
from rich.table import Table


logging: bool = True


def enable_logging(enable: bool = False) -> None: ...

def log(
    level: Literal["INFO", "WARNING", "ERROR"],
    master: str,
    msg: str,
    *extra: RenderableType,
) -> None: ...

def table(*lines: Iterable[Any], border_style: str) -> Table: ...

def format_exception(exc: Exception) -> str: ...

def jmcomic_log(
    topic: str,
    msg: str | Exception,
    e: Optional[Exception] = None
) -> None: ...
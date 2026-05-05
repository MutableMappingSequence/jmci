# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# pyright: reportMissingTypeStubs = false

"""
General utilities of jmci.

This module provides convenient ways to make PDF and ZIP files,
better enum member getting, and string truncating.
"""

from __future__ import annotations

import os
import shutil
from enum import Enum
from pathlib import Path
from typing import cast

from beartype import beartype
from img2pdf import convert  # pyright: ignore[reportUnknownVariableType]
from img2pdf import logging as __img2pdf_logging

from .logger import log


__all__ = [
    "make_zip",
    "make_pdf",
    "get_enum_member",
    "truncate_string"
]


__img2pdf_logging.disable(99999)
del __img2pdf_logging


@beartype
def make_zip(root_dir: os.PathLike[str] | str, to_path: os.PathLike[str] | str) -> None:
    """
    Make a zip file.

    Args:
        root_dir (PathLike[str] | str): The directory to pack.
        to_path (PathLike[str] | str): The path to save the zip file (without extension).
            If the path is not exist, it will be created automatically.
    """
    log(
        "INFO",
        "make_zip",
        f"Making a zip archive for [dark_green]{os.path.abspath(root_dir)}[/]."
    )
    os.makedirs(os.path.dirname(to_path), exist_ok=True)   # Create necessary directories.
    path = shutil.make_archive(os.path.abspath(to_path), "zip", root_dir)
    log(
        "INFO",
        "make_zip",
        f"Successfully zip [dark_green]{os.path.abspath(root_dir)}[/] "
        f"to [dark_green]{os.path.abspath(path)}[/].",
    )


@beartype
def make_pdf(
    picture_paths: list[os.PathLike[str] | str],
    to_path: os.PathLike[str] | str
) -> None:
    """
    Make a PDF.

    Args:
        picture_paths (list[PathLike[str]  |  str]): The paths to the pictures to include in the PDF.
        to_path (PathLike[str] | str): The path to save the PDF file (with extension).
            If the path is not exist, it will be created automatically.
    """  # noqa: E501
    length = len(set(picture_paths))
    log("INFO", "make_pdf", f"Combining {length} pictures into PDF.")
    path = Path(to_path)
    path.parent.mkdir(parents=True, exist_ok=True)   # Create necessary directories.
    with open(path, "wb") as f:
        # Why function `convert` accepts list but not generator? Strange isn't it :<
        # NOTE: DO NOT REMOVE THESE SQUARE BRACKETS. THEY ARE NECESSARY.
        f.write(cast(bytes, convert([os.path.abspath(p) for p in picture_paths])))
        # ..........................^.........................................^...
    log(
        "INFO",
        "make_pdf",
        f"Successfully combine {length} pictures into PDF "
        f"and export to [dark_green]{path.absolute()}[/].",
    )


@beartype
def get_enum_member[T: Enum](enum: type[T], name: str) -> T:
    """
    Get an enum member with detaild exception raised while member name not found.

    Args:
        enum (type[Enum]): The enum class the member getting from.
        name (str): The name of the member.

    Raises:
        KeyError: `KeyError(enum.__name__, name) from e` is raised when member name not found.

    Returns:
        _EnumMember_: The enum member got.
    """   # noqa: E501
    try:
        return enum[name]
    except KeyError as e:
        raise KeyError(enum.__name__, name) from e


@beartype
def truncate_string(string: str, length: int) -> str:
    """
    Truncate a string into specified length. The width must be at least 6.

    Args:
        string (str): The string to truncate.
        length (int): The maximum length of the truncated string. Minimum to 6.

    Returns:
        str: The truncated string.

    Example:
        >>> truncate_string("start xxxxxxxxxx end", 999)
        start xxxxxxxxxx end

        >>> truncate_string("start xxxxxxxxxx end", 10)
        st......nd

        >>> truncate_string("start xxxxxxxxxx end", 0)
        AssertionError: The width must be at least 6.
    """
    assert 6 <= length, "The width must be at least 6."
    if len(string) <= length:
        return string
    chars_to_keep = length - 6

    head_len = (chars_to_keep + 1) // 2
    tail_len = chars_to_keep // 2
    return string[:head_len] + "......" + string[-tail_len:]


# Ciallo ~ (<·w<)''+   :)

# !/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import os
from enum import Enum


def make_zip(
    root_dir: os.PathLike[str] | str,
    to_path: os.PathLike[str] | str
) -> None: ...

def make_pdf(
    picture_paths: list[os.PathLike[str] | str],
    to_path: os.PathLike[str] | str
) -> None: ...

def get_enum_member[T: Enum](enum: type[T], name: str) -> T: ...

def truncate_string(string: str, length: int) -> str: ...

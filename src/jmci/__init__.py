# !/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
A high-level encapsulation of `jmcomic`,
providing a fluent download API for JM Comic clients search and download process.
A CLI called "jmci" is also provided for simple process.
"""

from .download import *                                # noqa: F401
from .logger import enable_logging as enable_logging   # noqa: F401
from .search import *                                  # noqa: F401


__version__ = "0.1.0"

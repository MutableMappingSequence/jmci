# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# pyright: reportMissingTypeStubs = false

"""
Download utilities of jmci.

This module provides a fluent download API for JM Comic clients.
It includes an interface for downloading albums
with different export function in different formats integrated.
"""

from __future__ import annotations

import os
import shutil
from collections.abc import Iterable
from enum import Flag
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Optional
from typing import SupportsIndex
from typing import cast

from beartype import beartype
from jmcomic import JmAlbumDetail
from jmcomic import JmApiClient
from jmcomic import JmDownloader
from jmcomic import JmHtmlClient
from jmcomic import JmModuleConfig
from jmcomic import JmOption
from jmcomic import download_album  # pyright: ignore[reportUnknownVariableType]

from .logger import log
from .logger import table
from .utils import make_pdf
from .utils import make_zip


__all__ = ["ExportFormat", "Download"]


FILE_NAME_MAX_LENGTH: int = 255
"""The maximum length of file name. Default 255.

File names that exceed this length will cause `OSError [Errno 36]`.

To avoid `OSError [Errno 36]`,
the author of `jmcomic` truncates the file name to 100 characters to avoid this problem.
However, the truncated file name may change the file path
and cause problems when exporting to PDF or ZIP.
In order to avoid this problem, we check the length of the file name
and truncate it to 100 characters if it exceeds the maximum length
so as to match jmcomic's behavior.
"""


class ExportFormat(Flag):
    """An enum class enumerating export format flags supported."""

    folder = 1
    """Export as folders.
    All pictures of an album will be exported to a folder directly."""

    pdf = 2
    """Export as PDFs.
    Pictures of an album will be combined into a PDF file."""

    zip = 4
    """Export as ZIPs.
    Pictures of an album will be compressed into a ZIP file."""


# fmt: off
# Adding docs for enum members (not necessary)

ExportFormat.folder.__doc__ = """Export as folders. \
All pictures of an album will be exported to a folder directly."""
ExportFormat.pdf.__doc__ = """Export as PDFs. \
Pictures of an album will be combined into a PDF file."""
ExportFormat.zip.__doc__ = """Export as ZIPs. \
Pictures of an album will be compressed into a ZIP file."""

# fmt: on


@beartype
class Download:
    """A fluent API class for performing downloads on JM Comic."""

    def __init__(self, album_ids: list[int]) -> None:
        """
        Initialize a download process.

        Args:
            album_ids (list[int]): A list of album IDs to download.
        """
        self.__album_ids = album_ids
        self.__export_form = ExportFormat.folder
        self.__directory = Path(__file__).parent / "jmci_downloads"
        self.__jpg: bool = False
        self.__pictures: int = 50

    # =============== Download Albums ===============
    def downloading(self, album_ids: list[int]) -> Download:
        """
        Reassign the album IDs to download.

        Args:
            album_ids (list[int]): The new list of album IDs to download.

        Returns:
            Download: Self for method chaining.
        """
        self.__album_ids = album_ids
        return self

    def remove(self, id: int) -> Download:
        """
        Remove an album ID from the download list.

        Raises ValueError if the value is not present.

        Args:
            id (int): The album ID to remove.

        Returns:
            Download: Self for method chaining.
        """
        self.__album_ids.remove(id)
        return self

    def pop(self, index: SupportsIndex = -1) -> Download:
        """
        Remove and return an album ID at the specified index from the download list.

        Raises IndexError if list is empty or index is out of range.

        Args:
            index (SupportsIndex, optional): The index of the album ID to remove. Defaults to -1.

        Returns:
            Download: Self for method chaining.
        """  # noqa: E501
        self.__album_ids.pop(index)
        return self

    def add(self, id: int) -> Download:
        """
        Add (append) an album ID to the end of download list.

        Args:
            id (int): The album ID to add.

        Returns:
            Download: Self for method chaining.
        """
        self.__album_ids.append(id)
        return self

    def insert(self, index: SupportsIndex, id: int) -> Download:
        """
        Insert an album id to the download list before index.

        Args:
            index (SupportsIndex): The index before which the album ID will be inserted.
            id (int): The album ID to insert.

        Returns:
            Download: Self for method chaining.
        """
        self.__album_ids.insert(index, id)
        return self

    def extend(self, ids: Iterable[int]) -> Download:
        """
        Extend download list by appending album ids from the iterable.

        Args:
            ids (Iterable[int]): The list of album IDs to add.

        Returns:
            Download: Self for method chaining.
        """
        self.__album_ids.extend(ids)
        return self

    # =============== Export Options ===============
    def export_format(self, format: ExportFormat) -> Download:
        """
        Set the export format for downloaded albums.

        Args:
            format (ExportFormat): The export format to set.

        Returns:
            Download: Self for method chaining.
        """
        self.__export_form = format
        return self

    def add_export_format(self, format: ExportFormat) -> Download:
        """
        Add an export format.

        Args:
            format (ExportFormat): The export format to add.

        Returns:
            Download: Self for method chaining.
        """
        self.__export_form |= format
        return self

    def remove_export_format(self, format: ExportFormat) -> Download:
        """
        Remove an export format.

        Args:
            format (ExportFormat): The export format to remove.

        Returns:
            Download: Self for method chaining.
        """
        self.__export_form &= ~format
        return self

    def directory(self, directory: os.PathLike[str] | str) -> Download:
        """
        Set the directory to save the downloaded albums.

        Args:
            directory (PathLike[str] | str): The directory to save downloaded albums.

        Returns:
            Download: Self for method chaining.
        """
        self.__directory = directory
        return self

    def jpg(self, convert_to_jpg: bool = True) -> Download:
        """
        Set whether convert the pictures into JPG automatically.

        Args:
            convert_to_jpg (bool, optional): Whether convert the pictures into JPG automatically. Defaults to True.

        Returns:
            Download: Self for method chaining.
        """  # noqa: E501
        self.__jpg = convert_to_jpg
        return self

    def pictures(self, pictures: int) -> Download:
        """
        Set how many pictures can be download each time. Maximum to 50.

        Args:
            pictures (int): How many pictures can be download each time. Maximum to 50.

        Returns:
            Download: Self for method chaining.
        """
        assert (
            1 <= pictures <= 50
        ), f"Invalid value for pictures: {pictures} is not in the range 1 <= x <= 50"
        self.__pictures = pictures
        return self

    # =============== Processing ===============
    def process(self) -> None:
        """
        Start the download process with the specified options.
        If the specified directory does not exist, it will be created automatically.
        """
        log(
            "INFO",
            "Download.process",
            "Process start. Here is the search options specified.",
            table(
                ["Option", "Value"],
                ["Export Form", self.__export_form.name],
                ["Export Directory", os.path.abspath(self.__directory)],
                ["Convert to JPG", str(self.__jpg)],
                ["Pictures downloading each time", str(self.__pictures)],
                ["Albums Downloading", str(self.__album_ids)[1:-1]],
                border_style="blue",
            ),
        )
        os.makedirs(self.__directory, exist_ok=True)  # Create necessary directories.
        with TemporaryDirectory() as tempdir:
            log(
                "INFO",
                "Download.process.TemporaryDirectory",
                f"Create a temporary directory [dark_green]{tempdir}[/].",
            )
            option = JmOption.default().copy_option()
            option.download.threading.image = self.__pictures  # type: ignore
            option.download.image.suffix = ".jpg" if self.__jpg else None  # type: ignore
            option.dir_rule.base_dir = tempdir
            log("INFO", "Download.process", "Now downloading albums.")

            for detail, _ in cast(
                set[tuple[JmAlbumDetail, JmDownloader]],
                download_album(self.__album_ids, option),
            ):
                log("INFO", "Download.process", f"Handling album {detail.id} now.")
                if len(detail) >= FILE_NAME_MAX_LENGTH:
                    # Truncates the file name so as to match jmcomic's behavior.
                    detail.name = detail.name[
                        : JmModuleConfig.VAR_FILE_NAME_LENGTH_LIMIT
                    ]
                if self.__export_form & ExportFormat.folder:
                    # XXX: Is there any implementation can avoid copying tree?
                    log(
                        "INFO",
                        "Download.process",
                        "Copying downloaded picutres to "
                        f"{os.path.abspath(self.__directory)}",
                    )
                    shutil.copytree(
                        os.path.join(tempdir, detail.name),
                        os.path.join(self.__directory, detail.id),
                        dirs_exist_ok=True,
                    )
                if self.__export_form & ExportFormat.pdf:
                    make_pdf(
                        [  # <== NOTE: DO NOT USE "(" HERE!!!
                            os.path.join(root, file)
                            for root, _, files in os.walk(
                                os.path.join(tempdir, detail.name)
                            )
                            for file in files
                        ],  # <== NOTE: DO NOT USE ")" HERE!!!
                        os.path.join(self.__directory, detail.id + ".pdf"),
                    )
                if self.__export_form & ExportFormat.zip:
                    make_zip(
                        os.path.join(tempdir, detail.name),
                        os.path.join(self.__directory, detail.id),
                    )
            log(
                "INFO",
                "Download.process.TemporaryDirectory",
                f"Temporary directory [dark_green]{tempdir}[/] removed.",
            )
        log("INFO", "Download.process", "Process finished.")

    def process_download_cover(
        self, client: Optional[JmApiClient | JmHtmlClient] = None
    ) -> None:
        """
        Download the covers of the specified albums.

        Args:
            client (JmApiClient | JmHtmlClient):
                The JM Comic client to use for downloading.
                Default to None to create a new client automatically.
        """
        client = JmOption.default().new_jm_client() if client is None else client  # type: ignore # noqa: E501
        for id in self.__album_ids:
            log(
                "INFO",
                "Download.process_download_cover",
                f"Downloading the cover of {id}.",
            )
            client.download_album_cover(  # pyright: ignore[reportUnknownMemberType]
                id, os.path.join(self.__directory, f"{id}.jpg")
            )


if __name__ == "__main__":
    client = JmOption.default().new_jm_client()  # type: ignore
    (
        Download([1424747])
        .export_format(ExportFormat.folder)
        .add_export_format(ExportFormat.pdf)
        .directory(r"D:/")
        .process()
    )

    # Method chain is SO GRACE, isn't it (lol)
    # It's 4/5/2026 2:38 now and I feel very happy :)

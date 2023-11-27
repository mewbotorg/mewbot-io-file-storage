#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2021 - 2023 Mewbot Developers <mewbot@quicksilver.london>
#
# SPDX-License-Identifier: BSD-2-Clause

"""
'file_storage' IO plugin, allowing events to write to the local file system.

The IOConfig object is bound to a local path, and all operations will be
constrained to that path.
Events are able to create directories, write to files (with options for
appending, overwriting, and truncating), and deleting files.

IOConfigs:
  - FileStorage

Events:
  - CreateDirectoryOutputEvent
  - WriteToFileOutputEvent
  - DeleteFileOutputEvent
"""

from __future__ import annotations

from typing import Literal, Sequence

import logging
import pathlib

import aiofiles
from mewbot.api.v1 import Input, IOConfig, Output, OutputEvent

from mewbot.io.file_storage.portable_locking import AsyncFileLock

from .events import (
    CreateDirectoryOutputEvent,
    DeleteFileOutputEvent,
    FSOutputEvent,
    WriteToFileOutputEvent,
)


class FileStorage(IOConfig):
    """
    'file_storage' IO plugin, allowing events to write to the local file system.

    The IOConfig object is bound to a local path, and all operations will be
    constrained to that path.
    Events are able to create directories, write to files (with options for
    appending, overwriting, and truncating), and deleting files.
    """

    _path: str
    _output: FileStorageOutput

    def __init__(self, *, path: str = "") -> None:
        """
        Sets up a new file storage controller.

        The output is then immediately initialised, as it requires no lifecycle management.
        The properties on this object are mapped directly to the generated output.
        """

        if not hasattr(self, "_path"):
            self._path = path
            raise ValueError("FileStorage initialised without path")

        self._output = FileStorageOutput(self._path)

    @property
    def path(self) -> str:
        """The base path to output to. All files will be in this path."""

        return self._output.path

    @path.setter
    def path(self, path: str) -> None:
        """The base path to output to. All files will be in this path."""
        self._path = path

        if hasattr(self, "_output"):
            self._output.path = path

    @property
    def path_exists(self) -> bool:
        """
        Whether the target base path currently exists.

        This code will not create the base path.
        Events will not be processed.
        """

        return self._output.path_exists

    def get_inputs(self) -> Sequence[Input]:
        """File Storage provides no inputs."""

        return []

    def get_outputs(self) -> Sequence[FileStorageOutput]:
        """File Storage output: ability to write data to the local filesystem."""

        return [self._output]


class FileStorageOutput(Output):
    """
    'file_storage' Output class, allowing events to write to the local file system.

    The IOConfig object is bound to a local path, and all operations will be
    constrained to that path.
    Events are able to create directories, write to files (with options for
    appending, overwriting, and truncating), and deleting files.
    """

    _logger: logging.Logger
    _path: pathlib.Path  # Base directory

    def __init__(self, base_path: str) -> None:
        super().__init__()

        self._logger = logging.getLogger(__name__ + "FileSystemOutput")
        self._path = pathlib.Path(base_path)

    @property
    def path(self) -> str:
        """The base path to output to. All files will be in this path."""

        return str(self._path)

    @path.setter
    def path(self, path: str) -> None:
        """The base path to output to. All files will be in this path."""

        self._path = pathlib.Path(path)

    @property
    def path_exists(self) -> bool:
        """
        Whether the target base path currently exists.

        This code will not create the base path.
        Events will not be processed.
        """

        return bool(self._path.exists()) and self._path.is_dir()

    @staticmethod
    def consumes_outputs() -> set[type[OutputEvent]]:
        """
        Defines the set of output events that this Output class can consume.

        CreateDirectoryOutputEvent will create new directories in the base path.
        WriteToFileOutputEvent and DeleteFileOutputEvent allow for manipulating
        files inside the base path.
        """
        return {
            CreateDirectoryOutputEvent,
            WriteToFileOutputEvent,
            DeleteFileOutputEvent,
        }

    async def output(self, event: OutputEvent) -> bool:
        """
        Performs the write-to-disk operation requested via an event.
        """

        if not isinstance(event, FSOutputEvent):
            self._logger.warning("Received unexpected event type %s", type(event))
            return False

        if not self.path_exists:
            self._logger.warning("Cannot output - base path '%s' does not exist", self._path)
            return False

        path = self._path.joinpath(event.path).resolve().absolute()

        if not path.is_relative_to(self._path.resolve().absolute()):
            self._logger.error(
                "Refusing to write to %s, as it would result in a file outside of %s",
                path,
                self._path,
            )
            return False

        path = pathlib.Path(path)

        if isinstance(event, CreateDirectoryOutputEvent):
            future = self._process_directory_create_event(path)
        elif isinstance(event, WriteToFileOutputEvent):
            future = self._process_file_write_event(path, event)
        elif isinstance(event, DeleteFileOutputEvent):
            future = self._process_delete_file_event(path)
        else:
            self._logger.warning("Received unexpected event type %s", type(event))
            return False

        return await future

    async def _process_directory_create_event(self, path: pathlib.Path) -> bool:
        """
        Create the given directory (and any parent directories).
        """

        try:
            path.mkdir(parents=True, exist_ok=True)
        except PermissionError:
            self._logger.warning("Unable to create directory %s - PermissionError", path)
            return False
        # Can happen when you try to e.g. overwrite a folder
        except FileExistsError:
            return False

        return True

    async def _process_file_write_event(
        self, path: pathlib.Path, event: WriteToFileOutputEvent
    ) -> bool:
        """
        Create the given directory (and any parent directories).
        """

        mode: Literal["w", "x", "a"]

        if event.append:
            mode = "a"
        elif event.may_overwrite:
            mode = "w"
        else:
            mode = "x"

        contents = event.file_contents

        try:
            path.parent.mkdir(parents=True, exist_ok=True)

            if isinstance(contents, str):
                await self._do_file_write_str(path, mode, contents)
            else:
                await self._do_file_write_bytes(path, mode + "b", contents)  # type: ignore

            return True
        except FileExistsError:
            self._logger.warning("Unable to write file %s - FileExistsError", path)
            return False
        except PermissionError:
            self._logger.warning("Unable to write file %s - PermissionError", path)
            return False

    @staticmethod
    async def _do_file_write_str(
        path: pathlib.Path, mode: Literal["w", "x", "a"], contents: str
    ) -> None:
        async with aiofiles.open(path, mode=mode) as outfile:
            async with AsyncFileLock(outfile):
                await outfile.write(contents)

    @staticmethod
    async def _do_file_write_bytes(
        path: pathlib.Path, mode: Literal["wb", "xb", "ab"], contents: bytes
    ) -> None:
        async with aiofiles.open(path, mode=mode) as outfile:
            async with AsyncFileLock(outfile):
                await outfile.write(contents)

    async def _process_delete_file_event(self, path: pathlib.Path) -> bool:
        try:
            path.unlink()
        except FileNotFoundError:
            self._logger.warning("Unable to delete %s - FileNotFoundError", path)
            return False
        except PermissionError:
            self._logger.warning("Unable to delete %s - PermissionError", path)
            return False
        except IsADirectoryError:
            self._logger.warning("Unable to delete %s - IsADirectoryError", path)
            return False

        return True


__all__ = [
    "FileStorage",
    "CreateDirectoryOutputEvent",
    "WriteToFileOutputEvent",
    "DeleteFileOutputEvent",
]

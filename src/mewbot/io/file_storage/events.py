# SPDX-FileCopyrightText: 2023 Mewbot Developers <mewbot@quicksilver.london>
#
# SPDX-License-Identifier: BSD-2-Clause

"""
Events which your IOConfig can produce/consume.
"""
from __future__ import annotations

from typing import Union

import dataclasses
import os

from mewbot.api.v1 import OutputEvent


@dataclasses.dataclass
class FSOutputEvent(OutputEvent):
    """
    Base class for generic input events generated by the file system.
    """

    path: Union[str, os.PathLike[str]]


@dataclasses.dataclass
class CreateDirectoryOutputEvent(FSOutputEvent):
    """Creates a directory at the given path (and any parent directories)."""


@dataclasses.dataclass
class WriteToFileOutputEvent(FSOutputEvent):
    """
    Writes the given contents to the specified file.

    Options can enable or disable appending, file creation, and overwriting.
    """

    file_contents: bytes | str
    append: bool = False
    may_overwrite: bool = True


@dataclasses.dataclass
class DeleteFileOutputEvent(FSOutputEvent):
    """
    Delete a file with the given name.
    """

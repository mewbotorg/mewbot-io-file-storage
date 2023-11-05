#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2021 - 2023 Mewbot Developers <mewbot@quicksilver.london>
#
# SPDX-License-Identifier: BSD-2-Clause


"""
Tests for 'file_storage' IO module, used for writing to the file system.

This is the base test class with configuration fixtures.
"""

# pylint: disable=too-few-public-methods

import logging
import tempfile

from mewbot.io.file_storage import FileStorage, FileStorageOutput


class FileStorageTestFixture:
    """
    Tests for 'file_storage' IO module, used for writing to the file system.

    This class tests the behaviours of the CreateDirectoryOutputEvent.
    """

    ERROR_MESSAGE_OUTSIDE_BASE_PATH = (
        "Refusing to write to %s, as it would result in a file outside of %s"
    )

    temp_dir: tempfile.TemporaryDirectory[str]
    path: str
    io_config: FileStorage
    output: FileStorageOutput
    logger: logging.Logger

    @staticmethod
    def prepare_io_config(tmp_dir: str) -> tuple[FileStorage, FileStorageOutput]:
        """
        Prepare an output IOConfig for testing.

        :param tmp_dir: The temporary directory we're operating in
        :return:
        """
        io_config = FileStorage(path=tmp_dir)
        output = io_config.get_outputs()[0]
        return io_config, output

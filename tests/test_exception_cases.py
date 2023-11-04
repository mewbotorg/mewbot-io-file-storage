#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2023 Mewbot Developers <mewbot@quicksilver.london>
#
# SPDX-License-Identifier: BSD-2-Clause

"""
Tests for 'file_storage' IO module, used for writing to the file system.

This class tests the behaviours of the output when permission error occur.
"""

import logging
import os
import tempfile
import sys

import pytest

from mewbot.io.file_storage import (
    CreateDirectoryOutputEvent,
    DeleteFileOutputEvent,
    WriteToFileOutputEvent,
)
from tests.base import FileStorageTestFixture


class TestCreateDirectoryOutputEventHandling(FileStorageTestFixture):
    """
    Tests for 'file_storage' IO module, used for writing to the file system.

    This class tests the behaviours of the WriteToFileOutputEvent in situations
    it should fail for environmental reasons (folders not existing, not having
    permissions, etc.)
    """

    async def test_output_invalid_dir(self, caplog: pytest.LogCaptureFixture) -> None:
        """
        File Storage test case: write a fixed string to a file.

        The event should be processed, and the file exist with the written contents.
        """

        with tempfile.TemporaryDirectory() as tmp_dir_path:
            _, output = self.prepare_io_config(tmp_dir_path + "_")

            file_path = os.path.join(tmp_dir_path + "_", "test_file.test")

            contents = "Hello"

            event = WriteToFileOutputEvent(path=file_path, file_contents=contents)
            assert not await output.output(event)

            assert len(caplog.records) == 1

            record: logging.LogRecord = caplog.records[0]
            assert record.msg == "Cannot output - base path '%s' does not exist"

    @pytest.mark.skipif(
        sys.platform.lower().startswith("win"), reason="Linux (like) only test"
    )
    async def test_create_dir_no_permissions(self, caplog: pytest.LogCaptureFixture) -> None:
        """
        File Storage test case: write a fixed string to a file.

        The event should be processed, and the file exist with the written contents.
        """

        with tempfile.TemporaryDirectory() as tmp_dir_path:
            _, output = self.prepare_io_config(tmp_dir_path)
            os.chmod(tmp_dir_path, 0o500)

            file_path = os.path.join(tmp_dir_path, "test")
            event = CreateDirectoryOutputEvent(path=file_path)
            assert not await output.output(event)
            assert not os.path.exists(file_path)
            assert len(caplog.records) == 1

            record: logging.LogRecord = caplog.records[0]
            assert record.msg == "Unable to create directory %s - PermissionError"

    @pytest.mark.skipif(
        sys.platform.lower().startswith("win"), reason="Linux (like) only test"
    )
    async def test_output_no_permissions(self, caplog: pytest.LogCaptureFixture) -> None:
        """
        File Storage test case: write a fixed string to a file.

        The event should be processed, and the file exist with the written contents.
        """

        with tempfile.TemporaryDirectory() as tmp_dir_path:
            _, output = self.prepare_io_config(tmp_dir_path)
            os.chmod(tmp_dir_path, 0o500)

            file_path = os.path.join(tmp_dir_path, "test_file.test")

            contents = "Hello"

            event = WriteToFileOutputEvent(path=file_path, file_contents=contents)
            assert not await output.output(event)
            assert not os.path.exists(file_path)
            assert len(caplog.records) == 1

            record: logging.LogRecord = caplog.records[0]
            assert record.msg == "Unable to write file %s - PermissionError"

    @pytest.mark.skipif(
        sys.platform.lower().startswith("win"), reason="Linux (like) only test"
    )
    async def test_delete_no_permissions(self, caplog: pytest.LogCaptureFixture) -> None:
        """
        File Storage test case: write a fixed string to a file.

        The event should be processed, and the file exist with the written contents.
        """

        with tempfile.TemporaryDirectory() as tmp_dir_path:
            _, output = self.prepare_io_config(tmp_dir_path)

            file_path = os.path.join(tmp_dir_path, "test_file.test")
            with open(file_path, "wb"):
                pass

            os.chmod(tmp_dir_path, 0o500)

            event = DeleteFileOutputEvent(path=file_path)
            assert not await output.output(event)
            assert os.path.exists(file_path)
            assert len(caplog.records) == 1

            record: logging.LogRecord = caplog.records[0]
            assert record.msg == "Unable to delete %s - PermissionError"

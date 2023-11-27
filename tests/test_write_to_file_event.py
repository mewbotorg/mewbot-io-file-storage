#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2021 - 2023 Mewbot Developers <mewbot@quicksilver.london>
#
# SPDX-License-Identifier: BSD-2-Clause


"""
Tests for 'file_storage' IO module, used for writing to the file system.

This class tests the behaviours of the WriteToFileOutputEvent.
"""

# pylint: disable=duplicate-code

import logging
import os
import sys
import tempfile

import pytest

from mewbot.io.file_storage import WriteToFileOutputEvent
from tests.base import FileStorageTestFixture


class TestWriteToFileOutputEventHandling(FileStorageTestFixture):
    """
    Tests for 'file_storage' IO module, used for writing to the file system.

    This class tests the behaviours of the WriteToFileOutputEvent.
    """

    async def test_output_create_file_str(self) -> None:
        """
        File Storage test case: write a fixed string to a file.

        The event should be processed, and the file exist with the written contents.
        """

        # Bandit considers tempfile.mktemp(dir=self.path) insecure
        # Changing to explicitly working in temporary directories
        with tempfile.TemporaryDirectory() as tmp_dir_path:
            _, output = self.prepare_io_config(tmp_dir_path)

            file_path = os.path.join(tmp_dir_path, "test_file.test")

            contents = "Hello"

            event = WriteToFileOutputEvent(path=file_path, file_contents=contents)
            assert await output.output(event)

            assert os.path.exists(file_path)

            with open(file_path, encoding="utf-8") as file:
                assert file.read() == contents

    async def test_output_create_nested_file_str(self) -> None:
        """
        File Storage test case: write a fixed string to a file in a sub folder.

        The event should be processed, with the intermediate folder being
        auto-created, and the file exist with the written contents.
        """
        with tempfile.TemporaryDirectory() as tmp_dir_path:
            _, output = self.prepare_io_config(tmp_dir_path)

            file_path = tmp_dir_path + "/foo/bar"
            contents = "Hello"

            event = WriteToFileOutputEvent(path=file_path, file_contents=contents)
            assert await output.output(event)

            assert os.path.exists(file_path)

            with open(file_path, encoding="utf-8") as file:
                assert file.read() == contents

    async def test_output_create_file_bytes(self) -> None:
        """
        File Storage test case: write bytes to a file in the main folder.


        """
        with tempfile.TemporaryDirectory() as tmp_dir_path:
            _, output = self.prepare_io_config(tmp_dir_path)

            file_path = os.path.join(tmp_dir_path, "output_bytes.bin")
            contents = b"Hello"

            event = WriteToFileOutputEvent(path=file_path, file_contents=contents)
            assert await output.output(event)

            assert os.path.exists(file_path)
            with open(file_path, "rb") as file:
                assert file.read() == contents

    @pytest.mark.skipif(
        sys.platform.lower().startswith("win"), reason="Linux (like) only test"
    )
    async def test_output_write_file_root_fails_linux(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        """
        File Storage test case: Writing to the root of a drive should fail.
        """

        with tempfile.TemporaryDirectory() as tmp_dir_path:
            _, output = self.prepare_io_config(tmp_dir_path)

            file_path = "/"
            event = WriteToFileOutputEvent(path=file_path, file_contents="Hello")

            # pylint: disable=protected-access
            with caplog.at_level(logging.WARNING, output._logger.name):
                assert not await output.output(event)

            assert len(caplog.records) == 1
            assert caplog.records[0].msg == self.ERROR_MESSAGE_OUTSIDE_BASE_PATH
            assert not os.path.isfile(file_path)

    @pytest.mark.skipif(
        not sys.platform.lower().startswith("win"), reason="Windows only test"
    )
    async def test_output_write_file_root_fails_windows(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        """
        File Storage test case: Writing to the root of a drive should fail.
        """

        with tempfile.TemporaryDirectory() as tmp_dir_path:
            _, output = self.prepare_io_config(tmp_dir_path)

            file_path = "C:\\"
            event = WriteToFileOutputEvent(path=file_path, file_contents="Hello")

            # pylint: disable=protected-access
            with caplog.at_level(logging.WARNING, output._logger.name):
                assert not await output.output(event)

            assert len(caplog.records) == 1
            assert caplog.records[0].msg == self.ERROR_MESSAGE_OUTSIDE_BASE_PATH
            assert not os.path.isfile(file_path)

    async def test_output_write_file_relative(self, caplog: pytest.LogCaptureFixture) -> None:
        """
        File Storage test case: Use a relative path to try writing outside the output folder.

        FIXME: Write this
        """

        with tempfile.TemporaryDirectory() as tmp_dir_path:
            _, output = self.prepare_io_config(tmp_dir_path)

            file_path = tmp_dir_path + "/../foo"

            event = WriteToFileOutputEvent(
                path=file_path,
                file_contents="Hello",
            )

            # pylint: disable=protected-access
            with caplog.at_level(logging.WARNING, output._logger.name):
                assert not await output.output(event)

            assert len(caplog.records) == 1
            assert caplog.records[0].msg == self.ERROR_MESSAGE_OUTSIDE_BASE_PATH
            assert not os.path.exists(file_path)
            assert not os.path.exists(file_path)

    async def test_output_create_file_overwrite(self) -> None:
        """
        File Storage test case: Output a file over the top of an existing one.
        """
        with tempfile.TemporaryDirectory() as tmp_dir_path:
            _, output = self.prepare_io_config(tmp_dir_path)

            file_path = os.path.join(tmp_dir_path, "test_file_out.txt")
            initial_contents = "Hello"
            contents = "Goodbye"

            with open(file_path, "w", encoding="utf-8") as file:
                file.write(initial_contents)

            event = WriteToFileOutputEvent(path=file_path, file_contents=contents)
            assert await output.output(event)

            assert os.path.exists(file_path)
            with open(file_path, encoding="utf-8") as file:
                assert file.read() == contents

    async def test_output_create_file_no_overwrite(self) -> None:
        """
        File Storage test case: Attempt to overwrite a file with overwrite True and not.
        """
        with tempfile.TemporaryDirectory() as tmp_dir_path:
            _, output = self.prepare_io_config(tmp_dir_path)

            file_path = os.path.join(tmp_dir_path, "test_file_out.txt")
            initial_contents = "Hello"
            contents = "Goodbye"

            with open(file_path, "w", encoding="utf-8") as file:
                file.write(initial_contents)

            event = WriteToFileOutputEvent(
                path=file_path, file_contents=contents, may_overwrite=False
            )
            assert not await output.output(event)

            with open(file_path, encoding="utf-8") as file:
                assert file.read() == initial_contents

    async def test_output_create_file_append(self) -> None:
        """
        File Storage test case: Attempt to append to an existing file.
        """

        with tempfile.TemporaryDirectory() as tmp_dir_path:
            _, output = self.prepare_io_config(tmp_dir_path)

            file_path = os.path.join(tmp_dir_path, "some_kinda_test_file.txt")
            contents_1 = "Hello"
            contents_2 = "Goodbye"

            with open(file_path, "w", encoding="utf-8") as file:
                file.write(contents_1)

            event = WriteToFileOutputEvent(
                path=file_path, file_contents=contents_2, append=True
            )
            assert await output.output(event)

            assert os.path.exists(file_path)
            with open(file_path, encoding="utf-8") as file:
                assert file.read() == contents_1 + contents_2

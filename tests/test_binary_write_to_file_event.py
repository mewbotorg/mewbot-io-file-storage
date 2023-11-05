#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2021 - 2023 Mewbot Developers <mewbot@quicksilver.london>
#
# SPDX-License-Identifier: BSD-2-Clause


"""
Tests for 'file_storage' IO module, used for writing to the file system.

This class tests the behaviours of the WriteToFileOutputEvent - in binary write mode.
"""

import logging
import os
import sys
import tempfile

import pytest

from mewbot.io.file_storage import WriteToFileOutputEvent
from tests.base import FileStorageTestFixture


class TestBinaryWriteToFileOutputEventHandling(FileStorageTestFixture):
    """
    Tests for 'file_storage' IO module, used for writing to the file system.

    This class tests the behaviours of the WriteToFileOutputEvent in binary mode.
    """

    async def test_output_create_file_binary_str(self) -> None:
        """
        File Storage test case: write a fixed binary string to a file.

        The event should be processed, and the file exist with the written contents.
        """

        # Bandit considers tempfile.mktemp(dir=self.path) insecure
        # Changing to explicitly working in temporary directories
        with tempfile.TemporaryDirectory() as tmp_dir_path:
            _, output = self.prepare_io_config(tmp_dir_path)

            file_path = os.path.join(tmp_dir_path, "test_file.test")

            contents = b"Hello'~~~~~====\xc2\xa3'"

            event = WriteToFileOutputEvent(path=file_path, file_contents=contents)
            assert await output.output(event)

            assert os.path.exists(file_path)

            with open(file_path, mode="rb") as file:
                assert file.read() == contents

    async def test_output_create_nested_file_binary_str(self) -> None:
        """
        File Storage test case: write a fixed binary string to a file in a sub folder.

        The intermediate folder should be auto-created, and the file created with the written
        contents.
        """
        with tempfile.TemporaryDirectory() as tmp_dir_path:
            _, output = self.prepare_io_config(tmp_dir_path)

            file_path = tmp_dir_path + "/foo/bar"
            contents = b"Hello'~~~~~====\xc2\xa3'"

            event = WriteToFileOutputEvent(path=file_path, file_contents=contents)
            assert await output.output(event)

            assert os.path.exists(file_path)

            with open(file_path, mode="rb") as file:
                assert file.read() == contents

    async def test_output_create_file_ascii_bytes(self) -> None:
        """
        File Storage test case: write bytes to a file in the main folder.


        """
        with tempfile.TemporaryDirectory() as tmp_dir_path:
            _, output = self.prepare_io_config(tmp_dir_path)

            file_path = os.path.join(tmp_dir_path, "output_bytes.bin")
            contents = b"Hello with just ascii"

            event = WriteToFileOutputEvent(path=file_path, file_contents=contents)
            assert await output.output(event)

            assert os.path.exists(file_path)
            with open(file_path, "rb") as file:
                assert file.read() == contents

    @pytest.mark.skipif(
        sys.platform.lower().startswith("win"), reason="Linux (like) only test"
    )
    async def test_output_write_file_root_binary_fails_linux(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        """
        File Storage test case: Writing to the root of a drive should fail.
        """

        with tempfile.TemporaryDirectory() as tmp_dir_path:
            _, output = self.prepare_io_config(tmp_dir_path)

            file_path = "/"
            event = WriteToFileOutputEvent(path=file_path, file_contents=b"Hello")

            # pylint: disable=protected-access
            with caplog.at_level(logging.WARNING, output._logger.name):
                assert not await output.output(event)

            assert len(caplog.records) == 1
            assert caplog.records[0].msg == self.ERROR_MESSAGE_OUTSIDE_BASE_PATH
            assert not os.path.isfile(file_path)

    @pytest.mark.skipif(
        not sys.platform.lower().startswith("win"), reason="Windows only test"
    )
    async def test_output_write_file_root_binary_fails_windows(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        """
        File Storage test case: Writing to the root of a drive should fail.
        """

        with tempfile.TemporaryDirectory() as tmp_dir_path:
            _, output = self.prepare_io_config(tmp_dir_path)

            file_path = "C:\\"
            event = WriteToFileOutputEvent(path=file_path, file_contents=b"Hello")

            # pylint: disable=protected-access
            with caplog.at_level(logging.WARNING, output._logger.name):
                assert not await output.output(event)

            assert len(caplog.records) == 1
            assert caplog.records[0].msg == self.ERROR_MESSAGE_OUTSIDE_BASE_PATH
            assert not os.path.isfile(file_path)

    async def test_output_write_binary_file_relative(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        """
        File Storage test case: Use a relative path to try writing outside the output folder.
        """

        with tempfile.TemporaryDirectory() as tmp_dir_path:
            _, output = self.prepare_io_config(tmp_dir_path)

            file_path = tmp_dir_path + "/../foo"

            event = WriteToFileOutputEvent(
                path=file_path,
                file_contents=b"Hello'~~~~~====\xc2\xa3'",
            )

            # pylint: disable=protected-access
            with caplog.at_level(logging.WARNING, output._logger.name):
                assert not await output.output(event)

            assert len(caplog.records) == 1
            assert caplog.records[0].msg == self.ERROR_MESSAGE_OUTSIDE_BASE_PATH
            assert not os.path.exists(file_path)
            assert not os.path.exists(file_path)

    async def test_output_create_binary_file_overwrite(self) -> None:
        """
        File Storage test case: Output a file over the top of an existing one.
        """
        with tempfile.TemporaryDirectory() as tmp_dir_path:
            _, output = self.prepare_io_config(tmp_dir_path)

            file_path = os.path.join(tmp_dir_path, "test_file_out.txt")
            initial_contents = b"Hello'~~~~~====\xc2\xa3'"
            contents = b"Goodbye - Hello'~~~~~====\xc2\xa3'"

            with open(file_path, "wb") as file:
                file.write(initial_contents)

            event = WriteToFileOutputEvent(path=file_path, file_contents=contents)
            assert await output.output(event)

            assert os.path.exists(file_path)
            with open(file_path, "rb") as file:
                assert file.read() == contents

    async def test_output_create_binary_file_no_overwrite(self) -> None:
        """
        File Storage test case: Attempt to overwrite a file with overwrite True and not.
        """
        with tempfile.TemporaryDirectory() as tmp_dir_path:
            _, output = self.prepare_io_config(tmp_dir_path)

            file_path = os.path.join(tmp_dir_path, "test_file_out.txt")
            initial_contents = b"Hello'~~~~~====\xc2\xa3'"
            contents = b"Goodbye - Hello'~~~~~====\xc2\xa3'"

            with open(file_path, "wb") as file:
                file.write(initial_contents)

            event = WriteToFileOutputEvent(
                path=file_path, file_contents=contents, may_overwrite=False
            )
            assert not await output.output(event)

            with open(file_path, "rb") as file:
                assert file.read() == initial_contents

    async def test_output_create_binary_file_append(self) -> None:
        """
        File Storage test case: Attempt to append to an existing file.
        """

        with tempfile.TemporaryDirectory() as tmp_dir_path:
            _, output = self.prepare_io_config(tmp_dir_path)

            file_path = os.path.join(tmp_dir_path, "some_kinda_test_file.txt")
            contents_1 = b"Hello'~~~~~====\xc2\xa3'"
            contents_2 = b"Goodbye - Hello'~~~~~====\xc2\xa3'"

            with open(file_path, "wb") as file:
                file.write(contents_1)

            event = WriteToFileOutputEvent(
                path=file_path, file_contents=contents_2, append=True
            )
            assert await output.output(event)

            assert os.path.exists(file_path)
            with open(file_path, "rb") as file:
                assert file.read() == contents_1 + contents_2

    async def test_output_write_binary_file_relative_path_up_one_level(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        """
        File Storage test case: Use a relative path to try writing outside the output folder.
        """

        with tempfile.TemporaryDirectory() as tmp_dir_path:
            _, output = self.prepare_io_config(tmp_dir_path)

            file_path = tmp_dir_path + "../foo"

            event = WriteToFileOutputEvent(
                path=file_path,
                file_contents=b"Hello'~~~~~====\xc2\xa3'",
            )

            # pylint: disable=protected-access
            with caplog.at_level(logging.WARNING, output._logger.name):
                assert not await output.output(event)

            assert len(caplog.records) == 1
            assert caplog.records[0].msg == self.ERROR_MESSAGE_OUTSIDE_BASE_PATH
            assert not os.path.exists(file_path)
            assert not os.path.exists(file_path)

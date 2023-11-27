#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2021 - 2023 Mewbot Developers <mewbot@quicksilver.london>
#
# SPDX-License-Identifier: BSD-2-Clause


"""
Tests for 'file_storage' IO module, used for writing to the file system.

This class tests the behaviours of the WriteToFileOutputEvent and CreateDirectoryOutputEvent.
In particular, when we attempt to output to a directory which does not exist.
"""

# Need some very similar code to test behavior on windows and linux systems
# pylint: disable=duplicate-code

import logging
import os
import sys
import tempfile

import pytest

from mewbot.io.file_storage import CreateDirectoryOutputEvent, WriteToFileOutputEvent
from tests.base import FileStorageTestFixture


class TestCreateDirectoryOutputEventHandlingBadRootLoc(FileStorageTestFixture):
    """
    Tests for 'file_storage' IO module, used for writing to the file system.

    This class tests the behaviours of the CreateDirectoryOutputEvent.
    """

    async def test_output_create_dir_when_root_does_not_exist(self) -> None:
        """
        File Storage test case: create a directory.

        The event should succeed and the directory will be created.
        """
        # Get a plausible looking dir for the system to test with
        with tempfile.TemporaryDirectory() as bad_tmp_path:
            pass

        _, output = self.prepare_io_config(bad_tmp_path)

        dir_path = os.path.join(bad_tmp_path, "test_dir")

        assert not os.path.exists(dir_path)
        assert not os.path.isdir(dir_path)

        event = CreateDirectoryOutputEvent(path=dir_path)
        assert not await output.output(event)

        assert not os.path.exists(dir_path)
        assert not os.path.isdir(dir_path)

    async def test_output_create_nested_dir_os_join_in_bad_dir(self) -> None:
        """
        File Storage test case: Create nested dirs with a path created with os.join.

        (As this may behave different on different systems).
        """

        # Get a plausible looking dir for the system to test with
        with tempfile.TemporaryDirectory() as bad_tmp_path:
            pass

        _, output = self.prepare_io_config(bad_tmp_path)

        file_path = os.path.join(bad_tmp_path, "foo", "bar")

        event = CreateDirectoryOutputEvent(path=file_path)
        assert not await output.output(event)

        assert not os.path.exists(file_path)
        assert not os.path.isdir(file_path)

    async def test_output_create_nested_dir_adding_relative_path_in_bad_dir(self) -> None:
        """
        File Storage test case: Create nested dirs with a path created by adding relative paths.

        (As this may behave different on different systems).
        """
        # Get a plausible looking dir for the system to test with
        with tempfile.TemporaryDirectory() as bad_tmp_path:
            pass

        _, output = self.prepare_io_config(bad_tmp_path)

        file_path = bad_tmp_path + "/foo/bar"

        event = CreateDirectoryOutputEvent(path=file_path)
        assert not await output.output(event)

        assert not os.path.exists(file_path)
        assert not os.path.isdir(file_path)

    @pytest.mark.skipif(
        not sys.platform.lower().startswith("win"), reason="Windows only test"
    )
    async def test_output_create_dir_nonsense_path_windows(self) -> None:
        """
        File Storage test case: Attempt to create a dir at a nonsense path.
        """
        with tempfile.TemporaryDirectory() as tmp_dir_path:
            _, output = self.prepare_io_config(tmp_dir_path)

            test_dir_path = os.path.join(
                tmp_dir_path, "F:\\//utter_nonsense\\////\\//should not work"
            )

            event = CreateDirectoryOutputEvent(path=test_dir_path)
            assert not await output.output(event)

            assert not os.path.exists(test_dir_path)
            assert not os.path.isdir(test_dir_path)

    @pytest.mark.skipif(sys.platform.lower().startswith("win"), reason="Linux only test")
    async def test_output_create_dir_nonsense_path_linux(self) -> None:
        """
        File Storage test case: Attempt to create a dir at a nonsense path.
        """
        with tempfile.TemporaryDirectory() as tmp_dir_path:
            _, output = self.prepare_io_config(tmp_dir_path)

            test_dir_path = os.path.join(
                tmp_dir_path, "F:\\//utter_nonsense\\////\\//should not work"
            )

            event = CreateDirectoryOutputEvent(path=test_dir_path)
            assert await output.output(event)

            assert os.path.exists(test_dir_path)
            assert os.path.isdir(test_dir_path)

    async def test_output_create_parent_dir_outside_bad_dir_windows(self) -> None:
        """
        File Storage test case: Relative path which points to the parent.
        """

        # Get a plausible looking dir for the system to test with
        with tempfile.TemporaryDirectory() as bad_tmp_path:
            pass

        _, output = self.prepare_io_config(bad_tmp_path)

        file_path = bad_tmp_path + "/.."

        assert os.path.exists(file_path)

        event = CreateDirectoryOutputEvent(path=file_path)
        assert not await output.output(event)

        # The parent already existed
        assert os.path.exists(file_path)
        assert os.path.isdir(file_path)

    async def test_output_create_parent_dir_outside_bad_dir_linux(self) -> None:
        """
        File Storage test case: Relative path which points to the parent.
        """

        # Get a plausible looking dir for the system to test with
        with tempfile.TemporaryDirectory() as bad_tmp_path:
            pass

        _, output = self.prepare_io_config(bad_tmp_path)

        file_path = bad_tmp_path + "/.."

        assert os.path.exists(file_path)

        event = CreateDirectoryOutputEvent(path=file_path)
        assert not await output.output(event)

        # The parent already existed
        assert os.path.exists(file_path)
        assert os.path.isdir(file_path)


class TestCreateFileOutputEventHandlingBadRootLoc(FileStorageTestFixture):
    """
    Tests for 'file_storage' IO module, used for writing to the file system.

    This class tests the behaviours of the WriteToFileOutputEvent.
    """

    async def test_output_create_file_str_in_bad_root(self) -> None:
        """
        File Storage test case: write a fixed string to a file in a root which is not valid.

        The event should be processed, and the file exist with the written contents.
        """

        # Get a plausible looking dir for the system to test with
        with tempfile.TemporaryDirectory() as bad_tmp_path:
            pass

        _, output = self.prepare_io_config(bad_tmp_path)
        file_path = os.path.join(bad_tmp_path, "test_file.test")

        contents = "Hello"

        event = WriteToFileOutputEvent(path=file_path, file_contents=contents)
        assert not await output.output(event)

        assert not os.path.exists(file_path)

    async def test_output_create_nested_file_str_in_bad_root_loc(self) -> None:
        """
        File Storage test case: write a fixed string to a file in a sub folder.

        The event should be processed, with the intermediate folder being
        auto-created, and the file exist with the written contents.
        """
        # Get a plausible looking dir for the system to test with
        with tempfile.TemporaryDirectory() as bad_tmp_path:
            pass

        _, output = self.prepare_io_config(bad_tmp_path)

        file_path = bad_tmp_path + "/foo/bar"
        contents = "Hello"

        event = WriteToFileOutputEvent(path=file_path, file_contents=contents)
        assert not await output.output(event)

        assert not os.path.exists(file_path)

    async def test_output_create_file_bytes_bad_root_loc(self) -> None:
        """
        File Storage test case: write bytes to a file in the main folder.


        """
        with tempfile.TemporaryDirectory() as bad_tmp_path:
            pass

        _, output = self.prepare_io_config(bad_tmp_path)

        file_path = os.path.join(bad_tmp_path, "output_bytes.bin")
        contents = b"Hello"

        event = WriteToFileOutputEvent(path=file_path, file_contents=contents)
        assert not await output.output(event)

        assert not os.path.exists(file_path)

    async def test_output_write_file_relative_bad_root_loc(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        """
        File Storage test case: Use a relative path to try writing outside the output folder.
        """

        with tempfile.TemporaryDirectory() as bad_tmp_path:
            pass

        _, output = self.prepare_io_config(bad_tmp_path)

        file_path = bad_tmp_path + "/../foo"

        event = WriteToFileOutputEvent(
            path=file_path,
            file_contents="Hello",
        )

        # pylint: disable=protected-access
        with caplog.at_level(logging.WARNING, output._logger.name):
            assert not await output.output(event)

        assert len(caplog.records) == 1
        assert caplog.records[0].msg == self.ERROR_MESSAGE_BAD_ROOT_LOC
        assert not os.path.exists(file_path)
        assert not os.path.exists(file_path)


class TestBinaryWriteToFileOutputEventHandlingBadRoot(FileStorageTestFixture):
    """
    Tests for 'file_storage' IO module, used for writing to the file system.

    This class tests the behaviours of the WriteToFileOutputEvent in binary mode.
    """

    async def test_output_create_file_binary_str_bad_root_loc(self) -> None:
        """
        File Storage test case: write a fixed binary string to a file.

        The event should be processed, and the file exist with the written contents.
        """

        with tempfile.TemporaryDirectory() as bad_tmp_path:
            pass

        _, output = self.prepare_io_config(bad_tmp_path)

        file_path = os.path.join(bad_tmp_path, "test_file.test")

        contents = b"Hello'~~~~~====\xc2\xa3'"

        event = WriteToFileOutputEvent(path=file_path, file_contents=contents)
        assert not await output.output(event)

        assert not os.path.exists(file_path)

    async def test_output_create_nested_file_binary_str_bad_root_loc(self) -> None:
        """
        File Storage test case: write a fixed binary string to a file in a sub folder.

        The intermediate folder should be auto-created, and the file created with the written
        contents.
        """
        with tempfile.TemporaryDirectory() as bad_tmp_path:
            pass

        _, output = self.prepare_io_config(bad_tmp_path)

        file_path = bad_tmp_path + "/foo/bar"
        contents = b"Hello'~~~~~====\xc2\xa3'"

        event = WriteToFileOutputEvent(path=file_path, file_contents=contents)
        assert not await output.output(event)

        assert not os.path.exists(file_path)

    async def test_output_create_file_ascii_bytes_bad_root_loc(self) -> None:
        """
        File Storage test case: write bytes to a file in the main folder - which does not exist.


        """
        with tempfile.TemporaryDirectory() as bad_tmp_path:
            pass

        _, output = self.prepare_io_config(bad_tmp_path)

        file_path = os.path.join(bad_tmp_path, "output_bytes.bin")
        contents = b"Hello with just ascii"

        event = WriteToFileOutputEvent(path=file_path, file_contents=contents)
        assert not await output.output(event)

        assert not os.path.exists(file_path)

    async def test_output_write_binary_file_relative(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        """
        File Storage test case: Use a relative path to try writing outside the output folder.
        """

        with tempfile.TemporaryDirectory() as bad_tmp_path:
            pass

        _, output = self.prepare_io_config(bad_tmp_path)

        file_path = bad_tmp_path + "/../foo"

        event = WriteToFileOutputEvent(
            path=file_path,
            file_contents=b"Hello'~~~~~====\xc2\xa3'",
        )

        # pylint: disable=protected-access
        with caplog.at_level(logging.WARNING, output._logger.name):
            assert not await output.output(event)

        assert len(caplog.records) == 1
        assert caplog.records[0].msg == self.ERROR_MESSAGE_BAD_ROOT_LOC
        assert not os.path.exists(file_path)
        assert not os.path.exists(file_path)

    async def test_output_write_binary_file_relative_path_up_one_level_bad_root_loc(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        """
        File Storage test case: Use a relative path to try writing outside the output folder.
        """

        with tempfile.TemporaryDirectory() as bad_tmp_path:
            pass

        _, output = self.prepare_io_config(bad_tmp_path)

        file_path = bad_tmp_path + "../foo"

        event = WriteToFileOutputEvent(
            path=file_path,
            file_contents=b"Hello'~~~~~====\xc2\xa3'",
        )

        # pylint: disable=protected-access
        with caplog.at_level(logging.WARNING, output._logger.name):
            assert not await output.output(event)

        assert len(caplog.records) == 1
        assert caplog.records[0].msg == self.ERROR_MESSAGE_BAD_ROOT_LOC
        assert not os.path.exists(file_path)
        assert not os.path.exists(file_path)

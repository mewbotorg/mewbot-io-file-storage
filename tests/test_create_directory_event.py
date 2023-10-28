#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2021 - 2023 Mewbot Developers <mewbot@quicksilver.london>
#
# SPDX-License-Identifier: BSD-2-Clause


"""
Tests for 'file_storage' IO module, used for writing to the file system.

This class tests the behaviours of the WriteToFileOutputEvent.
"""

import os
import tempfile
import uuid

from mewbot.io.file_storage import CreateDirectoryOutputEvent
from tests.base import FileStorageTestFixture


class TestCreateDirectoryOutputEventHandling(FileStorageTestFixture):
    """
    Tests for 'file_storage' IO module, used for writing to the file system.

    This class tests the behaviours of the CreateDirectoryOutputEvent.
    """

    async def test_output_create_dir(self) -> None:
        """
        File Storage test case: create a directory.

        The event should succeed and the directory will be created.
        """

        with tempfile.TemporaryDirectory() as tmp_dir_path:
            _, output = self.prepare_io_config(tmp_dir_path)

            dir_path = os.path.join(tmp_dir_path, "test_dir")

            assert not os.path.exists(dir_path)
            assert not os.path.isdir(dir_path)

            event = CreateDirectoryOutputEvent(path=dir_path)
            assert await output.output(event)

            assert os.path.exists(dir_path)
            assert os.path.isdir(dir_path)

    async def test_output_create_nested_dir_os_join(self) -> None:
        """
        File Storage test case: Create nested dirs with a path created with os.join.

        (As this may behave different on different systems).
        """

        with tempfile.TemporaryDirectory() as tmp_dir_path:
            _, output = self.prepare_io_config(tmp_dir_path)

            file_path = os.path.join(tmp_dir_path, "foo", "bar")

            event = CreateDirectoryOutputEvent(path=file_path)
            assert await output.output(event)

            assert os.path.exists(file_path)
            assert os.path.isdir(file_path)

    async def test_output_create_nested_dir_adding_relative_path(self) -> None:
        """
        File Storage test case: Create nested dirs with a path created by adding relative paths.

        (As this may behave different on different systems).
        """

        with tempfile.TemporaryDirectory() as tmp_dir_path:
            _, output = self.prepare_io_config(tmp_dir_path)

            file_path = tmp_dir_path + "/foo/bar"

            event = CreateDirectoryOutputEvent(path=file_path)
            assert await output.output(event)

            assert os.path.exists(file_path)
            assert os.path.isdir(file_path)

    async def test_output_create_existing_dir(self) -> None:
        """
        File Storage test case: Creating a dir where one already exists should pass without error.

        And not erase the existing dir, or something equally weird.
        """

        with tempfile.TemporaryDirectory() as tmp_dir_path:
            _, output = self.prepare_io_config(tmp_dir_path)

            dir_path = os.path.join(tmp_dir_path, "test_dir")

            os.mkdir(dir_path)

            canary_file_contents = f"{str(uuid.uuid4())}"
            canary_file_path = os.path.join(tmp_dir_path, "canary_file.txt")
            with open(canary_file_path, "w", encoding="utf-8") as canary_outfile:
                canary_outfile.write(canary_file_contents)

            event = CreateDirectoryOutputEvent(path=dir_path)
            assert await output.output(event)

            assert os.path.exists(dir_path)
            assert os.path.isdir(dir_path)

            # Check the canary file
            with open(canary_file_path, "r", encoding="utf-8") as canary_infile:
                assert canary_infile.read() == canary_file_contents

    async def test_output_create_parent_dir(self) -> None:
        """
        File Storage test case: Relative path which points to the parent.
        """

        with tempfile.TemporaryDirectory() as tmp_dir_path:
            _, output = self.prepare_io_config(tmp_dir_path)

            file_path = tmp_dir_path + "/.."

            event = CreateDirectoryOutputEvent(path=file_path)
            assert not await output.output(event)

            assert os.path.exists(file_path)
            assert os.path.isdir(file_path)

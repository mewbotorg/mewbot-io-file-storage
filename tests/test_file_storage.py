#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2021 - 2023 Mewbot Developers <mewbot@quicksilver.london>
#
# SPDX-License-Identifier: BSD-2-Clause

"""
Tests for 'file_storage' IO module, used for writing to the file system.
"""

from __future__ import annotations

import logging
import os
import tempfile

import pytest
from mewbot.api.v1 import OutputEvent

from mewbot.io.file_storage import (
    CreateDirectoryOutputEvent,
    DeleteFileOutputEvent,
    FileStorage,
    FileStorageOutput,
    WriteToFileOutputEvent,
)
from mewbot.io.file_storage.events import FSOutputEvent
from tests.base import FileStorageTestFixture


class TestFileTypeFileStorage(FileStorageTestFixture):
    """
    File Storage test cases: handle non-output event test cases.
    """

    async def test_config_init_no_path(self) -> None:
        """
        File Storage test case: check that creation of the config with a path.

        Result should be a config with the given path, that reports the path as existing.
        """

        with pytest.raises(ValueError, match="FileStorage initialised without path"):
            FileStorage()

    async def test_config_init(self) -> None:
        """
        File Storage test case: check that creation of the config with a path.

        Result should be a config with the given path, that reports the path as existing.
        """

        with tempfile.TemporaryDirectory() as tmp_dir_path:
            config = FileStorage(path=tmp_dir_path)

            assert config.path == tmp_dir_path
            assert config.path_exists

            inputs = config.get_inputs()
            assert isinstance(inputs, list)
            assert len(inputs) == 0

            outputs = config.get_outputs()
            assert isinstance(outputs, list)
            assert len(outputs) == 1

            output = outputs[0]
            assert isinstance(output, FileStorageOutput)
            assert output.path == tmp_dir_path
            assert output.path_exists

    async def test_config_init_with_no_node(self) -> None:
        """
        File Storage test case: creation with a non-existent path.

        Result should be a config with the given path, that reports the path as not existing.
        """

        with tempfile.TemporaryDirectory() as tmp_dir_path:
            _, output = self.prepare_io_config(tmp_dir_path)

            file_path = os.path.join(tmp_dir_path, "not_a_file.tmp")
            config = FileStorage(path=file_path)

            assert config.path == file_path
            assert not config.path_exists

            outputs = config.get_outputs()
            assert isinstance(outputs, list)
            assert len(outputs) == 1

            output = outputs[0]
            assert isinstance(output, FileStorageOutput)
            assert output.path == file_path
            assert not output.path_exists

    async def test_output_init_with_file(self) -> None:
        """
        File Storage test case: creation with a path that exists as a file.

        Result should be a config with the given path, that reports the path
        as not existing, as it is not a directory.
        """

        with tempfile.TemporaryDirectory() as tmp_dir_path:
            _, output = self.prepare_io_config(tmp_dir_path)

            file_path = os.path.join(tmp_dir_path, "test_bin_file.bin")

            with open(file_path, "wb") as write:
                write.write(b"")

            config = FileStorage(path=file_path)

            assert config.path == file_path
            assert not config.path_exists

            outputs = config.get_outputs()
            assert isinstance(outputs, list)
            assert len(outputs) == 1

            output = outputs[0]
            assert isinstance(output, FileStorageOutput)
            assert output.path == file_path
            assert not output.path_exists

    async def test_output_update_path(self) -> None:
        """
        File Storage test case: changing the specified path on the fly.

        We confirm that the path value is updated in both the config and in
        the output. We also check that the existence check also updates dynamically.
        """

        with tempfile.TemporaryDirectory() as tmp_dir_path:
            _, output = self.prepare_io_config(tmp_dir_path)

            config = FileStorage(path=tmp_dir_path)
            output = config.get_outputs()[0]

            assert isinstance(output, FileStorageOutput)

            assert config.path == tmp_dir_path
            assert output.path == tmp_dir_path
            assert config.path_exists
            assert output.path_exists

            config.path = tmp_dir_path
            assert config.path == tmp_dir_path
            assert output.path == tmp_dir_path
            assert config.path_exists
            assert output.path_exists

            path = tmp_dir_path + "ssss"
            config.path = path
            assert config.path == path
            assert output.path == path
            assert not config.path_exists
            assert not output.path_exists

            config.path = tmp_dir_path
            assert config.path == tmp_dir_path
            assert output.path == tmp_dir_path
            assert config.path_exists
            assert output.path_exists

    def test_output_event_types(self) -> None:
        """
        File Storage test case: confirm the expected event types are in the output.
        """
        with tempfile.TemporaryDirectory() as tmp_dir_path:
            _, output = self.prepare_io_config(tmp_dir_path)

            events = output.consumes_outputs()

            assert isinstance(events, set)
            assert len(events) == 3

            assert WriteToFileOutputEvent in events
            assert DeleteFileOutputEvent in events
            assert CreateDirectoryOutputEvent in events

    async def test_output_event_bad_event(self, caplog: pytest.LogCaptureFixture) -> None:
        """
        File Storage test case: Attempt to output an invalid event.
        """

        with tempfile.TemporaryDirectory() as tmp_dir_path:
            _, output = self.prepare_io_config(tmp_dir_path)

            bad_path = os.path.join(tmp_dir_path, "not_a_dir")

            output = FileStorageOutput(bad_path)
            event = OutputEvent()

            # pylint: disable=protected-access
            with caplog.at_level(logging.WARNING, output._logger.name):
                assert not await output.output(event)

            assert len(caplog.records) == 1
            assert caplog.records[0].msg == "Received unexpected event type %s"

    async def test_output_event_bad_base_event(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        """
        File Storage test case: attempt to output the base FSOutputEvent.

        This should fail with by not handling the event, logging an error.
        """
        with tempfile.TemporaryDirectory() as tmp_dir_path:
            output = FileStorageOutput(tmp_dir_path)
            event = FSOutputEvent(tmp_dir_path)

            # pylint: disable=protected-access
            with caplog.at_level(logging.INFO, output._logger.name):
                assert not await output.output(event)

            assert len(caplog.records) == 1
            assert caplog.records[0].msg == "Received unexpected event type %s"

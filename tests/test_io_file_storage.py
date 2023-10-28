# SPDX-FileCopyrightText: 2023 Mewbot Developers <mewbot@quicksilver.london>
#
# SPDX-License-Identifier: BSD-2-Clause

"""
Tests for writing to the file system.
"""

from __future__ import annotations

from typing import Any, Sequence

import os.path
import tempfile

import pytest

from mewbot.io.file_storage import (
    CreateDirectoryOutputEvent,
    DeleteFileOutputEvent,
    FileStorage,
    FileStorageOutput,
    WriteToFileOutputEvent,
)


class TestFileTypeFileStorage:  # pylint: disable=too-many-public-methods
    """
    Tests the file storage backend - which writes and updates files on within a specified path.
    """

    @pytest.mark.asyncio
    async def test_output_init(self) -> None:
        """
        Tests the init method for the FileStorageOutput.

        :return:
        """
        with tempfile.TemporaryDirectory() as path:
            output = FileStorageOutput(path)

            assert output.path == path
            assert output.path_exists

    @pytest.mark.asyncio
    async def test_output_init_with_no_node(self) -> None:
        """
        Tests attempting to start the output with a non-existent target path.

        This should work - but output_path_exists should register as False.
        :return:
        """
        with tempfile.TemporaryDirectory() as path:
            file_path = os.path.join(path, "foo")

            output = FileStorageOutput(file_path)

            assert output.path == file_path
            assert not output.path_exists

    @pytest.mark.asyncio
    async def test_output_init_with_file(self) -> None:
        """
        Tests attempting to start the output with a non-existent target path.

        This should work - but output_path_exists should register as False.
        :return:
        """
        with tempfile.TemporaryDirectory() as path:
            file_path = os.path.join(path, "foo")

            with open(file_path, "wb") as write:
                write.write(b"")

            output = FileStorageOutput(file_path)

            assert output.path == file_path
            assert not output.path_exists

    @pytest.mark.asyncio
    async def test_output_update_path(self) -> None:
        """
        Tests that we can still output after updating the path which we're outputting to.

        :return:
        """
        with tempfile.TemporaryDirectory() as path:
            output = FileStorageOutput(path)

            assert output.path == path
            assert output.path_exists

            output.path = path
            assert output.path == path
            assert output.path_exists

            path = path + "ssss"
            output.path = path
            assert output.path == path
            assert not output.path_exists

    @pytest.mark.asyncio
    async def test_config_init(self) -> None:
        """
        Tests the config init function.

        :return:
        """
        with tempfile.TemporaryDirectory() as path:
            config = FileStorage(path=path)  # pylint: disable=unexpected-keyword-arg

            assert config.path == path

            inputs: Sequence[Any] = config.get_inputs()
            assert isinstance(inputs, list)
            assert len(inputs) == 0

            outputs: Sequence[Any] = config.get_outputs()
            assert isinstance(outputs, list)
            assert len(outputs) == 1

            output = outputs[0]
            assert isinstance(output, FileStorageOutput)
            assert output.path == path
            assert output.path_exists

    def test_output_event_types(self) -> None:
        """
        Tests that the declared possible output events are of the expected types.

        :return:
        """
        with tempfile.TemporaryDirectory() as path:
            output = FileStorageOutput(path)
            events = output.consumes_outputs()

            assert isinstance(events, set)
            assert len(events) == 3
            for event in events:
                assert event in (
                    WriteToFileOutputEvent,
                    DeleteFileOutputEvent,
                    CreateDirectoryOutputEvent,
                )


#     @pytest.mark.asyncio
#     async def test_output_event_bad_event(self) -> None:
#         with tempfile.TemporaryDirectory() as path:
#             bad_path = os.path.join(path, "foo")
#
#             output = FileStorageOutput(bad_path)
#             event = OutputEvent()
#             assert not await output.output(event)
#
#     @pytest.mark.asyncio
#     async def test_output_event_bad_event_2_path_same_as_output_path(self) -> None:
#         if os.name == "nt":
#             root_output_path = r"C:\Users\ADRIAN~1\AppData\Local\Temp\tmpyy700ab8"
#             async_root_output_path = AsyncWindowsPath(root_output_path)
#
#             tmp_example_path = "C:\\Users\\ADRIAN~1\\AppData\\Local\\Temp\\tmpyy700ab8"
#             async_tmp_example_path = AsyncWindowsPath(tmp_example_path)
#
#             assert (
#                 await async_root_output_path.resolve()
#                 == await async_tmp_example_path.resolve()
#             )
#
#             tmp_true_path = "C:/Users/Adriann Ves Bloche/AppData/Local/Temp/tmpyy700ab8"
#             async_tmp_true_path = AsyncWindowsPath(tmp_true_path)
#
#             assert (
#                 await async_tmp_example_path.resolve() == await async_tmp_true_path.resolve()
#             )
#
#             # On windows, the behavior seems to be different - you'd think this would work
#             assert not async_tmp_true_path.is_relative_to(async_tmp_example_path)
#             resolved_path = await async_tmp_example_path.resolve()
#             assert async_tmp_true_path.is_relative_to(resolved_path)  # type: ignore
#
#         with tempfile.TemporaryDirectory() as path:
#             output = FileStorageOutput(path)
#
#             event = FSOutputEvent(path)
#
#             with pytest.raises(NotImplementedError):
#                 await output.output(event)
#
#     @pytest.mark.asyncio
#     async def test_output_event_bad_event_3_base_event_type(self) -> None:
#         with tempfile.TemporaryDirectory() as path:
#             output = FileStorageOutput(path)
#
#             target_file_path = os.path.join(path, "foo")
#             event = FSOutputEvent(target_file_path)
#
#             with pytest.raises(NotImplementedError):
#                 await output.output(event)
#
#     @pytest.mark.asyncio
#     async def test_output_event_when_no_dir(self) -> None:
#         """
#         Tests trying to output to a FileStorageOutput initialized with a folder that does
#         not exist.
#         :return:
#         """
#         with tempfile.TemporaryDirectory() as path:
#             bad_path = os.path.join(path, "foo")
#
#             event = DeleteFileOutputEvent(path=bad_path)
#
#             output = FileStorageOutput(bad_path)
#             assert not await output.output(event)
#
#     @pytest.mark.asyncio
#     async def test_output_create_file_str(self) -> None:
#         with tempfile.TemporaryDirectory() as path:
#             file_path = os.path.join(path, "foo")
#             contents = "Hello"
#
#             output = FileStorageOutput(path)
#             event = WriteToFileOutputEvent(path=file_path, file_contents=contents)
#             assert await output.output(event)
#
#             assert os.path.exists(file_path)
#             with open(file_path, encoding="utf-8") as file:
#                 assert file.read() == contents
#
#     @pytest.mark.asyncio
#     async def test_output_create_file_bytes(self) -> None:
#         with tempfile.TemporaryDirectory() as path:
#             file_path = os.path.join(path, "foo")
#             contents = b"Hello"
#
#             output = FileStorageOutput(path)
#             event = WriteToFileOutputEvent(path=file_path, file_contents=contents)
#             assert await output.output(event)
#
#             assert os.path.exists(file_path)
#             with open(file_path, "rb") as file:
#                 assert file.read() == contents
#
#     @pytest.mark.asyncio
#     async def test_output_write_file_root(self) -> None:
#         with tempfile.TemporaryDirectory() as path:
#             if os.name != "nt":
#                 file_path = "/" + tempfile.mktemp()
#             else:
#                 file_path = "C:\\" + "test_name"
#                 assert not os.path.exists(file_path)
#
#             output = FileStorageOutput(path)
#             event = WriteToFileOutputEvent(
#                 path=file_path,
#                 file_contents="Hello",
#             )
#             assert not await output.output(event)
#             assert not os.path.exists(file_path)
#
#     @pytest.mark.asyncio
#     async def test_output_write_file_relative(self) -> None:
#         with tempfile.TemporaryDirectory() as path:
#             if os.name != "nt":
#                 file_path = path + "/../foo"
#             else:
#                 file_path = path + "\\..\\foo"
#
#             event = WriteToFileOutputEvent(
#                 path=file_path,
#                 file_contents="Hello",
#             )
#
#             output = FileStorageOutput(path)
#             assert not await output.output(event)
#             assert not os.path.exists(file_path)
#
#     @pytest.mark.asyncio
#     async def test_output_create_file_overwrite(self) -> None:
#         with tempfile.TemporaryDirectory() as path:
#             file_path = os.path.join(path, "foo")
#             initial_contents = "Hello"
#             contents = "Goodbye"
#
#             with open(file_path, "w", encoding="utf-8") as file:
#                 file.write(initial_contents)
#
#             output = FileStorageOutput(path)
#             event = WriteToFileOutputEvent(path=file_path, file_contents=contents)
#             assert await output.output(event)
#
#             assert os.path.exists(file_path)
#             with open(file_path, encoding="utf-8") as file:
#                 assert file.read() == contents
#
#     @pytest.mark.asyncio
#     async def test_output_create_file_no_overwrite(self) -> None:
#         """
#         Create a file, then attempt to overwrite it with may_overwrite False
#         :return:
#         """
#
#         with tempfile.TemporaryDirectory() as path:
#             file_path = os.path.join(path, "foo")
#             initial_contents = "Hello"
#             contents = "Goodbye"
#
#             with open(file_path, "w", encoding="utf-8") as file:
#                 file.write(initial_contents)
#
#             output = FileStorageOutput(path)
#             event = WriteToFileOutputEvent(
#                 path=file_path, file_contents=contents, may_overwrite=False
#             )
#             assert not await output.output(event)
#
#             with open(file_path, encoding="utf-8") as file:
#                 assert file.read() == initial_contents
#
#     @pytest.mark.asyncio
#     async def test_output_create_file_append(self) -> None:
#         """
#         Create a file and then try to append to it.
#         :return:
#         """
#         with tempfile.TemporaryDirectory() as path:
#             file_path = os.path.join(path, "foo")
#             contents_1 = "Hello"
#             contents_2 = "Goodbye"
#
#             with open(file_path, "w", encoding="utf-8") as file:
#                 file.write(contents_1)
#
#             output = FileStorageOutput(path)
#             event = WriteToFileOutputEvent(
#                 path=file_path, file_contents=contents_2, append=True
#             )
#             assert await output.output(event)
#
#             assert os.path.exists(file_path)
#             with open(file_path, encoding="utf-8") as file:
#                 assert file.read() == contents_1 + contents_2
#
#     @pytest.mark.asyncio
#     async def test_output_create_dir(self) -> None:
#         """
#         Create a folder in the output directory.
#         :return:
#         """
#         with tempfile.TemporaryDirectory() as path:
#             file_path = os.path.join(path, "foo")
#
#             output = FileStorageOutput(path)
#             event = CreateDirectoryOutputEvent(path=file_path)
#             assert await output.output(event)
#
#             assert os.path.exists(file_path)
#             assert os.path.isdir(file_path)
#
#     @pytest.mark.asyncio
#     async def test_output_create_nested_dir(self) -> None:
#         """
#         Create a nested directory in the output folder.
#         :return:
#         """
#         with tempfile.TemporaryDirectory() as path:
#             file_path = os.path.join(path, "foo", "bar")
#
#             output = FileStorageOutput(path)
#             event = CreateDirectoryOutputEvent(path=file_path)
#             assert await output.output(event)
#
#             assert os.path.exists(file_path)
#             assert os.path.isdir(file_path)
#
#     @pytest.mark.asyncio
#     async def test_output_create_existing_dir(self) -> None:
#         """
#         Attempt to create a folder in the output directory which already exists.
#         :return:
#         """
#         with tempfile.TemporaryDirectory() as path:
#             file_path = os.path.join(path, "foo")
#
#             os.mkdir(file_path)
#
#             output = FileStorageOutput(path)
#             event = CreateDirectoryOutputEvent(path=file_path)
#             assert await output.output(event)
#
#             assert os.path.exists(file_path)
#             assert os.path.isdir(file_path)
#
#     @pytest.mark.asyncio
#     async def test_output_unlink_file(self) -> None:
#         """
#         Attempt to unlink a folder in the output dir. This should fail.
#         :return:
#         """
#         with tempfile.TemporaryDirectory() as path:
#             file_path = os.path.join(path, "foo")
#
#             with open(file_path, "w", encoding="utf-8") as file:
#                 file.write("")
#
#             output = FileStorageOutput(path)
#             event = DeleteFileOutputEvent(path=file_path)
#             assert await output.output(event)
#
#             assert not os.path.exists(file_path)
#
#     @pytest.mark.asyncio
#     async def test_output_unlink_missing_file(self) -> None:
#         """
#         Attempts to unlink a file which does not exist.
#         :return:
#         """
#         with tempfile.TemporaryDirectory() as path:
#             file_path = os.path.join(path, "foo")
#
#             output = FileStorageOutput(path)
#             event = DeleteFileOutputEvent(path=file_path)
#             assert not await output.output(event)
#
#             assert not os.path.exists(file_path)

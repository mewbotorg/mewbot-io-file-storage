#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2021 - 2023 Mewbot Developers <mewbot@quicksilver.london>
#
# SPDX-License-Identifier: BSD-2-Clause

"""
Tests for 'file_storage' IO module, used for writing to the file system.
"""

from __future__ import annotations

import asyncio
import os.path
import sys
import tempfile

import aiofiles
import portalocker
import pytest

from mewbot.io.file_storage.portable_locking import (
    AsyncFileLock,
    PortaLockerAsyncFileLock,
)
from tests.base import FileStorageTestFixture


class TestAsyncFileLock(FileStorageTestFixture):
    """
    Tests for the AsyncFileLock that forms part of the file-storage.
    """

    async def test_basic_lock(self) -> None:
        """
        File Lock test case: open, lock, and write to a file.

        The file contents should be successfully written
        """

        with tempfile.TemporaryDirectory() as tmp_dir_path:
            file_path = os.path.join(tmp_dir_path, "test_lockable_file.txt")

            async with aiofiles.open(file_path, "w", encoding="utf-8") as test_handle:
                lock = AsyncFileLock(test_handle)

                async with lock:
                    await test_handle.write("hello")

            with open(file_path, "r", encoding="utf-8") as read_handle:
                assert read_handle.read() == "hello"

    async def test_portalocker_lock_unlock_async_context(self) -> None:
        """
        Tests using portalock to lock and unlock a file in an async context.

        :return:
        """

        with tempfile.TemporaryDirectory() as tmp_dir_path:
            file_path = os.path.join(tmp_dir_path, "target_file.txt")

            # First, ensure the file exists
            with open(file_path, "w", encoding="utf-8"):
                pass

            with open(file_path, "r", encoding="utf-8") as read_handle:
                portalocker.lock(read_handle, portalocker.LockFlags.EXCLUSIVE)
                portalocker.unlock(read_handle)

    async def test_portalocker_lock_acquisition(self) -> None:
        """
        File Lock test case: attempt to acquire a lock using portalocker.

        The lock should fail due to timeout.
        Need a version using portalocker for windows, and one using fcntl for linux.
        """

        with tempfile.TemporaryDirectory() as tmp_dir_path:
            file_path = os.path.join(tmp_dir_path, "target_file.txt")

            # First, ensure the file exists
            with open(file_path, "w", encoding="utf-8"):
                pass

            with open(file_path, "r", encoding="utf-8") as read_handle:
                portalocker.lock(read_handle, portalocker.LockFlags.EXCLUSIVE)

                async with aiofiles.open(file_path, "w") as test_handle:
                    lock = PortaLockerAsyncFileLock(test_handle, 0.5)
                    assert lock is not None

                portalocker.unlock(read_handle)

    async def test_portalocker_lock_timeout(self) -> None:
        """
        File Lock test case: attempt to lock a file that is already locked - portalocker backend.

        The lock should fail due to timeout.
        Need a version using portalocker for windows, and one using fcntl for linux.
        """

        with tempfile.TemporaryDirectory() as tmp_dir_path:
            file_path = os.path.join(tmp_dir_path, "target_file.txt")

            # First, ensure the file exists
            with open(file_path, "w", encoding="utf-8"):
                pass

            with open(file_path, "r", encoding="utf-8") as read_handle:
                portalocker.lock(read_handle, portalocker.LockFlags.EXCLUSIVE)

                async with aiofiles.open(file_path, "w") as test_handle:
                    lock = PortaLockerAsyncFileLock(test_handle, 0.5)
                    assert lock is not None

                    error = (
                        TimeoutError if sys.version_info.minor > 9 else asyncio.TimeoutError
                    )
                    with pytest.raises(error):
                        await lock.acquire()

                portalocker.unlock(read_handle)

    async def test_lock_before_timeout(self) -> None:
        """
        File Lock test case: attempt to lock a file that is already locked, but gets unlocked.

        The lock should not be acquired before the file is unlocked.
        """

        loop = asyncio.get_running_loop()

        with tempfile.TemporaryDirectory() as tmp_dir_path:
            file_path = os.path.join(tmp_dir_path, "test_file.bin")

            # First, ensure the file exists
            with open(file_path, "w", encoding="utf-8"):
                pass

            with open(file_path, "r", encoding="utf-8") as read_handle:
                portalocker.lock(read_handle, portalocker.LockFlags.EXCLUSIVE)

                async with aiofiles.open(file_path, "w") as test_handle:
                    lock = AsyncFileLock(test_handle, 0.6)
                    task = loop.create_task(lock.acquire())

                    await asyncio.sleep(0.2)
                    assert not task.done()

                    portalocker.unlock(read_handle)
                    await task

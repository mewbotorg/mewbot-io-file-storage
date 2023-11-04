# SPDX-FileCopyrightText: 2023 Mewbot Developers <mewbot@quicksilver.london>
#
# SPDX-License-Identifier: BSD-2-Clause

"""
The locking apis on Windows and linux are sufficiently different a compatibility layer is needed.
"""

from types import ModuleType
from typing import IO, TYPE_CHECKING, Any, Optional, Type

import asyncio
import functools

import portalocker
from aiofiles.threadpool.binary import AsyncBufferedIOBase as BytesIOBase
from aiofiles.threadpool.text import AsyncTextIOWrapper as TextIOBase

# Hideous hack to make mypy "happy"
if not TYPE_CHECKING:
    FCNTL_INSTALLED = None
    try:
        import fcntl as FCNTL_INSTALLED
    except ModuleNotFoundError:
        fcntl: Optional[ModuleType] = None
    fcntl = FCNTL_INSTALLED
else:
    fcntl: Optional[ModuleType] = None

FCNTL = globals()["fcntl"]


class FileHandlePortalocker(portalocker.Lock):
    """
    By default, portalocker opens a new file handle for use with a lock.

    We want to reuse an existing file handle - the one aiofiles is using.
    """

    _internal_fh: IO[bytes] | IO[str]

    def set_internal_fh(self, file_handle: IO[bytes] | IO[str]) -> None:
        """
        Set the internal file handle.

        :param file_handle:
        :return:
        """
        self._internal_fh = file_handle

    def _get_fh(self) -> IO[bytes] | IO[str]:
        """
        Return the internal file handle.

        :return:
        """
        return self._internal_fh

    def release(self) -> None:
        """
        Needed for mypy.

        :return:
        """
        # pylint: disable=W0246
        super().release()  # type: ignore[no-untyped-call]


class FcntlAsyncFileLock:
    """
    Asynchronous context-manager for locking a file descriptor with fcntl.

    This will acquire an exclusive lock using `fcntl.flock` in an executor
    thread, and wait up to the timeout to return.
    """

    _file: TextIOBase | BytesIOBase
    _timeout: float

    fcntl: Optional[ModuleType]

    def __init__(self, file: TextIOBase | BytesIOBase, timeout: float = 5) -> None:
        """
        Asynchronous context-manager for locking a file descriptor with fcntl.

        This will acquire an exclusive lock using fcntl.flock in an executor
        thread, and wait up to the timeout to return.
        """

        self._file = file
        self._timeout = timeout

        self.fcntl = FCNTL

    async def __aenter__(self) -> "FcntlAsyncFileLock":
        """Acquire the lock as part of an async context manager."""

        await self.acquire()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any | None,
    ) -> None:
        """Release the lock as part of an async context manager."""

        await self.release()

    async def acquire(self) -> None:
        """
        Acquire an exclusive a lock on the current file descriptor.
        """

        if self.fcntl is None:
            raise AssertionError("fcntl lock being used on non-fcntl system.")

        call = functools.partial(self.fcntl.flock, self._file.fileno(), self.fcntl.LOCK_EX)
        loop = asyncio.get_running_loop()
        future = loop.run_in_executor(None, call)

        await asyncio.wait_for(future, self._timeout)

    async def release(self) -> None:
        """
        Release any held locks on the file descriptor.
        """

        if self.fcntl is None:
            raise AssertionError("fcntl lock being used on non-fcntl system.")

        self.fcntl.flock(self._file.fileno(), self.fcntl.LOCK_UN)


class PortaLockerAsyncFileLock:
    """
    Asynchronous context-manager for locking a file descriptor with portalocker.

    This will acquire an exclusive lock using `fcntl.flock` in an executor
    thread, and wait up to the timeout to return.
    """

    _file: TextIOBase | BytesIOBase
    _timeout: float
    _lock: FileHandlePortalocker

    def __init__(self, file: TextIOBase | BytesIOBase, timeout: float = 5) -> None:
        """
        Asynchronous context-manager for locking a file descriptor with fcntl.

        This will acquire an exclusive lock using fcntl.flock in an executor
        thread, and wait up to the timeout to return.
        """

        self._file = file
        self._timeout = timeout

        self._lock = FileHandlePortalocker(filename="bypassed")
        self._lock.set_internal_fh(self._file._file)  # type: ignore[union-attr]

    async def __aenter__(self) -> "PortaLockerAsyncFileLock":
        """Acquire the lock as part of an async context manager."""

        await self.acquire()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any | None,
    ) -> None:
        """Release the lock as part of an async context manager."""

        await self.release()

    async def acquire(self) -> None:
        """
        Acquire an exclusive a lock on the current file descriptor.
        """
        # From the examples - portalocker.lock(file, portalocker.LockFlags.EXCLUSIVE)
        call = functools.partial(self._lock.acquire, portalocker.LOCK_EX)
        loop = asyncio.get_running_loop()
        future = loop.run_in_executor(None, call)

        # No clue why this is different between Windows and Linux
        try:
            await asyncio.wait_for(future, self._timeout)
        except asyncio.exceptions.TimeoutError as exp:
            raise TimeoutError from exp

    async def release(self) -> None:
        """
        Release any held locks on the file descriptor.
        """

        self._lock.release()


AsyncFileLock: Type[PortaLockerAsyncFileLock] | Type[FcntlAsyncFileLock]
if FCNTL is None:
    AsyncFileLock = PortaLockerAsyncFileLock
else:
    AsyncFileLock = FcntlAsyncFileLock

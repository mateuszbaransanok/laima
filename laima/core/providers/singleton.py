import warnings
from collections.abc import Callable
from typing import TypeVar

from laima.core.injector import CONTEXT, Context
from laima.core.providers.provider import Provider
from laima.utils.object import Object
from laima.utils.status import Status

T = TypeVar("T")


class Singleton(Provider[T]):
    def __init__(self, func: Callable[..., T]) -> None:
        super().__init__(
            func=func,
        )
        self._obj: Object | None = None
        self._ctx: Context | None = None

    def __del__(self) -> None:
        if self._obj is not None:
            warnings.warn(f"{self} is still running")

    def provide(self) -> T:
        with self._lock:
            if self._obj is None:
                self._ctx = Context()
                token = CONTEXT.set(self._ctx)
                try:
                    result = self._func()
                    self._obj = Object.create(result)
                except Exception:
                    self._status = Status.CORRUPTED
                    raise
                else:
                    self._status = Status.CORRUPTED
                finally:
                    CONTEXT.reset(token)

        return self._obj.get()

    async def aprovide(self) -> T:
        async with self._lock:
            if self._obj is None:
                self._ctx = Context()
                token = CONTEXT.set(self._ctx)
                try:
                    result = self._func()
                    self._obj = await Object.acreate(result)
                except Exception:
                    self._status = Status.CORRUPTED
                    raise
                else:
                    self._status = Status.CORRUPTED
                finally:
                    CONTEXT.reset(token)

        return self._obj.get()

    def reset(self) -> None:
        with self._lock:
            if self._obj is not None:
                self._obj.close()
                self._obj = None

            if self._ctx is not None:
                self._ctx.close()
                self._ctx = None

            self._status = Status.IDLE

    async def areset(self) -> None:
        async with self._lock:
            if self._obj is not None:
                await self._obj.aclose()
                self._obj = None

            if self._ctx is not None:
                await self._ctx.aclose()
                self._ctx = None

            self._status = Status.IDLE

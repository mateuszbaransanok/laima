from typing import TypeVar

from laima.core.injector import CONTEXT
from laima.core.providers.provider import Provider
from laima.exceptions import LaimaError
from laima.utils.object import Object, ScopedData
from laima.utils.status import Status

T = TypeVar("T")


class Scoped(Provider[T]):
    def provide(self) -> T:
        ctx = CONTEXT.get()

        if ctx is None:
            if self._is_generator:
                self._status = Status.CORRUPTED
                raise LaimaError("Scoped generator has to be called in context block")

            self._status = Status.RUNNING
            return self._func()

        with ctx.lock:
            if self in ctx:
                data = ctx[self]
            else:
                data = ScopedData()
                ctx[self] = data

        with data.lock:
            if data.obj is None:
                result = self._func()
                data.obj = Object.create(result)

        self._status = Status.RUNNING
        return data.obj.get()

    async def aprovide(self) -> T:
        ctx = CONTEXT.get()

        if ctx is None:
            if self._is_generator:
                self._status = Status.CORRUPTED
                raise LaimaError("Scoped generator has to be called in context block")

            self._status = Status.RUNNING
            return self._func()

        async with ctx.lock:
            if self in ctx:
                data = ctx[self]
            else:
                data = ScopedData()
                ctx[self] = data

        async with data.lock:
            if data.obj is None:
                result = self._func()
                data.obj = await Object.acreate(result)

        self._status = Status.RUNNING
        return data.obj.get()

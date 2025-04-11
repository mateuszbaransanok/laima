from collections.abc import Callable
from typing import TypeVar

from laima.core.injector import CONTEXT
from laima.core.providers.provider import Provider
from laima.exceptions import LaimaError
from laima.utils.object import Object, TransientData
from laima.utils.status import Status

T = TypeVar("T")
TCallable = TypeVar("TCallable", bound=Callable)


class Transient(Provider[T]):
    def provide(self) -> T:
        ctx = CONTEXT.get()

        if ctx is None:
            if self._is_generator:
                self._status = Status.CORRUPTED
                raise LaimaError("Transient generator has to be called in context block")

            self._status = Status.RUNNING
            return self._func()

        with ctx.lock:
            if self in ctx:
                data = ctx[self]
            else:
                data = TransientData()
                ctx[self] = data

        result = self._func()
        obj = Object.create(result)
        data.append(obj)

        self._status = Status.RUNNING
        return obj.get()

    async def aprovide(self) -> T:
        ctx = CONTEXT.get()

        if ctx is None:
            if self._is_generator:
                self._status = Status.CORRUPTED
                raise LaimaError("Transient generator has to be called in context block")

            self._status = Status.RUNNING
            return self._func()

        async with ctx.lock:
            if self in ctx:
                data = ctx[self]
            else:
                data = TransientData()
                ctx[self] = data

        result = self._func()
        obj = await Object.acreate(result)
        data.append(obj)

        self._status = Status.RUNNING
        return obj.get()

from collections.abc import AsyncIterator, Awaitable, Callable, Iterator
from typing import Any, TypeVar, overload

from laima.container import Container
from laima.context import CONTEXT
from laima.exc import LaimaError
from laima.providers.provider import Provider
from laima.utils.object import Object, ScopedData
from laima.utils.status import Status
from laima.utils.wrappers import provider_wrapper

T = TypeVar("T")
TypeT = TypeVar("TypeT", bound=type)


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
            self._status = Status.CORRUPTED
            raise LaimaError("Scoped provider has to be called in context block")

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


@overload
def scoped(func: TypeT) -> TypeT:  # type: ignore[overload-overlap]
    pass


@overload
def scoped(func: Callable[..., AsyncIterator[T]]) -> Scoped[Awaitable[T]]:
    pass


@overload
def scoped(func: Callable[..., Iterator[T]]) -> Scoped[T]:
    pass


@overload
def scoped(func: Callable[..., T]) -> Scoped[T]:
    pass


@overload
def scoped(
    *,
    bind_to: type | str | None = None,
    container: Container | None = None,
) -> Callable[[TypeT], TypeT]:
    pass


@overload
def scoped(  # type: ignore[overload-cannot-match]
    *,
    bind_to: type | str | None = None,
    container: Container | None = None,
) -> Callable[[Callable[..., AsyncIterator[T]]], Scoped[Awaitable[T]]]:
    pass


@overload
def scoped(  # type: ignore[overload-cannot-match]
    *,
    bind_to: type | str | None = None,
    container: Container | None = None,
) -> Callable[[Callable[..., Iterator[T]]], Scoped[T]]:
    pass


@overload
def scoped(  # type: ignore[overload-cannot-match]
    *,
    bind_to: type | str | None = None,
    container: Container | None = None,
) -> Callable[[Callable[..., T]], Scoped[T]]:
    pass


@overload
def scoped(  # type: ignore[overload-overlap]
    func: TypeT,
    *,
    bind_to: type | str | None = None,
    container: Container | None = None,
    override: bool = False,
) -> TypeT:
    pass


@overload
def scoped(
    func: Callable[..., AsyncIterator[T]],
    *,
    bind_to: type | str | None = None,
    container: Container | None = None,
    override: bool = False,
) -> Scoped[Awaitable[T]]:
    pass


@overload
def scoped(
    func: Callable[..., Iterator[T]],
    *,
    bind_to: type | str | None = None,
    container: Container | None = None,
    override: bool = False,
) -> Scoped[T]:
    pass


@overload
def scoped(
    func: Callable[..., T],
    *,
    bind_to: type | str | None = None,
    container: Container | None = None,
    override: bool = False,
) -> Scoped[T]:
    pass


def scoped(
    func: Any = None,
    *,
    bind_to: type | str | None = None,
    container: Container | None = None,
    override: bool = False,
) -> Any:
    return provider_wrapper(
        provider_cls=Scoped,
        func=func,
        bind_to=bind_to,
        container=container,
        override=override,
    )

from collections.abc import AsyncIterator, Awaitable, Callable, Iterator
from typing import Any, TypeVar, overload

from laima.container import Container
from laima.context import CONTEXT
from laima.exc import LaimaError
from laima.providers.provider import Provider
from laima.utils.object import Object, TransientData
from laima.utils.status import Status
from laima.utils.wrappers import provider_wrapper

T = TypeVar("T")
TCallable = TypeVar("TCallable", bound=Callable)
TypeT = TypeVar("TypeT", bound=type)


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


@overload
def transient(func: TypeT) -> TypeT:  # type: ignore[overload-overlap]
    pass


@overload
def transient(func: Callable[..., AsyncIterator[T]]) -> Transient[Awaitable[T]]:
    pass


@overload
def transient(func: Callable[..., Iterator[T]]) -> Transient[T]:
    pass


@overload
def transient(func: Callable[..., T]) -> Transient[T]:
    pass


@overload
def transient(
    *,
    bind_to: type | str | None = None,
    container: Container | None = None,
) -> Callable[[TypeT], TypeT]:
    pass


@overload
def transient(  # type: ignore[overload-cannot-match]
    *,
    bind_to: type | str | None = None,
    container: Container | None = None,
) -> Callable[[Callable[..., AsyncIterator[T]]], Transient[Awaitable[T]]]:
    pass


@overload
def transient(  # type: ignore[overload-cannot-match]
    *,
    bind_to: type | str | None = None,
    container: Container | None = None,
) -> Callable[[Callable[..., Iterator[T]]], Transient[T]]:
    pass


@overload
def transient(  # type: ignore[overload-cannot-match]
    *,
    bind_to: type | str | None = None,
    container: Container | None = None,
) -> Callable[[Callable[..., T]], Transient[T]]:
    pass


@overload
def transient(  # type: ignore[overload-overlap]
    func: TypeT,
    *,
    bind_to: type | str | None = None,
    container: Container | None = None,
    override: bool = False,
) -> TypeT:
    pass


@overload
def transient(
    func: Callable[..., AsyncIterator[T]],
    *,
    bind_to: type | str | None = None,
    container: Container | None = None,
    override: bool = False,
) -> Transient[Awaitable[T]]:
    pass


@overload
def transient(
    func: Callable[..., Iterator[T]],
    *,
    bind_to: type | str | None = None,
    container: Container | None = None,
    override: bool = False,
) -> Transient[T]:
    pass


@overload
def transient(
    func: Callable[..., T],
    *,
    bind_to: type | str | None = None,
    container: Container | None = None,
    override: bool = False,
) -> Transient[T]:
    pass


def transient(
    func: Any = None,
    *,
    bind_to: type | str | None = None,
    container: Container | None = None,
    override: bool = False,
) -> Any:
    return provider_wrapper(
        provider_cls=Transient,
        func=func,
        bind_to=bind_to,
        container=container,
        override=override,
    )

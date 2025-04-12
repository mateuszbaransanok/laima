import warnings
from collections.abc import AsyncIterator, Awaitable, Callable, Iterator
from typing import Any, TypeVar, overload

from laima.container import Container
from laima.context import CONTEXT
from laima.providers.provider import Provider
from laima.utils.context import Context
from laima.utils.object import Object
from laima.utils.status import Status
from laima.utils.wrappers import provider_wrapper

T = TypeVar("T")
TypeT = TypeVar("TypeT", bound=type)


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

@overload
def singleton(func: TypeT) -> TypeT:  # type: ignore[overload-overlap]
    pass


@overload
def singleton(func: Callable[..., AsyncIterator[T]]) -> Singleton[Awaitable[T]]:
    pass


@overload
def singleton(func: Callable[..., Iterator[T]]) -> Singleton[T]:
    pass


@overload
def singleton(func: Callable[..., T]) -> Singleton[T]:
    pass


@overload
def singleton(
    *,
    bind_to: type | str | None = None,
    container: Container | None = None,
) -> Callable[[TypeT], TypeT]:
    pass


@overload
def singleton(  # type: ignore[overload-cannot-match]
    *,
    bind_to: type | str | None = None,
    container: Container | None = None,
) -> Callable[[Callable[..., AsyncIterator[T]]], Singleton[Awaitable[T]]]:
    pass


@overload
def singleton(  # type: ignore[overload-cannot-match]
    *,
    bind_to: type | str | None = None,
    container: Container | None = None,
) -> Callable[[Callable[..., Iterator[T]]], Singleton[T]]:
    pass


@overload
def singleton(  # type: ignore[overload-cannot-match]
    *,
    bind_to: type | str | None = None,
    container: Container | None = None,
) -> Callable[[Callable[..., T]], Singleton[T]]:
    pass


@overload
def singleton(  # type: ignore[overload-overlap]
    func: TypeT,
    *,
    bind_to: type | str | None = None,
    container: Container | None = None,
    override: bool = False,
) -> TypeT:
    pass


@overload
def singleton(
    func: Callable[..., AsyncIterator[T]],
    *,
    bind_to: type | str | None = None,
    container: Container | None = None,
    override: bool = False,
) -> Singleton[Awaitable[T]]:
    pass


@overload
def singleton(
    func: Callable[..., Iterator[T]],
    *,
    bind_to: type | str | None = None,
    container: Container | None = None,
    override: bool = False,
) -> Singleton[T]:
    pass


@overload
def singleton(
    func: Callable[..., T],
    *,
    bind_to: type | str | None = None,
    container: Container | None = None,
    override: bool = False,
) -> Singleton[T]:
    pass


def singleton(
    func: Any = None,
    *,
    bind_to: type | str | None = None,
    container: Container | None = None,
    override: bool = False,
) -> Any:
    return provider_wrapper(
        provider_cls=Singleton,
        func=func,
        bind_to=bind_to,
        container=container,
        override=override,
    )

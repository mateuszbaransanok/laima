import asyncio
import functools
import inspect
from collections.abc import Awaitable, Callable
from contextvars import ContextVar, Token
from types import TracebackType
from typing import Any, Generic, ParamSpec, TypeVar, overload

from laima.utils.lock import Lock
from laima.utils.object import Data

P = ParamSpec("P")
T = TypeVar("T")
TData = TypeVar("TData", bound=Data)


class Context(Generic[TData]):
    def __init__(self) -> None:
        self._lock = Lock()
        self._data: dict[Callable, TData] = {}

    @property
    def lock(self) -> Lock:
        return self._lock

    def __setitem__(self, key: Callable, value: TData) -> None:
        self._data[key] = value

    def __getitem__(self, key: Callable) -> TData:
        return self._data[key]

    def __contains__(self, key: Callable) -> bool:
        return key in self._data

    def close(self) -> None:
        for val in self._data.values():
            val.close()

    async def aclose(self) -> None:
        await asyncio.gather(*(val.aclose() for val in self._data.values()))


CONTEXT: ContextVar[Context | None] = ContextVar("CONTEXT", default=None)


class ContextManager:
    def __init__(self, *, reuse_context: bool = True) -> None:
        self._reuse_context = reuse_context
        self._ctx: Context | None = None
        self._token: Token | None = None

    @overload
    def __call__(self, func: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T]]:
        pass

    @overload
    def __call__(self, func: Callable[P, T]) -> Callable[P, T]:
        pass

    def __call__(self, func: Any) -> Any:
        @functools.wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            with ContextManager(reuse_context=self._reuse_context):
                return func(*args, **kwargs)

        @functools.wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            async with ContextManager(reuse_context=self._reuse_context):
                return await func(*args, **kwargs)

        if inspect.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    def __enter__(self) -> None:
        if not (self._reuse_context and CONTEXT.get()):
            self._ctx = Context()
            self._token = CONTEXT.set(self._ctx)

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if self._ctx:
            self._ctx.close()
        if self._token:
            CONTEXT.reset(self._token)

    async def __aenter__(self) -> None:
        if not (self._reuse_context and CONTEXT.get()):
            self._ctx = Context()
            self._token = CONTEXT.set(self._ctx)

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if self._ctx:
            await self._ctx.aclose()
        if self._token:
            CONTEXT.reset(self._token)


@overload
def context(func: Callable[P, T]) -> Callable[P, T]:
    pass


@overload
def context(*, reuse_context: bool = True) -> ContextManager:
    pass


def context(
    func: Any = None,
    *,
    reuse_context: bool = True,
) -> Any:
    context_manager = ContextManager(
        reuse_context=reuse_context,
    )

    if func is None:
        return context_manager
    return context_manager(func)

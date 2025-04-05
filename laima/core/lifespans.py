import asyncio
import functools
import inspect
from collections.abc import AsyncIterator, Callable, Iterator
from typing import Any, ParamSpec, TypeVar, overload

from laima.core.context import CONTEXT, Context
from laima.core.register import REGISTER
from laima.exceptions import LaimaError
from laima.utils.lock import Lock
from laima.utils.object import Object, ScopedData, TransientData

P = ParamSpec("P")
T = TypeVar("T")


@overload
def singleton(func: Callable[P, AsyncIterator[T] | Iterator[T] | T]) -> Callable[P, T]:
    pass


@overload
def singleton(
    *,
    tags: list[str] | tuple[str, ...] | set[str],
) -> Callable[[Callable[P, AsyncIterator[T] | Iterator[T] | T]], Callable[P, T]]:
    pass


def singleton(func: Any = None, *, tags: Any = None) -> Any:
    def wrapper(f: Callable) -> Any:
        obj: Object | None = None
        ctx: Context | None = None
        lock = Lock()

        @functools.wraps(f)
        def sync_fun(*args: Any, **kwargs: Any) -> Any:
            nonlocal obj, lock, ctx

            with lock:
                if obj is None:
                    ctx = Context()
                    token = CONTEXT.set(ctx)
                    try:
                        result = f(*args, **kwargs)
                        obj = Object.create(result)
                    finally:
                        CONTEXT.reset(token)

            return obj.get()

        @functools.wraps(f)
        async def async_fun(*args: Any, **kwargs: Any) -> Any:
            nonlocal obj, lock, ctx

            async with lock:
                if obj is None:
                    ctx = Context()
                    token = CONTEXT.set(ctx)
                    try:
                        result = await f(*args, **kwargs)
                        obj = await Object.acreate(result)
                    finally:
                        CONTEXT.reset(token)

            return obj.get()

        def sync_reset() -> None:
            nonlocal obj, ctx

            with lock:
                if obj is not None:
                    obj.close()
                    obj = None

                if ctx is not None:
                    ctx.close()
                    ctx = None

        async def async_reset() -> None:
            nonlocal obj, ctx

            async with lock:
                if obj is not None:
                    await obj.aclose()
                    obj = None

                if ctx is not None:
                    await ctx.aclose()
                    ctx = None

        if asyncio.iscoroutinefunction(f):
            async_fun.__laima_lifespan__ = singleton  # type: ignore[attr-defined]
            async_fun.__laima_tags__ = set(tags) if tags else set()  # type: ignore[attr-defined]
            async_fun.__laima_reset__ = async_reset  # type: ignore[attr-defined]
            REGISTER.add(async_fun)
            return async_fun
        sync_fun.__laima_lifespan__ = singleton  # type: ignore[attr-defined]
        sync_fun.__laima_tags__ = set(tags) if tags else set()  # type: ignore[attr-defined]
        sync_fun.__laima_reset__ = sync_reset  # type: ignore[attr-defined]
        REGISTER.add(sync_fun)
        return sync_fun

    if func is None:
        return wrapper
    return wrapper(func)


@overload
def scoped(func: Callable[P, AsyncIterator[T] | Iterator[T] | T]) -> Callable[P, T]:
    pass


@overload
def scoped(
    *,
    tags: list[str] | tuple[str, ...] | set[str],
) -> Callable[[Callable[P, AsyncIterator[T] | Iterator[T] | T]], Callable[P, T]]:
    pass


def scoped(func: Any = None, *, tags: Any = None) -> Any:
    def wrapper(f: Callable) -> Any:
        @functools.wraps(f)
        def sync_fun(*args: Any, **kwargs: Any) -> Any:
            ctx = CONTEXT.get()

            if ctx is None:
                raise LaimaError("Scoped generator has to be called in context block")

            with ctx.lock:
                if sync_fun in ctx:
                    data = ctx[sync_fun]
                else:
                    data = ScopedData()
                    ctx[sync_fun] = data

            with data.lock:
                if data.obj is None:
                    result = f(*args, **kwargs)
                    data.obj = Object.create(result)

            return data.obj.get()

        @functools.wraps(f)
        async def async_fun(*args: Any, **kwargs: Any) -> Any:
            ctx = CONTEXT.get()

            if ctx is None:
                raise LaimaError("Scoped async generator has to be called in context block")

            async with ctx.lock:
                if async_fun in ctx:
                    data = ctx[async_fun]
                else:
                    data = ScopedData()
                    ctx[async_fun] = data

            async with data.lock:
                if data.obj is None:
                    result = await f(*args, **kwargs)
                    data.obj = await Object.acreate(result)

            return data.obj.get()

        if asyncio.iscoroutinefunction(f):
            async_fun.__laima_lifespan__ = scoped  # type: ignore[attr-defined]
            async_fun.__laima_tags__ = set(tags) if tags else set()  # type: ignore[attr-defined]
            REGISTER.add(async_fun)
            return async_fun
        sync_fun.__laima_lifespan__ = scoped  # type: ignore[attr-defined]
        sync_fun.__laima_tags__ = set(tags) if tags else set()  # type: ignore[attr-defined]
        REGISTER.add(sync_fun)
        return sync_fun

    if func is None:
        return wrapper
    return wrapper(func)


@overload
def transient(func: Callable[P, AsyncIterator[T] | Iterator[T] | T]) -> Callable[P, T]:
    pass


@overload
def transient(
    *,
    tags: list[str] | tuple[str, ...] | set[str],
) -> Callable[[Callable[P, AsyncIterator[T] | Iterator[T] | T]], Callable[P, T]]:
    pass


def transient(func: Any = None, *, tags: Any = None) -> Any:
    def wrapper(f: Callable) -> Any:
        @functools.wraps(f)
        def sync_fun(*args: Any, **kwargs: Any) -> Any:
            ctx = CONTEXT.get()

            if ctx is None:
                if inspect.isgeneratorfunction(f):
                    raise LaimaError("Transient generator has to be called in context block")
                return f(*args, **kwargs)
            with ctx.lock:
                if sync_fun in ctx:
                    data = ctx[sync_fun]
                else:
                    data = TransientData()
                    ctx[sync_fun] = data

            result = f(*args, **kwargs)
            obj = Object.create(result)
            data.append(obj)

            return obj.get()

        @functools.wraps(f)
        async def async_fun(*args: Any, **kwargs: Any) -> Any:
            ctx = CONTEXT.get()

            if ctx is None:
                if inspect.isasyncgenfunction(f):
                    raise LaimaError("Transient async generator has to be called in context block")
                return await f(*args, **kwargs)
            async with ctx.lock:
                if async_fun not in ctx:
                    ctx[async_fun] = TransientData()

            result = await f(*args, **kwargs)
            obj = await Object.acreate(result)
            ctx[async_fun].append(obj)

            return obj.get()

        if asyncio.iscoroutinefunction(f):
            async_fun.__laima_lifespan__ = transient  # type: ignore[attr-defined]
            async_fun.__laima_tags__ = set(tags) if tags else set()  # type: ignore[attr-defined]
            REGISTER.add(async_fun)
            return async_fun
        sync_fun.__laima_lifespan__ = transient  # type: ignore[attr-defined]
        sync_fun.__laima_tags__ = set(tags) if tags else set()  # type: ignore[attr-defined]
        REGISTER.add(sync_fun)
        return sync_fun

    if func is None:
        return wrapper
    return wrapper(func)

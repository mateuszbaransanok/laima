from collections.abc import AsyncIterator, Awaitable, Callable, Iterator
from typing import Any, ParamSpec, TypeVar, cast, overload

from laima.core.container import LAIMA_MAIN_CONTAINER, Container
from laima.core.injector import Injector
from laima.core.providers.provider import Provider
from laima.core.providers.scoped import Scoped
from laima.core.providers.singleton import Singleton
from laima.core.providers.transient import Transient
from laima.exceptions import LaimaError

T = TypeVar("T")
P = ParamSpec("P")


# SCOPED -------------------------------------------------------------------------------------------
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


# SINGLETON ----------------------------------------------------------------------------------------
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


# TRANSIENT ----------------------------------------------------------------------------------------
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


# IMPLEMENTATION -----------------------------------------------------------------------------------
def provider_wrapper(
    *,
    provider_cls: type[Provider],
    func: Any = None,
    bind_to: type | str | None = None,
    container: Container | None = None,
    override: bool = False,
) -> Any:
    container = container or LAIMA_MAIN_CONTAINER

    def wrapper(f: Callable) -> Any:
        if isinstance(f, Provider):
            raise LaimaError("Wrapping other providers is not allowed")

        is_class = isinstance(f, type)

        if is_class:
            if f.__init__ is not object.__init__:  # type: ignore[misc]
                f.__init__ = inject(f.__init__)  # type: ignore[misc]
        else:
            f = inject(f)

        provider = provider_cls(f)

        if is_class:
            container.bind(provider, to=bind_to or cast("type", f), override=override)
            return f

        if bind_to:
            container.bind(provider, to=bind_to, override=override)

        return provider

    if func is None:
        return wrapper
    return wrapper(func)


# INJECT -------------------------------------------------------------------------------------------
@overload
def inject(func: Callable[P, T]) -> Callable[..., T]:
    pass


@overload
def inject(*, container: Container | None = None, reuse_context: bool = True) -> Injector:
    pass


def inject(
    func: Any = None,
    *,
    container: Container | None = None,
    reuse_context: bool = True,
) -> Any:
    context_manager = Injector(
        reuse_context=reuse_context,
        container=container or LAIMA_MAIN_CONTAINER,
    )

    if func is None:
        return context_manager
    return context_manager(func)

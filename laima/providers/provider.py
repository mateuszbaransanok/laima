import inspect
import secrets
from abc import ABC, abstractmethod
from collections.abc import Callable
from functools import partial
from typing import Any, Generic, Self, TypeVar

from laima.exc import LaimaTypeError
from laima.utils.lock import Lock
from laima.utils.status import Status

T = TypeVar("T")


class Provider(Generic[T], ABC):
    def __init__(self, func: Callable[..., T]) -> None:
        self._func = func
        self._is_generator = (
            inspect.isgeneratorfunction(func)
            or inspect.isasyncgenfunction(func)
        )
        self._is_async = (
            inspect.iscoroutinefunction(func)
            or inspect.isasyncgenfunction(func)
        )
        self._attr_name: str | None = None
        self._lock = Lock()
        self._status = Status.IDLE
        self._id = secrets.token_hex(4)

    @property
    def status(self) -> Status:
        return self._status

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}[{self._id}]({self._func})"

    def __set_name__(self, owner: type, name: str) -> None:
        if self._attr_name is None:
            self._attr_name = name
        elif name != self._attr_name:
            raise LaimaTypeError(
                "Cannot assign the same cached_property to two different names "
                f"({self._attr_name!r} and {name!r}).",
            )

    def __get__(self, instance: Any, owner: type) -> Self:
        if instance is None:
            return self

        if self._attr_name is None:
            raise LaimaTypeError("Cannot use provider without calling __set_name__ on it.")

        try:
            cache = instance.__dict__
        except AttributeError:
            msg = (
                f"No '__dict__' attribute on {type(instance).__name__!r} "
                f"instance to cache {self._attr_name!r} property."
            )
            raise LaimaTypeError(msg) from None

        with self._lock:
            if self._attr_name not in cache:
                func = partial(self._func, instance)
                func.__qualname__ = self._func.__qualname__  # type: ignore[attr-defined]
                provider = self.__class__(func)
                try:
                    cache[self._attr_name] = provider
                except TypeError:
                    msg = (
                        f"The '__dict__' attribute on {type(instance).__name__!r} instance "
                        f"does not support item assignment for caching {self._attr_name!r} provider."
                    )
                    raise LaimaTypeError(msg) from None
            else:
                provider = cache[self._attr_name]

        return provider

    def __call__(self) -> T:
        if self._is_async:
            coroutine = self.aprovide()
            coroutine.__qualname__ = self._func.__qualname__
            return coroutine  # type: ignore[return-value]

        return self.provide()

    @abstractmethod
    def provide(self) -> T:
        pass

    @abstractmethod
    async def aprovide(self) -> T:
        pass

    def reset(self) -> None:
        self._status = Status.IDLE

    async def areset(self) -> None:
        self._status = Status.IDLE

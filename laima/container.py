import asyncio
from typing import Any, TypeVar, overload

from laima.exc import LaimaError
from laima.providers.provider import Provider
from laima.utils.lock import Lock

T = TypeVar("T")


class Container:
    def __init__(self) -> None:
        self._lock = Lock()
        self._registry: dict[type | str, Provider] = {}

    def __str__(self) -> str:
        return f"{self.__class__.__qualname__}({self._registry})"

    @property
    def registry(self) -> dict[type | str, Provider]:
        return self._registry.copy()

    @overload
    def get(self, obj: type | str) -> Provider:
        pass

    @overload
    def get(self, obj: type | str, *, default: T) -> Provider | T:
        pass

    def get(self, obj: type | str, *, default: Any = ...) -> Any:
        try:
            return self._registry[obj]
        except KeyError:
            if default is not ...:
                return default
            raise LaimaError(f"There is nothing bound with {obj}")

    def bind(
        self,
        obj: Provider | type | str,
        *,
        to: type | str,
        override: bool = False,
    ) -> None:
        with self._lock:
            if not override and to in self._registry:
                raise LaimaError(f"Cannot bind to '{to}' because it already bound")

            if isinstance(obj, Provider):
                self._registry[to] = obj
            else:
                self._registry[to] = self.get(obj)

    def unbind(self, obj: type | str) -> None:
        with self._lock:
            self._registry.pop(obj, None)

    def unbind_all(self) -> None:
        with self._lock:
            self._registry.clear()

    def reset(self) -> None:
        with self._lock:
            for provider in self._registry.values():
                provider.reset()

    async def areset(self) -> None:
        async with self._lock:
            await asyncio.gather(*(provider.areset() for provider in self._registry.values()))


LAIMA_MAIN_CONTAINER = Container()

get = LAIMA_MAIN_CONTAINER.get
bind = LAIMA_MAIN_CONTAINER.bind
unbind = LAIMA_MAIN_CONTAINER.unbind
unbind_all = LAIMA_MAIN_CONTAINER.unbind_all
reset_container = LAIMA_MAIN_CONTAINER.reset
areset_container = LAIMA_MAIN_CONTAINER.areset

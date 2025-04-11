import asyncio
from typing import Generic, TypeVar

from laima.core.providers.provider import Provider
from laima.utils.lock import Lock
from laima.utils.object import Data

TData = TypeVar("TData", bound=Data)


class Context(Generic[TData]):
    def __init__(self) -> None:
        self._lock = Lock()
        self._data: dict[Provider, TData] = {}

    @property
    def lock(self) -> Lock:
        return self._lock

    def __setitem__(self, provider: Provider, value: TData) -> None:
        self._data[provider] = value

    def __getitem__(self, provider: Provider) -> TData:
        return self._data[provider]

    def __contains__(self, provider: Provider) -> bool:
        return provider in self._data

    def close(self) -> None:
        for val in self._data.values():
            val.close()

    async def aclose(self) -> None:
        await asyncio.gather(*(val.aclose() for val in self._data.values()))


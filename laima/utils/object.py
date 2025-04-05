import asyncio
import warnings
from abc import ABC, abstractmethod
from collections.abc import AsyncIterator, Iterator
from dataclasses import dataclass, field
from typing import Generic, TypeVar

from laima.exceptions import LaimaAsyncError, LaimaError
from laima.utils.empty import EMPTY, Empty
from laima.utils.lock import Lock

T = TypeVar("T")


class Data(Generic[T], ABC):
    @abstractmethod
    def close(self) -> None:
        pass

    @abstractmethod
    async def aclose(self) -> None:
        pass


@dataclass
class Object(Data[T]):
    obj: AsyncIterator[T] | Iterator[T] | T
    instance: T | Empty = EMPTY

    @classmethod
    def create(cls, obj: AsyncIterator[T] | Iterator[T] | T) -> "Object":
        match obj:
            case AsyncIterator():
                raise LaimaAsyncError("Object have to be created asynchronously; use `acreate()`")
            case Iterator():
                instance = next(obj)
            case _:
                instance = obj

        return cls(
            obj=obj,
            instance=instance,
        )

    @classmethod
    async def acreate(cls, obj: AsyncIterator[T] | Iterator[T] | T) -> "Object":
        match obj:
            case AsyncIterator():
                instance = await anext(obj)
            case Iterator():
                instance = next(obj)
            case _:
                instance = obj

        return cls(
            obj=obj,
            instance=instance,
        )

    def get(self) -> T:
        if isinstance(self.instance, Empty):
            raise LaimaError("Object has been already closed")
        return self.instance

    def close(self) -> None:
        match self.obj:
            case AsyncIterator():
                raise LaimaAsyncError("Object have to be closed asynchronously; use `aclose()`")
            case Iterator():
                try:
                    next(self.obj)
                except StopIteration:
                    pass
                except Exception as exc:
                    warnings.warn(f"Object closed with error: {exc}", stacklevel=2)
                finally:
                    self.instance = EMPTY

    async def aclose(self) -> None:
        match self.obj:
            case AsyncIterator():
                try:
                    await anext(self.obj)
                except StopAsyncIteration:
                    pass
                except Exception as exc:
                    warnings.warn(f"Object closed with error: {exc}", stacklevel=2)
                finally:
                    self.instance = EMPTY
            case Iterator():
                try:
                    next(self.obj)
                except StopIteration:
                    pass
                except Exception as exc:
                    warnings.warn(f"Object closed with error: {exc}", stacklevel=2)
                finally:
                    self.instance = EMPTY


@dataclass()
class TransientData(Data[T]):
    objects: list[Object[T]] = field(default_factory=list)

    def append(self, data: Object[T]) -> None:
        self.objects.append(data)

    def close(self) -> None:
        for val in self.objects:
            val.close()

    async def aclose(self) -> None:
        await asyncio.gather(*(val.aclose() for val in self.objects))


@dataclass
class ScopedData(Data[T]):
    lock: Lock = field(default_factory=Lock)
    obj: Object[T] | None = None

    def close(self) -> None:
        if self.obj is not None:
            self.close()

    async def aclose(self) -> None:
        if self.obj is not None:
            await self.aclose()

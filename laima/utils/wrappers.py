from collections.abc import Callable
from typing import Any, cast

from laima.container import LAIMA_MAIN_CONTAINER, Container
from laima.context import inject
from laima.exc import LaimaError
from laima.providers.provider import Provider


class ClassWrapper:
    def __init__(self, cls: type[object]) -> None:
        self.cls = cls
        self.origin_new = cls.__new__
        self.origin_init = cls.__init__

    def __call__(self) -> Any:
        instance = self.origin_new(self.cls)
        if self.origin_init is not object.__init__:
            inject(self.origin_init)(instance)
        return instance


class ClassInitWrapper:
    def __init__(self, cls: type) -> None:
        self.cls = cls
        self.origin_init = cls.__init__  # type: ignore[misc]
        self.__call__ = self.origin_init

    def __get__(self, instance: Any, owner: type | None = None) -> Callable[..., None]:
        if instance is None:
            raise LaimaError("Init requires an instance")

        def init(*args: Any, **kwargs: Any) -> None:
            if type(instance) is not self.cls:
                self.origin_init(instance, *args, **kwargs)

        return init


class ClassNewWrapper:
    def __init__(self, cls: type, provider: Provider) -> None:
        self.cls = cls
        self.origin_new = cls.__new__
        self.provider = provider

    def __call__(self, cls: type[object], *args: Any, **kwargs: Any) -> Any:
        if self.cls is cls:
            if args or kwargs:
                raise LaimaError(f"Provider '{cls.__qualname__}' takes no external parameters")
            instance = self.provider()
        elif self.origin_new is object.__new__:
            instance = object.__new__(cls)
        else:
            instance = self.origin_new(cls, *args, **kwargs)

        return instance


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

        if isinstance(f, type):
            cls = cast("type[object]", f)
            class_wrapper = ClassWrapper(cls)
            provider = provider_cls(class_wrapper)
            cls.__new__ = ClassNewWrapper(cls, provider)  # type: ignore[method-assign]
            cls.__init__ = ClassInitWrapper(cls)  # type: ignore[method-assign]
            container.bind(provider, to=bind_to or cls, override=override)
            return cls

        f = inject(f)
        provider = provider_cls(f)

        container.bind(provider, to=bind_to or f"{f.__module__}:{f.__qualname__}", override=override)

        return provider

    if func is None:
        return wrapper
    return wrapper(func)

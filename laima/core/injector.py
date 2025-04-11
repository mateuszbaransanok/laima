import asyncio
import functools
import inspect
from collections.abc import Awaitable, Callable
from contextvars import ContextVar, Token
from types import TracebackType
from typing import Annotated, Any, ParamSpec, TypeVar, get_args, get_origin, overload

from laima.core.container import Container
from laima.core.providers.provider import Provider
from laima.exceptions import LaimaError, LaimaTypeError
from laima.utils.context import Context

T = TypeVar("T")
P = ParamSpec("P")

CONTEXT: ContextVar[Context | None] = ContextVar("CONTEXT", default=None)


class Injector:
    def __init__(self, container: Container, *, reuse_context: bool = True) -> None:
        self._container = container
        self._reuse_context = reuse_context
        self._ctx: Context | None = None
        self._token: Token | None = None

    @overload
    def __call__(self, func: Callable[P, Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        pass

    @overload
    def __call__(self, func: Callable[P, T]) -> Callable[..., T]:
        pass

    def __call__(self, func: Any) -> Any:
        if getattr(func, "__laima_inject__", False):
            raise LaimaError("Overlapped decorator `@laima.inject`")
        if isinstance(func, Provider):
            raise LaimaError("Decorator `@laima.inject` cannot be used on Provider")

        signature = inspect.signature(func)

        def prepare_arguments(
            *args: Any,
            **kwargs: Any,
        ) -> tuple[inspect.BoundArguments, dict[str, Provider]]:
            bound_params = signature.bind_partial(*args, **kwargs)

            providers = {}
            for param in signature.parameters.values():
                if param.name in bound_params.arguments or param.default is not param.empty:
                    continue
                if provider := self._container.get(param.annotation, default=None):
                    providers[param.name] = provider
                elif get_origin(param.annotation) is Annotated:
                    annot_args = get_args(param.annotation)
                    if len(annot_args) == 2:
                        _, annot_meta = annot_args
                        if (
                            (callable(annot_meta) or isinstance(annot_meta, (str, Provider)))
                            and (provider := self._container.get(annot_meta, default=None))
                        ):
                            providers[param.name] = provider

                if param.name not in providers:
                    raise LaimaTypeError(
                        f"{func.__qualname__} missing a required argument: '{param.name}'")

            return bound_params, providers

        @functools.wraps(func)
        def sync_function(*args: Any, **kwargs: Any) -> Any:
            bound_params, providers = prepare_arguments(*args, **kwargs)

            with Injector(container=self._container, reuse_context=self._reuse_context):
                for name, provider in providers.items():
                    bound_params.arguments[name] = provider.provide()

                signature.bind(*bound_params.args, **bound_params.kwargs)
                return func(*bound_params.args, **bound_params.kwargs)

        @functools.wraps(func)
        async def async_function(*args: Any, **kwargs: Any) -> Any:
            bound_params, providers = prepare_arguments(*args, **kwargs)

            async with Injector(container=self._container, reuse_context=self._reuse_context):
                values = await asyncio.gather(*(provider.aprovide() for provider in providers.values()))
                for name, value in zip(providers, values, strict=True):
                    bound_params.arguments[name] = value

                signature.bind(*bound_params.args, **bound_params.kwargs)
                return await func(*bound_params.args, **bound_params.kwargs)

        @functools.wraps(func)
        def sync_generator(*args: Any, **kwargs: Any) -> Any:
            bound_params, providers = prepare_arguments(*args, **kwargs)

            with Injector(container=self._container, reuse_context=self._reuse_context):
                for name, provider in providers.items():
                    bound_params.arguments[name] = provider.provide()

                signature.bind(*bound_params.args, **bound_params.kwargs)
                yield from func(*bound_params.args, **bound_params.kwargs)

        @functools.wraps(func)
        async def async_generator(*args: Any, **kwargs: Any) -> Any:
            bound_params, providers = prepare_arguments(*args, **kwargs)

            async with Injector(container=self._container, reuse_context=self._reuse_context):
                values = await asyncio.gather(*(provider.aprovide() for provider in providers.values()))
                for name, value in zip(providers, values, strict=True):
                    bound_params.arguments[name] = value

                signature.bind(*bound_params.args, **bound_params.kwargs)
                async for result in func(*bound_params.args, **bound_params.kwargs):
                    yield result

        if inspect.iscoroutinefunction(func):
            async_function.__laima_inject__ = True  # type: ignore[attr-defined]
            return async_function

        if inspect.isasyncgenfunction(func):
            async_generator.__laima_inject__ = True  # type: ignore[attr-defined]
            return async_generator

        if inspect.isgeneratorfunction(func):
            sync_generator.__laima_inject__ = True  # type: ignore[attr-defined]
            return sync_generator

        sync_function.__laima_inject__ = True  # type: ignore[attr-defined]
        return sync_function

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

from collections.abc import Callable, Iterator
from importlib import import_module

REGISTER: set[Callable] = set()


def discover(*modules: str) -> None:
    for module in modules:
        import_module(module)


def registered() -> Iterator[Callable]:
    yield from REGISTER

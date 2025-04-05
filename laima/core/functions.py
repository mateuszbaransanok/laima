from collections.abc import Callable

from laima.exceptions import LaimaError


def get_tags(f: Callable) -> set[str]:
    if hasattr(f, "__laima_tags__"):
        return f.__laima_tags__
    raise LaimaError("Function is not wrapped by lifespan")


def get_lifespan(f: Callable) -> Callable:
    if hasattr(f, "__laima_lifespan__"):
        return f.__laima_lifespan__
    raise LaimaError("Function is not wrapped by lifespan")


def reset_singleton(f: Callable) -> None:
    if hasattr(f, "__laima_reset__"):
        f.__laima_reset__()
    else:
        raise LaimaError("Function is not wrapped by singleton")

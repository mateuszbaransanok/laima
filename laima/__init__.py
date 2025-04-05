from laima.core.context import context
from laima.core.functions import get_lifespan, get_tags, reset_singleton
from laima.core.lifespans import scoped, singleton, transient
from laima.core.register import discover, registered

__version__ = "0.1.0"

__all__ = [
    "__version__",
    "context",
    "core",
    "discover",
    "exceptions",
    "get_lifespan",
    "get_tags",
    "registered",
    "reset_singleton",
    "scoped",
    "singleton",
    "transient",
    "utils",
]

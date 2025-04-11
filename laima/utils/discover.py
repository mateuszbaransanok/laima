import importlib


def discover(*modules: str) -> None:
    for module in modules:
        importlib.import_module(module)

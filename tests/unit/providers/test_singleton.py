from unittest.mock import Mock

import laima


def test_singleton__same_instance_function() -> None:
    func = laima.singleton(lambda: Mock())

    assert isinstance(func, laima.Singleton)
    assert func() is func()


def test_singleton__same_instance_class() -> None:
    class MockClass:
        pass

    cls = laima.singleton(MockClass)

    assert cls is MockClass
    assert cls() is cls()


def test_singleton__same_instance_in_different_contexts() -> None:
    func = laima.singleton(lambda: Mock())

    with laima.inject():
        result = func()
        assert result is func()

    with laima.inject():
        assert result is func()
        assert func() is func()

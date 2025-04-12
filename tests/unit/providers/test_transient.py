from unittest.mock import Mock

import laima


def test_transient__same_instance_function() -> None:
    func = laima.transient(lambda: Mock())

    assert isinstance(func, laima.Transient)
    with laima.inject():
        assert func() is not func()


def test_transient__no_context_raise_error() -> None:
    class MockClass:
        pass

    cls = laima.transient(MockClass)

    assert cls is MockClass
    with laima.inject():
        assert cls() is not cls()


def test_transient__same_instance_in_different_contexts() -> None:
    func = laima.transient(lambda: Mock())

    with laima.inject():
        result = func()
        assert result is not func()

    with laima.inject():
        assert result is not func()
        assert func() is not func()

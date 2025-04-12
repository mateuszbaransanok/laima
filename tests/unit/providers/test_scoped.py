from unittest.mock import Mock

import laima


def test_scoped__same_instance_function() -> None:
    func = laima.scoped(lambda: Mock())

    assert isinstance(func, laima.Scoped)
    with laima.inject():
        assert func() is func()


def test_scoped__no_context_raise_error() -> None:
    class MockClass:
        pass

    cls = laima.scoped(MockClass)

    assert cls is MockClass
    with laima.inject():
        assert cls() is cls()


def test_scoped__same_instance_in_different_contexts() -> None:
    func = laima.scoped(lambda: Mock())

    with laima.inject():
        result = func()
        assert result is func()

    with laima.inject():
        assert result is not func()
        assert func() is func()

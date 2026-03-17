"""Result container for explicit error propagation across layer boundaries."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")
E = TypeVar("E", bound=Exception)


@dataclass
class Result(Generic[T]):
    """
    Lightweight result container.

    Usage::

        result = Result.ok_value(data)
        result = Result.err_value(SomeError("msg"))

        if result.is_ok:
            print(result.value)
        else:
            raise result.error
    """

    _value: T | None
    _error: Exception | None

    @classmethod
    def ok_value(cls, value: T) -> Result[T]:
        return cls(_value=value, _error=None)

    @classmethod
    def err_value(cls, error: Exception) -> Result[T]:
        return cls(_value=None, _error=error)

    @property
    def is_ok(self) -> bool:
        return self._error is None

    @property
    def is_err(self) -> bool:
        return self._error is not None

    @property
    def value(self) -> T:
        if self._error is not None:
            raise self._error
        return self._value  # type: ignore[return-value]

    @property
    def error(self) -> Exception | None:
        return self._error

    def unwrap(self) -> T:
        """Return value or raise the contained error."""
        if self._error is not None:
            raise self._error
        return self._value  # type: ignore[return-value]

    def unwrap_or(self, default: T) -> T:
        """Return value or a default if error."""
        if self._error is not None:
            return default
        return self._value  # type: ignore[return-value]

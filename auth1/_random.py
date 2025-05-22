import os
import binascii
import typing as t

try:
    randbytes = os.urandom
except AttributeError:
    from random import randbytes

def _default_random_string(length: int = 16) -> str:
    result = binascii.hexlify(randbytes(length)).decode()
    return result[:length]

_random_string_factory: t.Callable[[int], str] | None = None

def set_random_string_factory(factory: t.Callable[[int], str]) -> None:
    global _random_string_factory
    _random_string_factory = factory

def random_string(length: int = 16) -> str:
    assert _random_string_factory is not None
    return _random_string_factory(length)

set_random_string_factory(_default_random_string)

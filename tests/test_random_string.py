import pytest

from auth1 import random_string

def test_random_string_default_length() -> None:
    s = random_string()
    assert 16 == len(s)

def test_random_string() -> None:
    s = random_string(19)
    assert 19 == len(s)

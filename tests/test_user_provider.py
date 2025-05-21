import pytest
import typing as t

from auth1 import Authenticatable, GenericUser

def test_user_provider()->None:
    pass


class SimpleUser(Authenticatable):
    identifier_name: str = "username"
    password_name: str = "password"
    remember_token_name: str | None = None

    def __init__(self, username: str, password: str, remember_token: str | None = None):
        self.identifier: str = username
        self.password: str = password
        self.remember_token: str | None = remember_token


def test_authenticatable() -> None:
    user = SimpleUser(username="harianja", password="wsdfsrewe")

    assert isinstance(user, Authenticatable)
    assert isinstance(user, SimpleUser)

    assert user.remember_token_name is None
    assert user.remember_token is None

def test_generic_user() -> None:
    user = GenericUser({
        'userid': "harianja",
        'password': "Password123!",
        'email': "harianja@lundu.com"
    })

    assert isinstance(user, Authenticatable)
    assert isinstance(user, GenericUser)

    assert "userid" == user.identifier_name
    assert "harianja" == user.identifier
    assert "password" == user.password_name
    assert "Password123!" == user.password
    assert "remember_token" == user.remember_token_name
    assert "harianja@lundu.com" == user.email
    assert user.remember_token is None

    with pytest.raises(AttributeError) as exc_info:
        user.non_existence_attribute

    assert "GenericUser object has no attribute non_existence_attribute" == exc_info.value.args[0]

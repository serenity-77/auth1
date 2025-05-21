import typing as t
from ._types import Authenticatable


class GenericUser(Authenticatable):

    identifier_name: str = "userid"
    password_name: str = "password"
    remember_token_name: str = "remember_token"

    def __init__(self, attributes: t.Dict[str, t.Any]):
        self._attributes: t.Dict[str, t.Any] = attributes

    @property
    def identifier(self) -> str:
        return self._attributes[self.identifier_name]   # type: ignore

    @identifier.setter
    def identifier(self, value: str) -> None:
        ...

    @property
    def password(self) -> str:
        return t.cast(str, self._attributes[self.password_name])

    @password.setter
    def password(self, value: str) -> None:
        ...

    @property
    def remember_token(self) -> str | None:
        try:
            return self._attributes[self.remember_token_name]   # type: ignore
        except KeyError:
            return None

    @remember_token.setter
    def remember_token(self, value: str) -> None:
        self._attributes[self.remember_token_name] = value

    def __getattr__(self, name: str) -> t.Any:
        try:
            return self._attributes[name]
        except KeyError:
            raise AttributeError(f"{self.__class__.__name__} object has no attribute {name}")

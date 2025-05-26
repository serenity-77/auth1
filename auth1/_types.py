import abc
import typing as t

@t.runtime_checkable
class Authenticatable(t.Protocol):
    identifier_name: str
    identifier: str
    password_name: str
    password: str
    remember_token_name: str | None
    remember_token: str | None


AuthenticatableRetval = Authenticatable | None | t.Awaitable[Authenticatable | None]

class UserProvider(abc.ABC):

    @abc.abstractmethod
    def retrieve_by_id(self, id: str | int) -> AuthenticatableRetval:
        ...

    @abc.abstractmethod
    def retrieve_by_credentials(self, credentials: t.Dict[str, t.Any]) -> AuthenticatableRetval:
        ...

    @abc.abstractmethod
    def validate_credentials(self, user: Authenticatable, credentials: t.Dict[str, t.Any]) -> t.Awaitable[bool] | bool:
        ...


GuardCheckRetval = bool
GuardUserRetval = Authenticatable | None

class Guard(abc.ABC):

    @abc.abstractmethod
    def user(self) -> GuardUserRetval:
        ...

    @abc.abstractmethod
    async def async_user(self) -> Authenticatable | None:
        ...


class StatefullGuard(Guard):

    @abc.abstractmethod
    def attempt(self, credentials: t.Dict[str, t.Any], remember: bool = False) -> bool:
        ...

    @abc.abstractmethod
    async def async_attempt(self, credentials: t.Dict[str, t.Any], remember: bool = False) -> bool:
        ...

class AuthFactory(abc.ABC):

    @abc.abstractmethod
    def guard(self, name: str | None) -> Guard | None:
        pass


class SessionHandler(abc.ABC):

    @abc.abstractmethod
    def read(self, id: str) -> t.Awaitable[bytes] | bytes:
        ...

    @abc.abstractmethod
    def write(self, id: str, data: bytes) -> t.Awaitable[None] | None:
        ...

    @abc.abstractmethod
    def destroy(self, id: str) -> t.Awaitable[None] | None:
        ...


class SessionSerializer(abc.ABC):

    @abc.abstractmethod
    def encode(self, data: t.Dict[t.Any, t.Any]) -> bytes:
        ...

    @abc.abstractmethod
    def decode(self, data: bytes) -> t.Dict[t.Any, t.Any]:
        ...


@t.runtime_checkable
class Session(t.Protocol):
    id: str | None
    name: str

    def start(self) -> None:
        ...

    async def async_start(self) -> None:
        ...

    def save(self) -> None:
        ...

    async def async_save(self) -> None:
        ...

    def migrate(self, destroy: bool = False) -> bool:
        ...

    async def async_migrate(self, destroy: bool = False) -> bool:
        ...

    def __getitem__(self, key: t.Any) -> t.Any:
        ...

    def __setitem__(self, key: t.Any, data: t.Any) -> None:
        ...


class Request(t.Protocol):
    cookies: t.Dict[str, str]
    query: t.Dict[str, str]
    input: t.Dict[str, str]
    headers: t.Dict[str, str]
    session: Session

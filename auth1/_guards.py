import typing as t
import hashlib
import inspect

from ._types import (
    StatefullGuard,
    GuardCheckRetval,
    GuardUserRetval,
    UserProvider,
    Session,
    Authenticatable,
    AuthenticatableRetval
)

class SessionGuard(StatefullGuard):

    _user: Authenticatable | None = None
    _remember: bool = False

    def __init__(self, name: str, user_provider: UserProvider, session: Session) -> None:
        self._name = name
        self._user_provider = user_provider
        self._session = session

    @property
    def name(self) -> str:
        cls_hash = hashlib.sha1(self.__class__.__name__.encode()).hexdigest()
        return f"login_{self._name}_{cls_hash}"

    @property
    def remember(self) -> bool:
        return self._remember

    def user(self) -> GuardUserRetval:
        self._user = self._get_user() # type: ignore
        return self._user

    async def async_user(self) -> GuardUserRetval:
        result: AuthenticatableRetval = self._get_user(_async=True)

        if inspect.isawaitable(result):
            self._user = await result
        else:
            # testcase: test_session_guard_async_user_from_sync_provider
            self._user = result

        return self._user

    def attempt(self, credentials: t.Dict[str, t.Any], remember: bool = False) -> bool:
        user = self._user_provider.retrieve_by_credentials(credentials)

        if user is not None and isinstance(user, Authenticatable):
            validate_result = self._user_provider.validate_credentials(user, credentials)

            if validate_result:
                self._login(user, remember=remember)
                return True

        return False

    async def async_attempt(self, credentials: t.Dict[str, t.Any], remember: bool = False) -> bool:
        user = self._user_provider.retrieve_by_credentials(credentials)

        if inspect.isawaitable(user):
            user = await user

        if user is not None and isinstance(user, Authenticatable):
            validate_result = self._user_provider.validate_credentials(user, credentials)

            if inspect.isawaitable(validate_result):
                validate_result = await validate_result

            if validate_result:
                login_result: t.Awaitable[None] | None = self._login(user, remember=remember)
                if inspect.isawaitable(login_result):
                    await login_result
                return True

        return False

    def _login(self, user: Authenticatable, remember: bool = False, _async: bool = False) -> t.Awaitable[None] | None:
        self._user = user
        self._remember = remember
        if _async:
            return self._async_update_session(user.identifier)
        self._update_session(user.identifier)
        return None

    def _update_session(self, id: str) -> None:
        self._session[self.name] = id
        self._session.migrate(True)

    async def _async_update_session(self, id: str) -> None:
        self._session[self.name] = id
        await self._session.async_migrate(True)

    def _get_user(self, _async: bool = False) -> AuthenticatableRetval:
        if self._user is not None:
            return self._user

        try:
            id = self._session[self.name]
        except AttributeError:
            id = None

        if id is not None:
            coro_or_authenticatable: AuthenticatableRetval = self._user_provider.retrieve_by_id(id)

            if not _async and inspect.isawaitable(coro_or_authenticatable):
                # suppress coroutine was never awaited
                # https://stackoverflow.com/questions/62045387/how-to-suppress-coroutine-was-never-awaited-warning
                if hasattr(coro_or_authenticatable, "close"):
                    coro_or_authenticatable.close()
                    del coro_or_authenticatable
                raise ValueError("Cannot use awaitable return value from user provider")

            return coro_or_authenticatable

        return self._user

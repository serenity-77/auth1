import typing as t
import pytest
import pytest_asyncio
import hashlib

from auth1 import (
    SessionGuard,
    Guard,
    StatefullGuard,
    UserProvider,
    GenericUser,
    Session,
    SessionStore,
    AuthenticatableRetval,
    NullSessionHandler,
    Authenticatable
)

from ._helpers import NoopUserProvider1

class NoopUserProvider2(UserProvider):
    retrieve_by_id_called: int = 0

    def __init__(self, _async: bool = False) -> None:
        self._async = _async

    def retrieve_by_id(self, id: str | int) -> AuthenticatableRetval:
        self.retrieve_by_id_called += 1

        if not self._async:
            return GenericUser({
                'userid': "harianja",
                'password': "Harianja710433!",
                'email': "harianja@lundu.com"
            })

        return self._do_retrieve_by_id(id)

    async def _do_retrieve_by_id(self, id: str | int) -> Authenticatable | None:
        return GenericUser({
            'userid': "harianja",
            'password': "Harianja710433!",
            'email': "harianja@lundu.com"
        })

    def retrieve_by_credentials(self, credentials: t.Dict[str, t.Any]) -> AuthenticatableRetval:
        if not self._async:
            return GenericUser({
                'userid': "harianja",
                'password': "Harianja710433!",
                'email': "harianja@lundu.com"
            })

        return self._do_retrieve_by_credentials(credentials)

    async def _do_retrieve_by_credentials(self, credentials: t.Dict[str, t.Any]) -> Authenticatable | None:
        return GenericUser({
            'userid': "harianja",
            'password': "Harianja710433!",
            'email': "harianja@lundu.com"
        })

    def validate_credentials(self, user: Authenticatable, credentials: t.Dict[str, t.Any]) -> t.Awaitable[bool] | bool:
        if not self._async:
            return True
        return self._async_validate_credentials(user, credentials)

    async def _async_validate_credentials(self, user: Authenticatable, credentials: t.Dict[str, t.Any]) -> bool:
        return True


def test_session_guard_init() -> None:
    guard = SessionGuard(
        "horas",
        NoopUserProvider1(),
        SessionStore("auth1", NullSessionHandler())
    )

    assert isinstance(guard, Guard)
    assert isinstance(guard, SessionGuard)

    assert "horas" == guard._name

    assert isinstance(guard._user_provider, UserProvider)
    assert isinstance(guard._user_provider, NoopUserProvider1)

    assert isinstance(guard._session, Session)
    assert isinstance(guard._session, SessionStore)

def session_guard_name(session_guard: SessionGuard) -> str:
    cls_hash = hashlib.sha1(session_guard.__class__.__name__.encode()).hexdigest()
    return f"login_{session_guard._name}_{cls_hash}"

def test_session_guard_user_none() -> None:
    session_store: Session = SessionStore("auth1", NullSessionHandler())

    guard: SessionGuard = SessionGuard("horas", NoopUserProvider1(), session_store)

    user = guard.user()

    assert user is None

    session_store[session_guard_name(guard)] = "harianja"

    user = guard.user()

    assert user is None


def test_session_guard_user() -> None:
    session_store: Session = SessionStore("auth1", NullSessionHandler())
    user_provider: NoopUserProvider2 = NoopUserProvider2()

    guard: SessionGuard = SessionGuard("horas", user_provider, session_store)

    # Set the currently logged in user in the session
    session_store[session_guard_name(guard)] = "harianja"

    user = guard.user()

    assert isinstance(user, Authenticatable)
    assert isinstance(user, GenericUser)

    assert user.identifier == "harianja"
    assert user.password == "Harianja710433!"
    assert user.email == "harianja@lundu.com"

    user2 = guard.user()

    assert user2 is user

    assert 1 == user_provider.retrieve_by_id_called


def test_session_guard_user_awaitable_from_user_provider() -> None:
    session_store: Session = SessionStore("auth1", NullSessionHandler())

    guard: SessionGuard = SessionGuard(
        "horas",
        NoopUserProvider2(_async=True),
        session_store
    )

    # Set the currently logged in user in the session
    session_store[session_guard_name(guard)] = "harianja"

    with pytest.raises(ValueError) as exc_info:
        guard.user()

    assert "Cannot use awaitable return value from user provider" == exc_info.value.args[0]


async def _do_test_session_guard_async_user(user_provider: NoopUserProvider2) -> None:
    session_store: Session = SessionStore("auth1", NullSessionHandler())
    guard: SessionGuard = SessionGuard("horas", user_provider, session_store)

    # Set the currently logged in user in the session
    session_store[session_guard_name(guard)] = "harianja"

    user = await guard.async_user()

    assert isinstance(user, Authenticatable)
    assert isinstance(user, GenericUser)

    assert user.identifier == "harianja"
    assert user.password == "Harianja710433!"
    assert user.email == "harianja@lundu.com"

    user2 = await guard.async_user()

    assert user2 is user

    assert 1 == user_provider.retrieve_by_id_called

@pytest.mark.asyncio
async def test_session_guard_async_user() -> None:
    await _do_test_session_guard_async_user(NoopUserProvider2(_async=True))

@pytest.mark.asyncio
async def test_session_guard_async_user_from_sync_provider() -> None:
    await _do_test_session_guard_async_user(NoopUserProvider2(_async=False))

def _do_test_session_guard_attempt(remember: bool = False) -> None:
    def session_store_id() -> str:
        return "54321"

    session_handler: NullSessionHandler = NullSessionHandler()
    session_store: SessionStore = SessionStore("auth1", session_handler, id="12345")
    # session_store.generate_session_id = session_store_id
    setattr(session_store, "generate_session_id", session_store_id)

    user_provider = NoopUserProvider2()
    guard: SessionGuard = SessionGuard("horas", user_provider, session_store)

    credentials: t.Dict[str, t.Any] = {
        'username': "harianja",
        'password': "Harianjalundu710433!"
    }

    assert "12345" == session_store.id

    attempt_result: bool = guard.attempt(credentials, remember=remember)

    assert True == attempt_result

    guard_name = session_guard_name(guard)

    assert "harianja" == session_store[guard_name]
    assert "54321" == session_store.id

    if remember:
        assert True == guard.remember

    user = guard.user()

    assert user is not None
    assert isinstance(user, Authenticatable)
    assert isinstance(user, GenericUser)

    # attempt method use retrieve_by_credentials
    assert 0 == user_provider.retrieve_by_id_called

    assert user.identifier == "harianja"
    assert user.password == "Harianja710433!"
    assert user.email == "harianja@lundu.com"

    assert True == session_handler.destroyed

    user2 = guard.user()

    assert user2 is user

    assert 0 == user_provider.retrieve_by_id_called

def test_session_guard_attempt() -> None:
    _do_test_session_guard_attempt()

def test_session_guard_attempt_remember() -> None:
    _do_test_session_guard_attempt(remember=True)

async def _do_test_session_guard_async_attempt(remember: bool = False) -> None:
    def session_store_id() -> str:
        return "54321"

    session_handler: NullSessionHandler = NullSessionHandler()
    session_store: SessionStore = SessionStore("auth1", session_handler, id="12345")
    # session_store.generate_session_id = session_store_id
    setattr(session_store, "generate_session_id", session_store_id)

    user_provider = NoopUserProvider2(_async=True)
    guard: SessionGuard = SessionGuard("horas", user_provider, session_store)

    credentials: t.Dict[str, t.Any] = {
        'username': "harianja",
        'password': "Harianjalundu710433!"
    }

    assert "12345" == session_store.id

    attempt_result: bool = await guard.async_attempt(credentials, remember=remember)

    assert True == attempt_result

    guard_name = session_guard_name(guard)

    assert "harianja" == session_store[guard_name]
    assert "54321" == session_store.id

    if remember:
        assert True == guard.remember

    user = await guard.async_user()

    assert user is not None
    assert isinstance(user, Authenticatable)
    assert isinstance(user, GenericUser)

    # attempt method use retrieve_by_credentials
    assert 0 == user_provider.retrieve_by_id_called

    assert user.identifier == "harianja"
    assert user.password == "Harianja710433!"
    assert user.email == "harianja@lundu.com"

    assert True == session_handler.destroyed

    user2 = await guard.async_user()

    assert user2 is user

    assert 0 == user_provider.retrieve_by_id_called

@pytest.mark.asyncio
async def test_session_guard_async_attempt() -> None:
    await _do_test_session_guard_async_attempt()

@pytest.mark.asyncio
async def test_session_guard_async_attempt_remember() -> None:
    await _do_test_session_guard_async_attempt(remember=True)

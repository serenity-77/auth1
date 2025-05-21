import copy
import pytest

from auth1 import (
    AuthManager,
    AuthConfig,
    Guard,
    StatefullGuard,
    SessionGuard,
    SessionStore,
    NullSessionHandler,
    GuardCheckRetval,
    GuardUserRetval,
    Authenticatable
)

from ._helpers import NoopUserProvider1

_CONFIG = {
    'defaults': {
        'guard': 'web'
    },
    'guards': {
        'web': {
            'driver': 'session'
        },
        'noop': {
            'driver': "noop"
        }
    }
}

def test_auth_manager_init() -> None:
    config = AuthConfig(copy.deepcopy(_CONFIG))
    auth = AuthManager(config=config)
    assert _CONFIG == auth._config._config


def test_auth_manager_no_default_guard() -> None:
    auth = AuthManager(AuthConfig({}))

    with pytest.raises(RuntimeError) as exc_info:
        auth.guard()

    assert "No default guard specified" == exc_info.value.args[0]

def session_guard_factory(name: str) -> SessionGuard:
    user_provider = NoopUserProvider1()
    session = SessionStore("session1", NullSessionHandler())
    return SessionGuard(name, user_provider, session)


def test_auth_manager_guard_default() -> None:
    config = AuthConfig(copy.deepcopy(_CONFIG))
    config.add_driver_factory("session", session_guard_factory)

    auth = AuthManager(config=config)

    guard = auth.guard()

    assert isinstance(guard, Guard)
    assert isinstance(guard, StatefullGuard)
    assert isinstance(guard, SessionGuard)

    assert "session1" == guard._session.name


class NoopGuard1(Guard):

    def check(self) -> GuardCheckRetval:
        return True

    def user(self) -> GuardUserRetval:
        pass

    async def async_user(self) -> Authenticatable | None:
        pass

def noop_session_guard_factory(name: str) -> NoopGuard1:
    return NoopGuard1()

def test_auth_manager_guard() -> None:
    config = AuthConfig(copy.deepcopy(_CONFIG))
    config.add_driver_factory("noop", noop_session_guard_factory)

    auth = AuthManager(config=config)

    guard = auth.guard("noop")

    assert isinstance(guard, Guard)
    assert isinstance(guard, NoopGuard1)

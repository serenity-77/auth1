import typing as t

from auth1 import (
    SessionManager,
    AuthManager
)

session_manager: SessionManager | None = None
auth_manager: AuthManager | None = None

def session_manager_init(config: t.Dict[str, t.Any]) -> None:
    global session_manager
    session_manager = SessionManager(config)

def auth_manager_init(config: t.Dict[str, t.Any]) -> None:
    global auth_manager
    auth_manager = AuthManager(config)

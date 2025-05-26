import typing as t

from auth1 import (
    UserProvider,
    GenericUser,
    AuthenticatableRetval,
    Authenticatable
)

class NoopUserProvider1(UserProvider):

    def retrieve_by_id(self, id: str | int) -> AuthenticatableRetval:
        return GenericUser({
            'userid': "harianja",
            'password': "Password123!",
            'email': "harianja@lundu.com"
        })

    def retrieve_by_credentials(self, credentials: t.Dict[str, t.Any]) -> AuthenticatableRetval:
        return GenericUser({
            'userid': "harianja",
            'password': "Password123!",
            'email': "harianja@lundu.com"
        })

    def validate_credentials(self, user: Authenticatable, credentials: t.Dict[str, t.Any]) -> bool:
        return True

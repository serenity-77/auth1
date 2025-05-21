import typing as t
from ._types import AuthFactory, Guard

# config = {
#     'defaults': {
#         'guards': 'web'
#     },
#
#     'guards': {
#         'web': {
#             'driver': 'session'
#         }
#     }
# }

class AuthConfig:

    def __init__(self, config: t.Dict[str, t.Any]) -> None:
        self._config = config

    def add_driver_factory(self, name: str, factory: t.Callable[[str], Guard]) -> None:
        try:
            drivers = self._config['drivers']
        except KeyError:
            drivers = self._config.setdefault('drivers', {})

        drivers[name] = factory

    def create_driver(self, name: str) -> Guard | None:
        pass

    def __getitem__(self, key: str) -> t.Any:
        return self._config[key]

    def __setitem__(self, key: str, value: t.Any) -> None:
        self._config[key] = value


class AuthManager(AuthFactory):

    def __init__(self, config: AuthConfig):
        self._config = config

    def guard(self, name: str | None = None) -> Guard | None:
        if name is None:
            name = self._get_default_driver()

        config = self._config['guards'][name]
        guard_factory = self._config['drivers'][config['driver']]

        guard: Guard = guard_factory(name)

        return guard

    def _get_default_driver(self) -> str:
        try:
            defaults = self._config['defaults']
        except KeyError:
            defaults = {}

        if isinstance(defaults, dict):
            try:
                return defaults['guard'] # type: ignore
            except KeyError:
                pass

        raise RuntimeError("No default guard specified")

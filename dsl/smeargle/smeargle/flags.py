from __future__ import annotations

import os


class Flags:
    def get(self, name: str, /, *, default: bool | None = None) -> bool:
        """Throws if default is None and name doesn't exist"""
        env_key = f"{name.upper()}"
        if env_key not in os.environ:
            if default is None:
                raise AttributeError(
                    f"flag {name!r} is not set (no {env_key} in the environment) and no default was given"
                )
            return default

        # True biased by default
        return os.environ[env_key].strip().lower() != "false"

    def __getattr__(self, name: str) -> bool:
        """
        flags.MY_FLAG_HERE simply wraps getenv(MY_FLAG_HERE)
        """
        return self.get(name)

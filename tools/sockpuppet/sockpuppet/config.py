import tomllib
from dataclasses import dataclass


@dataclass
class VpnConfig:
    name: str
    host: str
    port: int

    @classmethod
    def load(cls, path: str = "sockpuppet.toml") -> "VpnConfig":
        with open(path, "rb") as f:
            data = tomllib.load(f).get("vpn", {})

        name = data.get("name")
        if name is None:
            raise ValueError("Config missing required field: 'name'")

        host = data.get("host")
        if host is None:
            raise ValueError("Config missing required field: 'host'")

        port = data.get("port")
        if port is None:
            raise ValueError("Config missing required field: 'port'")

        return cls(name=name, host=host, port=port)

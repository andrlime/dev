from .app import VpnApp as VpnApp
from .config import VpnConfig as VpnConfig


def main() -> None:
    import argparse

    from .backend import SensibleDefaultBackend

    parser = argparse.ArgumentParser(description="sockpuppet SOCKS proxy VPN")
    parser.add_argument(
        "-c",
        "--config",
        default="config.toml",
        metavar="PATH",
        help="path to config.toml (default: config.toml)",
    )
    args = parser.parse_args()

    cfg = VpnConfig.load(args.config)
    backend = SensibleDefaultBackend(cfg.name, cfg.host, cfg.port)
    VpnApp(backend).run()

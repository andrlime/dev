from .app import VpnApp as VpnApp
from .config import VpnConfig as VpnConfig


def main() -> None:
    import argparse
    import sys
    from pathlib import Path

    from .backend import ManagedVpn, SensibleDefaultBackend
    from .log import set_log_level

    default_config = Path(sys.argv[0]).parent.resolve() / "sockpuppet.toml"

    parser = argparse.ArgumentParser(description="sockpuppet SOCKS proxy VPN")
    parser.add_argument(
        "-c",
        "--config",
        default=str(default_config),
        type=str,
        metavar="PATH",
        help="path to config (default: sockpuppet.toml next to the executable)",
    )
    parser.add_argument(
        "-a",
        "--automatic",
        action="store_true",
        help="whether to automatically enable the VPN as RAII without a GUI",
    )
    parser.add_argument(
        "-L",
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="logging verbosity (default: %(default)s)",
    )
    args = parser.parse_args()

    set_log_level(args.log_level)

    cfg = VpnConfig.load(args.config)
    backend = SensibleDefaultBackend(cfg.name, cfg.host, cfg.port)
    if args.automatic:
        ManagedVpn(backend).run()
    else:
        VpnApp(backend).run()

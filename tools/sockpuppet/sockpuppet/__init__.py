from .config import VpnConfig as VpnConfig


def main() -> None:
    import argparse
    import sys
    from pathlib import Path

    from .log import Logger

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
    parser.add_argument(
        "-f",
        "--log-file",
        default=None,
        type=str,
        metavar="PATH",
        help="optional path to also write logs to a file",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="disable colored log output",
    )
    args = parser.parse_args()

    Logger.set_log_level(args.log_level)
    if args.no_color:
        Logger.set_no_color(True)
    if args.log_file:
        Logger.set_log_file(args.log_file)

    from .app import VpnApp
    from .backend import ManagedVpn, SensibleDefaultBackend

    main_logger = Logger.get(__name__)
    main_logger.debug(f"Read args {str(args)} from CLI arguments")

    cfg = VpnConfig.load(args.config)
    backend = SensibleDefaultBackend(cfg.name, cfg.host, cfg.port)
    if args.automatic:
        ManagedVpn(backend).run()
    else:
        VpnApp(backend).run()

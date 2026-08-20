import argparse
import sys
from pathlib import Path

from .config import VpnConfig
from .log import Logger


class Runner:
    @staticmethod
    def run(argv: list[str] | None = None) -> None:
        args = Runner._parse_args(argv)
        Runner._configure_logging(args)

        from .app import VpnApp
        from .backend import SensibleDefaultBackend
        from .managed import ManagedVpn

        logger = Logger.get(__name__)
        logger.debug(f"Read args {args} from CLI arguments")

        cfg = VpnConfig.load(args.config)
        backend = SensibleDefaultBackend(cfg.name, cfg.host, cfg.port)
        if args.automatic:
            ManagedVpn(backend).run()
        else:
            VpnApp(backend).run()

    @staticmethod
    def _parse_args(argv: list[str] | None) -> argparse.Namespace:
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
        return parser.parse_args(argv)

    @staticmethod
    def _configure_logging(args: argparse.Namespace) -> None:
        Logger.set_log_level(args.log_level)
        if args.no_color:
            Logger.set_no_color(True)
        if args.log_file:
            Logger.set_log_file(args.log_file)

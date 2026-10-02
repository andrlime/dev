from __future__ import annotations

import argparse
import sys
from pathlib import Path

from alakazam.config import AlakazamConfig
from alakazam.sync import sync as run_sync


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="alakazam",
        description="Add your description here",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    sync_parser = subparsers.add_parser("sync", help="Sync a directory to a drive, per its config file.")
    sync_parser.add_argument("directory", type=Path, help="Directory containing the config file.")
    sync_parser.add_argument(
        "--config-filename",
        default="alakazam.toml",
        help="Name of the config file inside the directory (default: 'alakazam.toml').",
    )
    sync_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be transferred without copying anything.",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    directory: Path = args.directory
    if not directory.is_dir():
        parser.error(f"not a directory: {directory}")

    config_path = directory / args.config_filename
    if not config_path.exists():
        parser.error(f"missing config file: {config_path}")

    try:
        config = AlakazamConfig.load(config_path)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    try:
        run_sync(directory, config, dry_run=args.dry_run)
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    return 0

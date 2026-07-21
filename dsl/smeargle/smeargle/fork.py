from __future__ import annotations

import re
import shutil
import subprocess
import tempfile
from pathlib import Path

_HEADER_RE = re.compile(r"^# smeargle-fork: source=(?P<source>.+) branch=(?P<branch>.+)$")


class MergeConflict(Exception):
    pass


class Fork:
    @staticmethod
    def header(source_name: str, branch_name: str) -> str:
        return f"# smeargle-fork: source={source_name} branch={branch_name}\n"

    @staticmethod
    def base_path(fork_path: Path) -> Path:
        return fork_path.with_name(f".{fork_path.name}.base")

    @staticmethod
    def create(source_path: Path, branch_name: str) -> Path:
        if not source_path.exists():
            raise FileNotFoundError(f"{source_path} not found")

        fork_path = source_path.with_name(f"{source_path.stem}_{branch_name}{source_path.suffix}")
        if fork_path.exists():
            raise FileExistsError(f"{fork_path} already exists")

        source_content = source_path.read_text()
        fork_path.write_text(Fork.header(source_path.name, branch_name) + source_content)

        # Write to the base path so we can do a three-way merge
        Fork.base_path(fork_path).write_text(source_content)
        return fork_path

    @staticmethod
    def discard(branch_path: Path) -> None:
        branch_path.unlink(missing_ok=True)
        Fork.base_path(branch_path).unlink(missing_ok=True)

    @staticmethod
    def source_of(branch_path: Path) -> Path:
        if not branch_path.exists():
            raise FileNotFoundError(f"{branch_path} not found")

        first_line = branch_path.read_text().split("\n", 1)[0]
        match = _HEADER_RE.match(first_line)
        if not match:
            raise ValueError(f"{branch_path} has no smeargle-fork header -- not a fork")

        source_path = branch_path.with_name(match.group("source"))
        if not source_path.exists():
            raise FileNotFoundError(f"{source_path} (forked from, per {branch_path}) not found")
        return source_path

    @staticmethod
    def merge(branch_path: Path) -> bool:
        """Three-way merge branch_path's changes back into the file it was
        forked from. Returns True if changes were applied, False if there
        was nothing to merge. Conservative and all-or-nothing: if any part
        of the merge conflicts, raises MergeConflict and touches nothing."""
        if shutil.which("git") is None:
            raise RuntimeError("`git` not found on PATH (needed for the three-way merge)")

        source_path = Fork.source_of(branch_path)
        base_path = Fork.base_path(branch_path)
        if not base_path.exists():
            raise FileNotFoundError(
                f"{base_path} (merge base for {branch_path}) not found -- "
                "was this fork created by an older version of smeargle?"
            )

        base_content = base_path.read_text()
        source_content = source_path.read_text()
        _, _, branch_content = branch_path.read_text().partition("\n")  # drop the header line

        if source_content == base_content and branch_content == base_content:
            return False

        with tempfile.TemporaryDirectory() as tmp_dir:
            ours_path = Path(tmp_dir) / "ours"
            theirs_path = Path(tmp_dir) / "theirs"
            ours_path.write_text(source_content)
            theirs_path.write_text(branch_content)

            result = subprocess.run(
                ["git", "merge-file", "--stdout", str(ours_path), str(base_path), str(theirs_path)],
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                raise MergeConflict(result.stdout.strip() or result.stderr.strip())
            merged = result.stdout

        if merged == source_content:
            return False

        source_path.write_text(merged)
        return True

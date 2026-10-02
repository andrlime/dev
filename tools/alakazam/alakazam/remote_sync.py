from __future__ import annotations

import subprocess
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class RemoteSync:
    source: str | Path
    destination: str | Path

    # Transfer behavior
    archive: bool = True
    recursive: bool = False
    links: bool = True
    perms: bool = True
    times: bool = True
    group: bool = True
    owner: bool = True
    devices: bool = False
    specials: bool = False
    hard_links: bool = False
    sparse: bool = False
    whole_file: bool = False
    one_file_system: bool = False
    prune_empty_dirs: bool = False

    # What counts as "changed"
    checksum: bool = False
    size_only: bool = False
    ignore_times: bool = False
    update: bool = False
    existing: bool = False
    ignore_existing: bool = False

    # Deletion behavior
    delete: bool = False
    delete_before: bool = False
    delete_during: bool = False
    delete_after: bool = False
    delete_excluded: bool = False
    remove_source_files: bool = False
    force: bool = False

    # Output / safety
    verbose: bool = True
    human_readable: bool = True
    stats: bool = True
    progress: bool = False
    itemize_changes: bool = False
    dry_run: bool = False

    # Performance / transport
    compress: bool = False
    partial: bool = False
    bwlimit: str | None = None
    timeout: int | None = None
    port: int | None = None
    rsh: str | None = None  # e.g. "ssh -p 2222 -i ~/.ssh/id_ed25519"

    # Filtering
    exclude: list[str] = field(default_factory=list)
    include: list[str] = field(default_factory=list)
    exclude_from: Path | None = None
    include_from: Path | None = None
    filter_rules: list[str] = field(default_factory=list)
    max_size: str | None = None
    min_size: str | None = None

    # Backups / incremental
    backup: bool = False
    backup_dir: Path | None = None
    link_dest: Path | None = None

    # Logging
    log_file: Path | None = None
    out_format: str | None = None

    # Escape hatch for anything not modeled above
    extra_args: list[str] = field(default_factory=list)

    def build_command(self) -> list[str]:
        cmd = ["rsync"]

        if self.archive:
            cmd.append("-a")
        else:
            if self.recursive:
                cmd.append("-r")
            if self.links:
                cmd.append("-l")
            if self.perms:
                cmd.append("-p")
            if self.times:
                cmd.append("-t")
            if self.group:
                cmd.append("-g")
            if self.owner:
                cmd.append("-o")
            if self.devices:
                cmd.append("--devices")
            if self.specials:
                cmd.append("--specials")

        if self.hard_links:
            cmd.append("-H")
        if self.sparse:
            cmd.append("-S")
        if self.whole_file:
            cmd.append("-W")
        if self.one_file_system:
            cmd.append("-x")
        if self.prune_empty_dirs:
            cmd.append("--prune-empty-dirs")

        if self.checksum:
            cmd.append("-c")
        if self.size_only:
            cmd.append("--size-only")
        if self.ignore_times:
            cmd.append("-I")
        if self.update:
            cmd.append("-u")
        if self.existing:
            cmd.append("--existing")
        if self.ignore_existing:
            cmd.append("--ignore-existing")

        if self.delete:
            cmd.append("--delete")
        if self.delete_before:
            cmd.append("--delete-before")
        if self.delete_during:
            cmd.append("--delete-during")
        if self.delete_after:
            cmd.append("--delete-after")
        if self.delete_excluded:
            cmd.append("--delete-excluded")
        if self.remove_source_files:
            cmd.append("--remove-source-files")
        if self.force:
            cmd.append("--force")

        if self.verbose:
            cmd.append("-v")
        if self.human_readable:
            cmd.append("-h")
        if self.stats:
            cmd.append("--stats")
        if self.progress:
            cmd.append("--progress")
        if self.itemize_changes:
            cmd.append("-i")
        if self.dry_run:
            cmd.append("-n")

        if self.compress:
            cmd.append("-z")
        if self.partial:
            cmd.append("--partial")
        if self.bwlimit:
            cmd.append(f"--bwlimit={self.bwlimit}")
        if self.timeout is not None:
            cmd.append(f"--timeout={self.timeout}")
        if self.port is not None:
            cmd.append(f"--port={self.port}")
        if self.rsh:
            cmd.append(f"--rsh={self.rsh}")

        for pattern in self.exclude:
            cmd.append(f"--exclude={pattern}")
        for pattern in self.include:
            cmd.append(f"--include={pattern}")
        if self.exclude_from:
            cmd.append(f"--exclude-from={self.exclude_from}")
        if self.include_from:
            cmd.append(f"--include-from={self.include_from}")
        for rule in self.filter_rules:
            cmd.append(f"--filter={rule}")
        if self.max_size:
            cmd.append(f"--max-size={self.max_size}")
        if self.min_size:
            cmd.append(f"--min-size={self.min_size}")

        if self.backup:
            cmd.append("--backup")
        if self.backup_dir:
            cmd.append(f"--backup-dir={self.backup_dir}")
        if self.link_dest:
            cmd.append(f"--link-dest={self.link_dest}")

        if self.log_file:
            cmd.append(f"--log-file={self.log_file}")
        if self.out_format:
            cmd.append(f"--out-format={self.out_format}")

        cmd.extend(self.extra_args)

        cmd.extend([f"{self.source}/", f"{self.destination}/"])
        return cmd

    def run(self) -> subprocess.CompletedProcess[bytes]:
        return subprocess.run(self.build_command(), check=True)

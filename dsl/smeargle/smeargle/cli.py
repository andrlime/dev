from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Annotated

import typer

from .fork import Fork, MergeConflict
from .runtime import Runtime

app = typer.Typer()


@app.command()
def build(
    content_path: Annotated[Path, typer.Argument(help="source .py")],
    output_path: Annotated[Path, typer.Argument(help="destination .pdf")],
    dry_run: Annotated[
        bool,
        typer.Option("--dry-run", "-D", help="keep the generated .typ file instead of cleaning it up"),
    ] = False,
) -> None:
    runtime = Runtime(content_path=content_path, output_path=output_path, dry_run=dry_run)
    raise typer.Exit(code=runtime.render())


@app.command()
def format(
    file_path: Annotated[Path, typer.Argument(help="content file to format")],
) -> None:
    # TODO: Create a library to offload calls to tools like this
    LINE_COLUMN_LIMIT = 200
    raise typer.Exit(code=subprocess.call(["uvx", "black", "--line-length", str(LINE_COLUMN_LIMIT), str(file_path)]))


@app.command()
def fork(
    source_path: Annotated[Path, typer.Argument(help="file to fork")],
    branch_name: Annotated[str, typer.Argument(help="name for the new branch")],
) -> None:
    try:
        fork_path = Fork.create(source_path, branch_name)
    except (FileExistsError, FileNotFoundError) as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(code=1) from e
    typer.echo(f"forked {source_path} -> {fork_path}")


@app.command()
def merge(
    branch_path: Annotated[Path, typer.Argument(help="forked file to merge back into its source")],
    keep_branch: Annotated[
        bool,
        typer.Option("--keep-branch", help="don't delete the branch file after a successful merge"),
    ] = False,
) -> None:
    try:
        merged = Fork.merge(branch_path)
    except MergeConflict as e:
        typer.echo("merge refused: source and branch changed the same lines differently", err=True)
        typer.echo(str(e), err=True)
        raise typer.Exit(code=1) from e
    except (ValueError, FileNotFoundError, RuntimeError) as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(code=1) from e

    typer.echo(f"merged {branch_path} into its source" if merged else "nothing to merge")

    if not keep_branch:
        Fork.discard(branch_path)


def main() -> None:
    app()


if __name__ == "__main__":
    main()

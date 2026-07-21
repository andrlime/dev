from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Annotated

import typer

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


def main() -> None:
    app()


if __name__ == "__main__":
    main()

from __future__ import annotations

import runpy
import shutil
import subprocess
from pathlib import Path

from .arena import Arena
from .page import PageConfig
from .resume import Resume


class Runtime:
    def __init__(self, content_path: Path, output_path: Path, *, dry_run: bool = False) -> None:
        self.content_path = content_path
        self.output_path = output_path
        self.dry_run = dry_run
        self.typst_path: Path | None = None

    def run(self) -> Resume:
        Arena.get().reset()
        namespace = runpy.run_path(str(self.content_path), run_name="__resume_content__")

        page = namespace.get("page")
        if not isinstance(page, PageConfig):
            raise RuntimeError(f"{self.content_path} did not define a top-level `page: PageConfig`")

        return Resume.from_arena(page)

    def source_to_typst(self) -> Path:
        typst_path = self.content_path.with_suffix(".typ")
        typst_path.write_text(self.run().to_typst())
        self.typst_path = typst_path
        return typst_path

    def typst_to_pdf(self) -> int:
        if self.typst_path is None:
            raise RuntimeError("source_to_typst() must run before typst_to_pdf()")

        typst_bin = shutil.which("typst")
        if typst_bin is None:
            raise RuntimeError("`typst` not found on PATH")

        result = subprocess.run([typst_bin, "compile", str(self.typst_path), str(self.output_path)])
        return result.returncode

    def clean_typst(self) -> None:
        if self.typst_path is not None:
            self.typst_path.unlink(missing_ok=True)

    def render(self) -> int:
        self.source_to_typst()
        exit_code = self.typst_to_pdf()
        if not self.dry_run:
            self.clean_typst()
        return exit_code

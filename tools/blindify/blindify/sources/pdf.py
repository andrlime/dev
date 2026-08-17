from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pypdfium2 as pdfium

from blindify.sources.base import SourcePage

_PDF_MAGIC = b"%PDF-"


def is_pdf(path: Path) -> bool:
    if path.suffix.lower() != ".pdf":
        return False
    try:
        with path.open("rb") as f:
            header = f.read(len(_PDF_MAGIC))
    except OSError:
        return False
    return header == _PDF_MAGIC


class PdfSource:
    def __init__(self, path: Path) -> None:
        self._document = pdfium.PdfDocument(str(path))

    def page_count(self) -> int:
        return len(self._document)

    def iter_pages(self, dpi: int) -> Iterator[SourcePage]:
        scale = dpi / 72
        for index in range(len(self._document)):
            page = self._document.get_page(index)
            try:
                width_pt, height_pt = page.get_size()
                bitmap = page.render(scale=scale, rev_byteorder=True)
                try:
                    image = bitmap.to_pil().convert("RGB")
                finally:
                    bitmap.close()
                yield SourcePage(
                    image=image,
                    width_pt=width_pt,
                    height_pt=height_pt,
                    index=index,
                )
            finally:
                page.close()

"""Builds the expanded output PDF: one page per (original page, filter)."""

from __future__ import annotations

from pathlib import Path

from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

import tqdm

from blindify.filters.base import Filter
from blindify.sources.base import Source

HEADER_HEIGHT = 0.6 * inch
"""Vertical space reserved at the top of each output page for the label."""

MARGIN = 0.4 * inch
"""Inset between the page edges and the bounding box around the content."""

LABEL_FONT = "Helvetica-Bold"
LABEL_FONT_SIZE = 14


def compose(
    source: Source,
    filters: list[Filter],
    dpi: int,
    output_path: Path,
) -> int:
    pdf_canvas = canvas.Canvas(str(output_path))
    page_count = 0

    for page in tqdm.tqdm(source.iter_pages(dpi), desc="page"):
        out_width = page.width_pt
        out_height = page.height_pt + HEADER_HEIGHT

        for filt in filters:
            pdf_canvas.setPageSize((out_width, out_height))

            pdf_canvas.setFont(LABEL_FONT, LABEL_FONT_SIZE)
            pdf_canvas.drawCentredString(
                out_width / 2,
                out_height - HEADER_HEIGHT / 2 - LABEL_FONT_SIZE / 3,
                filt.label,
            )

            box_x = MARGIN
            box_y = MARGIN
            box_width = out_width - 2 * MARGIN
            box_height = page.height_pt - 2 * MARGIN

            filtered_image = filt.apply(page.image)
            img_x, img_y, img_width, img_height = _fit_within_box(
                filtered_image.size, (box_width, box_height), (box_x, box_y)
            )

            pdf_canvas.rect(box_x, box_y, box_width, box_height, stroke=1, fill=0)
            pdf_canvas.drawImage(
                ImageReader(filtered_image),
                img_x,
                img_y,
                width=img_width,
                height=img_height,
            )

            pdf_canvas.showPage()
            page_count += 1

    pdf_canvas.save()
    return page_count


def _fit_within_box(
    image_size: tuple[int, int],
    box_size: tuple[float, float],
    box_origin: tuple[float, float],
) -> tuple[float, float, float, float]:
    image_width, image_height = image_size
    box_width, box_height = box_size
    box_x, box_y = box_origin

    scale = min(box_width / image_width, box_height / image_height)
    width = image_width * scale
    height = image_height * scale

    x = box_x + (box_width - width) / 2
    y = box_y + (box_height - height) / 2
    return x, y, width, height

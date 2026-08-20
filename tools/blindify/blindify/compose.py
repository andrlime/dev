from __future__ import annotations

from pathlib import Path

import tqdm
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

from blindify.constants import HEADER_HEIGHT, LABEL_FONT, LABEL_FONT_SIZE, MARGIN
from blindify.filters.base import Filter
from blindify.sources.base import Source, SourcePage


def compose(
    source: Source,
    filters: list[Filter],
    dpi: int,
    output_path: Path,
) -> int:
    pdf_canvas = canvas.Canvas(str(output_path))
    page_count = 0

    for page in tqdm.tqdm(source.iter_pages(dpi), desc="page"):
        for filt in filters:
            _draw_page(pdf_canvas, page, filt)
            page_count += 1

    pdf_canvas.save()
    return page_count


def _draw_page(pdf_canvas: canvas.Canvas, page: SourcePage, filt: Filter) -> None:
    out_width = page.width_pt
    out_height = page.height_pt + HEADER_HEIGHT

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
    img_x, img_y, img_width, img_height = _fit_within_box(filtered_image.size, (box_width, box_height), (box_x, box_y))

    pdf_canvas.rect(box_x, box_y, box_width, box_height, stroke=1, fill=0)
    pdf_canvas.drawImage(
        ImageReader(filtered_image),
        img_x,
        img_y,
        width=img_width,
        height=img_height,
    )

    pdf_canvas.showPage()


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

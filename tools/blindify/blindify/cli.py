from __future__ import annotations

import argparse
import sys
from pathlib import Path

from pypdfium2 import PdfiumError

from blindify.compose import compose
from blindify.filters import FILTER_REGISTRY
from blindify.sources.pdf import PdfSource, is_pdf

MAX_RECOMMENDED_PAGES = 8
DEFAULT_DPI = 150


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="blindify",
        description=(
            "Expand a PDF into a page per colorblindness type, to check whether the document is colorblind-friendly."
        ),
    )
    parser.add_argument(
        "input",
        type=Path,
        nargs="?",
        help="Path to the input PDF file.",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="Output PDF path (default: <input>_blindify.pdf next to the input).",
    )
    parser.add_argument(
        "--dpi",
        type=int,
        default=DEFAULT_DPI,
        help=f"Rendering resolution in DPI (default: {DEFAULT_DPI}).",
    )
    parser.add_argument(
        "--types",
        nargs="+",
        choices=list(FILTER_REGISTRY),
        default=None,
        metavar="TYPE",
        help=("Restrict output to these filter types (default: all). Choices: " + ", ".join(FILTER_REGISTRY)),
    )
    parser.add_argument(
        "--list-types",
        action="store_true",
        help="List all available filter types and exit.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.list_types:
        for key, filt in FILTER_REGISTRY.items():
            print(f"{key}: {filt.label}")
        return 0

    if args.input is None:
        parser.error("the following arguments are required: input")

    if not args.input.exists():
        parser.error(f"input file not found: {args.input}")

    if not is_pdf(args.input):
        parser.error(
            f"blindify only supports PDF input files, got: {args.input} (expected a .pdf file with a valid PDF header)"
        )

    output = args.output or args.input.with_name(f"{args.input.stem}_blindify.pdf")

    try:
        source = PdfSource(args.input)
    except PdfiumError as exc:  # raised by pypdfium2 on unreadable/corrupt PDFs
        print(f"error: could not open PDF: {exc}", file=sys.stderr)
        return 1

    page_count = source.page_count()
    if page_count == 0:
        print("error: input PDF has no pages", file=sys.stderr)
        return 1

    selected_keys = args.types or list(FILTER_REGISTRY)
    selected_filters = [FILTER_REGISTRY[key] for key in selected_keys]

    if page_count > MAX_RECOMMENDED_PAGES:
        print(
            f"warning: input PDF has {page_count} pages; output will contain "
            f"{page_count * len(selected_filters)} pages",
            file=sys.stderr,
        )

    written = compose(source, selected_filters, dpi=args.dpi, output_path=output)
    print(f"wrote {output} ({written} pages)")
    return 0

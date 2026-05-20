from __future__ import annotations

import argparse
import logging
from pathlib import Path

from .converter import convert_directory, parse_resize


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="heic2jpg",
        description="Convert HEIC/HEIF images to JPG format.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  heic2jpg /path/to/images
  heic2jpg /path/to/images --quality 90 --workers 8
  heic2jpg /path/to/images --recursive --resize 1920x1080 --output ./jpgs
  uvx --from git+https://github.com/iancleary/heic2jpg.git heic2jpg /path/to/images
""",
    )
    parser.add_argument("heic_dir", type=Path, help="Directory containing HEIC/HEIF images.")
    parser.add_argument(
        "-q",
        "--quality",
        type=int,
        default=90,
        help="Output JPG image quality, 1-100. Default: 90.",
    )
    parser.add_argument(
        "-w",
        "--workers",
        type=int,
        default=4,
        help="Number of parallel conversion workers. Default: 4.",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="Output directory. Default: ConvertedFiles inside the source directory.",
    )
    parser.add_argument(
        "-r",
        "--recursive",
        action="store_true",
        help="Find HEIC/HEIF files recursively and preserve folder hierarchy in the output.",
    )
    parser.add_argument(
        "--resize",
        default=None,
        help="Resize images before saving, as WIDTHxHEIGHT, for example 1920x1080.",
    )
    parser.add_argument(
        "-d",
        "--delete-originals",
        action="store_true",
        help="Delete each original HEIC/HEIF file after a successful conversion.",
    )
    parser.add_argument(
        "--replace-output",
        action="store_true",
        help="Delete and recreate the output directory before converting.",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(message)s",
    )

    try:
        resize = parse_resize(args.resize)
    except ValueError as exc:
        parser.error(str(exc))

    result = convert_directory(
        args.heic_dir,
        quality=args.quality,
        workers=args.workers,
        output_dir=args.output,
        recursive=args.recursive,
        resize=resize,
        delete_originals=args.delete_originals,
        replace_output=args.replace_output,
    )

    if result.message:
        print(result.message)
    if result.files_failed:
        print(f"Failed files: {result.files_failed}")
    if result.total_time:
        print(f"Completed in {result.total_time:.2f}s")

    return 1 if result.status == "error" or result.files_failed else 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import logging
import os
import shutil
import time
from collections.abc import Iterable
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, UnidentifiedImageError
from pillow_heif import register_heif_opener

logger = logging.getLogger(__name__)

HEIC_SUFFIXES = {".heic", ".heif"}


@dataclass(frozen=True)
class ConversionResult:
    """Summary of a batch conversion."""

    status: str
    files_converted: int = 0
    files_failed: int = 0
    total_time: float = 0.0
    average_time_per_file: float = 0.0
    failed_files: tuple[str, ...] = ()
    message: str = ""


def parse_resize(value: str | None) -> tuple[int, int] | None:
    """Parse WIDTHxHEIGHT resize values."""

    if not value:
        return None

    try:
        width_text, height_text = value.lower().split("x", maxsplit=1)
        width = int(width_text)
        height = int(height_text)
    except ValueError as exc:
        msg = "Resize must use WIDTHxHEIGHT, for example 1920x1080"
        raise ValueError(msg) from exc

    if width <= 0 or height <= 0:
        msg = "Resize dimensions must be positive integers"
        raise ValueError(msg)

    return width, height


def find_heic_files(directory: Path | str, *, recursive: bool = False) -> list[Path]:
    """Find HEIC/HEIF files in a directory."""

    root = Path(directory)
    if not root.is_dir():
        msg = f"Directory does not exist: {root}"
        raise NotADirectoryError(msg)

    pattern: Iterable[Path] = root.rglob("*") if recursive else root.iterdir()
    return sorted(
        path for path in pattern if path.is_file() and path.suffix.lower() in HEIC_SUFFIXES
    )


def output_path_for_file(
    source: Path, *, source_root: Path, output_root: Path, recursive: bool
) -> Path:
    """Return the JPG output path for a source HEIC file."""

    relative = source.relative_to(source_root) if recursive else Path(source.name)
    return output_root / relative.with_suffix(".jpg")


def convert_file(
    source: Path | str,
    destination: Path | str,
    *,
    quality: int = 90,
    resize: tuple[int, int] | None = None,
) -> float:
    """Convert one HEIC/HEIF file to JPG and return elapsed seconds."""

    if not 1 <= quality <= 100:
        msg = "quality must be between 1 and 100"
        raise ValueError(msg)

    register_heif_opener()
    source_path = Path(source)
    destination_path = Path(destination)
    destination_path.parent.mkdir(parents=True, exist_ok=True)

    started = time.perf_counter()
    with Image.open(source_path) as image:
        if resize:
            image = image.resize(resize, Image.Resampling.LANCZOS)

        exif_data = image.info.get("exif")
        save_kwargs: dict[str, object] = {"quality": quality, "optimize": True}
        if exif_data:
            save_kwargs["exif"] = exif_data

        # JPEG cannot represent alpha; normalize images that have it.
        if image.mode in {"RGBA", "LA", "P"}:
            image = image.convert("RGB")

        image.save(destination_path, "JPEG", **save_kwargs)

    source_stat = source_path.stat()
    os.utime(destination_path, (source_stat.st_atime, source_stat.st_mtime))
    return time.perf_counter() - started


def convert_directory(
    heic_dir: Path | str,
    *,
    quality: int = 90,
    workers: int = 4,
    output_dir: Path | str | None = None,
    recursive: bool = False,
    resize: tuple[int, int] | None = None,
    delete_originals: bool = False,
    replace_output: bool = False,
) -> ConversionResult:
    """Convert HEIC/HEIF images in a directory to JPG using parallel workers."""

    started = time.perf_counter()
    source_root = Path(heic_dir).expanduser().resolve()
    if not source_root.is_dir():
        return ConversionResult(
            status="error",
            message=f"Directory does not exist: {source_root}",
        )

    if not 1 <= quality <= 100:
        return ConversionResult(status="error", message="quality must be between 1 and 100")

    if workers < 1:
        return ConversionResult(status="error", message="workers must be at least 1")

    jpg_root = (
        Path(output_dir).expanduser().resolve()
        if output_dir is not None
        else source_root / "ConvertedFiles"
    )

    if jpg_root.exists() and replace_output:
        shutil.rmtree(jpg_root)
    jpg_root.mkdir(parents=True, exist_ok=True)

    try:
        heic_files = find_heic_files(source_root, recursive=recursive)
    except NotADirectoryError as exc:
        return ConversionResult(status="error", message=str(exc))

    tasks = [
        (
            source,
            output_path_for_file(
                source,
                source_root=source_root,
                output_root=jpg_root,
                recursive=recursive,
            ),
        )
        for source in heic_files
    ]
    tasks = [(source, destination) for source, destination in tasks if not destination.exists()]

    if not heic_files:
        return ConversionResult(status="completed", message="No HEIC/HEIF files found.")
    if not tasks:
        return ConversionResult(status="completed", message="No new files to convert.")

    converted = 0
    failed: list[str] = []
    processing_time = 0.0

    logger.info("Converting %d HEIC/HEIF file(s) to JPG...", len(tasks))
    with ThreadPoolExecutor(max_workers=workers) as executor:
        future_to_source = {
            executor.submit(
                convert_file, source, destination, quality=quality, resize=resize
            ): source
            for source, destination in tasks
        }
        for future in as_completed(future_to_source):
            source = future_to_source[future]
            try:
                processing_time += future.result()
            except (UnidentifiedImageError, FileNotFoundError, OSError, ValueError) as exc:
                logger.error("Error converting %s: %s", source, exc)
                failed.append(str(source))
                continue

            converted += 1
            if delete_originals:
                source.unlink()
            logger.info("Converted %d/%d", converted, len(tasks))

    total_time = time.perf_counter() - started
    return ConversionResult(
        status="completed",
        files_converted=converted,
        files_failed=len(failed),
        total_time=total_time,
        average_time_per_file=processing_time / len(tasks),
        failed_files=tuple(failed),
        message=f"Successfully converted {converted}/{len(tasks)} file(s).",
    )

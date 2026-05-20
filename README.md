# heic2jpg

A small, `uv`-friendly command-line tool for converting HEIC/HEIF images to JPG.

This is a modern Python packaging port inspired by [`dragonGR/PyHEIC2JPG`](https://github.com/dragonGR/PyHEIC2JPG). It keeps the same useful workflow—batch conversion, recursive mode, custom output directories, resizing, parallel workers, and EXIF preservation—while packaging it as an installable CLI with a `pyproject.toml`.

## Run with `uvx` from GitHub

No clone or virtualenv setup required:

```bash
uvx --from git+https://github.com/iancleary/heic2jpg.git heic2jpg /path/to/heic/files
```

If you want a tiny reusable shell script, save this as `heic2jpg` somewhere on your `PATH`:

```bash
#!/usr/bin/env bash
exec uvx --from git+https://github.com/iancleary/heic2jpg.git heic2jpg "$@"
```

Useful examples:

```bash
# Convert HEIC/HEIF files in one directory into ./ConvertedFiles
uvx --from git+https://github.com/iancleary/heic2jpg.git heic2jpg ~/Pictures

# Preserve subdirectories while recursively converting
uvx --from git+https://github.com/iancleary/heic2jpg.git heic2jpg ~/Pictures --recursive

# Choose quality, parallel workers, output folder, and resize
uvx --from git+https://github.com/iancleary/heic2jpg.git heic2jpg ~/Pictures \
  --quality 92 \
  --workers 8 \
  --recursive \
  --resize 1920x1080 \
  --output ~/Pictures/JPG

# Delete originals only after successful conversion
uvx --from git+https://github.com/iancleary/heic2jpg.git heic2jpg ~/Pictures --delete-originals
```

## Install for repeated use

```bash
uv tool install git+https://github.com/iancleary/heic2jpg.git
heic2jpg /path/to/heic/files
```

To upgrade later:

```bash
uv tool upgrade heic2jpg
```

## Development

```bash
git clone https://github.com/iancleary/heic2jpg.git
cd heic2jpg
uv sync --dev
uv run heic2jpg --help
uv run pytest
uv run ruff check .
```

## Command-line options

| Option | Description |
| --- | --- |
| `heic_dir` | Directory containing HEIC/HEIF images. |
| `-q, --quality` | Output JPG image quality from 1 to 100. Default: `90`. |
| `-w, --workers` | Number of parallel conversion workers. Default: `4`. |
| `-o, --output` | Output directory. Default: `ConvertedFiles` inside the source directory. |
| `-r, --recursive` | Find HEIC/HEIF files recursively and preserve folder hierarchy. |
| `--resize WIDTHxHEIGHT` | Resize images before saving, for example `1920x1080`. |
| `-d, --delete-originals` | Delete originals after successful conversion. |
| `--replace-output` | Delete and recreate the output directory before converting. |
| `-v, --verbose` | Enable verbose logging. |

## Notes

- HEIC/HEIF support is provided by [`pillow-heif`](https://pypi.org/project/pillow-heif/).
- JPG metadata preservation uses EXIF data exposed by Pillow when present.
- JPEG cannot store alpha channels, so images with alpha are converted to RGB before saving.

# heic2jpg

A small, `uv`-friendly command-line tool for converting HEIC/HEIF images to JPG.

This is a modern Python packaging port inspired by [`dragonGR/PyHEIC2JPG`](https://github.com/dragonGR/PyHEIC2JPG). It keeps the same useful workflow—batch conversion, recursive mode, custom output directories, resizing, parallel workers, and EXIF preservation—while packaging it as an installable CLI with a `pyproject.toml`.

## Dependency policy

`heic2jpg` intentionally pins runtime dependencies exactly and does not update dependencies just because newer versions exist. Dependency updates require a concrete user bug, relevant security advisory, platform break, or specific upstream commit that matters for this tool's HEIC/HEIF-to-JPG conversion path.

See [`DEPENDENCY_POLICY.md`](DEPENDENCY_POLICY.md) for the full policy.

## Install as a uv tool

Install the latest release once to create a persistent `heic2jpg` executable on your `PATH`:

```bash
uv tool install git+https://github.com/iancleary/heic2jpg.git
```

For a reproducible install pinned to the `v0.2.0` release tag:

```bash
uv tool install git+https://github.com/iancleary/heic2jpg.git@v0.2.0
```

Then run the installed tool without re-downloading from GitHub on every invocation:

```bash
heic2jpg /path/to/heic/files
```

To upgrade later:

```bash
uv tool upgrade heic2jpg
```

## Run once with `uvx` from GitHub

Use `uvx` when you want a one-shot run without installing a persistent executable:

```bash
uvx --from git+https://github.com/iancleary/heic2jpg.git heic2jpg /path/to/heic/files
```

Pinned one-shot run from the `v0.2.0` release tag:

```bash
uvx --from git+https://github.com/iancleary/heic2jpg.git@v0.2.0 heic2jpg /path/to/heic/files
```

`uvx` may reuse uv's cache, but it is still a run command rather than a durable tool install. Prefer `uv tool install` for repeated use.

Useful examples after installing with `uv tool install`:

```bash
# Convert HEIC/HEIF files in one directory into ./ConvertedFiles
heic2jpg ~/Pictures

# Preserve subdirectories while recursively converting
heic2jpg ~/Pictures --recursive

# Choose quality, parallel workers, output folder, and resize
heic2jpg ~/Pictures \
  --quality 92 \
  --workers 8 \
  --recursive \
  --resize 1920x1080 \
  --output ~/Pictures/JPG

# Delete originals only after successful conversion
heic2jpg ~/Pictures --delete-originals
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

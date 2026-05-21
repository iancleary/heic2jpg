# Dependency Policy

`heic2jpg` follows a conservative dependency policy: dependencies are pinned, updates are intentional, and churn is treated as supply-chain risk.

## Principles

- Runtime dependencies are pinned exactly in `pyproject.toml`.
- Development dependencies are pinned exactly for repeatable local validation and release builds.
- `uv.lock` is committed and refreshed only when dependency pins intentionally change.
- Dependencies are not updated just because newer versions exist.
- Dependabot/Renovate-style routine bump PRs are intentionally avoided for this project.
- Forking is an available escalation path, not the default first step for native image-processing libraries.

## Current runtime dependency set

`heic2jpg` intentionally keeps a very small runtime dependency graph:

```text
heic2jpg
├── pillow==12.2.0
└── pillow-heif==1.3.0
    └── pillow==12.2.0
```

## When to update

Only update a dependency when there is a concrete reason, such as:

1. A user-impacting bug fixed by a specific upstream commit.
2. A relevant security advisory or CVE that affects this project's actual use case.
3. A platform compatibility break for users.
4. A specific upstream change that materially improves this tool's HEIC/HEIF-to-JPG conversion path.

If there is no compelling upstream commit or advisory, do not update.

## Required review before updating

Before changing any dependency pin:

1. Identify the exact upstream commit, release note, advisory, or user bug that justifies the update.
2. Inspect the upstream changelog and commits between the current pinned version and the proposed version.
3. Inspect the full transitive dependency set for changes.
4. Verify that the change matters for `heic2jpg`'s use case.
5. Run the full local validation suite:

   ```bash
   uv lock
   uv run ruff format --check .
   uv run ruff check .
   uv run pytest
   uv run python -m build
   uv tool install --force .
   heic2jpg --help
   uv tool uninstall heic2jpg
   ```

6. Document the reason in the commit message or PR body with the specific commit/advisory/user bug.

## Forking escalation

Fork a dependency only when pinning is no longer sufficient, for example:

- Upstream becomes unmaintained or compromised.
- The project needs a small patch that upstream will not accept quickly.
- A dependency grows functionality or transitive dependencies that are unnecessary for `heic2jpg`.
- A fork lets us trim or audit the actual code path used by this tool.

If forking, pin to an immutable commit or release tag from the fork and document what was trimmed or patched.

## Security monitoring

Security advisories should be reviewed for applicability to this tool's actual behavior. A broad advisory on image parsing is worth attention; an issue in an unused code path may not require immediate churn. The burden of proof is on the dependency update: show the commit we need.

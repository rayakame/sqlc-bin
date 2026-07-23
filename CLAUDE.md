# CLAUDE.md

pip-installable distribution of the official [sqlc](https://github.com/sqlc-dev/sqlc) release binaries. Each platform gets its own wheel with the binary bundled; installing it puts `sqlc` on PATH with no Go toolchain needed.

## Architecture

- `hatch_build.py` — hatchling build hook, the core of the project. On wheel builds it downloads the sqlc release archive for the target platform, verifies its sha256 against `checksums.json`, extracts the binary into the wheel (`sqlc_bin/bin/sqlc[.exe]`), and sets the platform wheel tag. Target selection: `SQLC_BIN_TARGET` env var (e.g. `linux_amd64`), host platform if unset (that's the sdist-fallback path).
- `checksums.json` — pinned sha256 per release asset. A build with no pinned hash fails on purpose (supply-chain guard); `scripts/bump_sqlc.py` adds hashes for new releases.
- `src/sqlc_bin/__init__.py` — launcher: `os.execv` on POSIX (process is replaced; signals/exit codes pass through), `subprocess.call` on Windows.
- `.github/workflows/` — `ci.yml` (build + smoke test per OS), `release.yml` (sdist + all 6 wheels on one Linux runner, smoke test on real runners, `uv publish` via trusted publishing on `v*` tags), `bump.yml` (daily check for new sqlc releases, opens a bump PR).

## Rules

- Use **uv** for everything: `uv build`, `uv pip`, `uv run`, `uv publish`. Never invoke pip, build, twine, or the hatch CLI directly. hatchling stays as the build *backend* — `uv_build` can't do custom hooks or platform-tagged wheels.
- The package version **tracks the sqlc version** (`1.31.1` ships sqlc v1.31.1). Packaging-only fixes get a `.postN` suffix, never a version of their own.
- Version bumps go through `scripts/bump_sqlc.py` so `pyproject.toml` and `checksums.json` stay in sync — don't edit the version by hand.
- Downloaded archives are cached in `.sqlc-cache/` (gitignored). Safe to delete.

## Commands

```sh
uv sync                                          # dev environment
uv build --wheel                                 # wheel for the host platform
SQLC_BIN_TARGET=windows_arm64 uv build --wheel   # cross-build any target
uv run pytest                                    # tests skip unless a built wheel is installed
uv run --no-project scripts/bump_sqlc.py         # update to latest sqlc release
```

Full verification loop: build the wheel, `uv pip install` it into a fresh venv, then run `sqlc version` and pytest there — tests are written against an *installed* wheel, not the source tree.

## Releasing

1. Merge the bump PR (or run `uv run --no-project scripts/bump_sqlc.py` manually).
2. Tag `v<version>` and push the tag — `release.yml` builds, smoke-tests all six platforms, and publishes to PyPI.

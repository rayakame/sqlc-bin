# sqlc-bin

[sqlc](https://sqlc.dev) as a pip-installable package. Installs the **official sqlc release binaries** — no Go toolchain required.

[sqlc](https://github.com/sqlc-dev/sqlc) generates fully type-safe code from SQL. This package exists so Python projects (and anyone without Go installed) can get the `sqlc` CLI straight from PyPI and pin it like any other dependency.

## Installation

```sh
# with uv
uv add --dev sqlc-bin        # as a project dev dependency
uv tool install sqlc-bin     # as a global tool

# with pip
pip install sqlc-bin

# with pipx
pipx install sqlc-bin

# run without installing
uvx --from sqlc-bin sqlc version
```

## Usage

Exactly like a `go install`ed sqlc — the `sqlc` command is on your PATH:

```sh
sqlc version
sqlc init
sqlc generate
```

It also works as a Python module:

```sh
python -m sqlc_bin generate
```

See the [sqlc documentation](https://docs.sqlc.dev) for everything the CLI can do.

## Supported platforms

| OS      | x86_64 | arm64 |
| ------- | :----: | :---: |
| Linux (glibc and musl) | ✅ | ✅ |
| macOS 11+ | ✅ | ✅ |
| Windows | ✅ | ✅ |

Each platform gets its own wheel with the matching binary inside; pip/uv picks the right one automatically. On any other platform, installation falls back to the sdist, which downloads the binary for the host at build time (and fails clearly if sqlc doesn't publish one).

## How it works

- Wheels bundle the **unmodified official binaries** from [sqlc's GitHub releases](https://github.com/sqlc-dev/sqlc/releases).
- Every downloaded archive is verified against sha256 checksums pinned in [`checksums.json`](checksums.json) before packaging.
- The `sqlc` entry point `exec`s the bundled binary (POSIX) or forwards to it as a subprocess (Windows), so arguments, stdio, exit codes, and signals behave like the real thing — because it is the real thing.

## Versioning

The package version tracks the sqlc version: `sqlc-bin==1.31.1` ships sqlc `v1.31.1`. Packaging-only fixes are published as post-releases (`1.31.1.post1`) containing the same binary.

## Development

```sh
uv sync                                          # set up the dev environment
uv build --wheel                                 # build a wheel for your platform
SQLC_BIN_TARGET=windows_arm64 uv build --wheel   # cross-build for another target
uv run --with dist/*.whl pytest                  # tests run against an installed wheel
uv run --no-project scripts/bump_sqlc.py         # update to the latest sqlc release
```

Releases are built and published to PyPI by GitHub Actions (`.github/workflows/release.yml`) on version tags, using trusted publishing. A daily workflow checks for new sqlc releases and opens a bump PR.

## License

This packaging project is MIT-licensed. sqlc itself is [MIT-licensed](https://github.com/sqlc-dev/sqlc/blob/main/LICENSE) by its authors; the binaries are redistributed unmodified. This project is not affiliated with or endorsed by the sqlc authors.

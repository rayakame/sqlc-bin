# sqlc-bin

**Unofficial.** This is a community-maintained packaging project. It is not affiliated with or endorsed by the sqlc authors. Please file issues about this package [here](https://github.com/rayakame/sqlc-bin/issues), not against [sqlc-dev/sqlc](https://github.com/sqlc-dev/sqlc).

[sqlc](https://sqlc.dev) as a pip-installable package. Ships the unmodified upstream release binaries, so no Go toolchain is required.

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

Exactly like a `go install`ed sqlc: the `sqlc` command is on your PATH.

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

- Wheels bundle the unmodified binaries from [sqlc's GitHub releases](https://github.com/sqlc-dev/sqlc/releases). Nothing is rebuilt, patched, or recompiled.
- Every downloaded archive is verified against sha256 checksums pinned in [`checksums.json`](checksums.json) before packaging.
- The `sqlc` entry point `exec`s the bundled binary

## License

The packaging code in this repository is MIT-licensed ([`LICENSE`](LICENSE)).

sqlc itself is a separate project by its own authors, licensed under the MIT
license — see [`LICENSE-sqlc`](LICENSE-sqlc) (Copyright (c) Riza, Inc.), which
covers the bundled binaries and is shipped inside every wheel. "sqlc" is the
name of the upstream project; this package is not affiliated with, endorsed
by, or sponsored by the sqlc authors.

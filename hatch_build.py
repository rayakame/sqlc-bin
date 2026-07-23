"""Hatchling build hook that packs the official sqlc binary into the wheel.

Wheel builds download the sqlc release archive for the target platform,
verify its sha256 against checksums.json, and inject the binary into the
wheel as ``sqlc_bin/bin/sqlc`` (``sqlc.exe`` on Windows) with the matching
platform tag.

The target is chosen by the ``SQLC_BIN_TARGET`` environment variable
(e.g. ``SQLC_BIN_TARGET=darwin_arm64``); when unset the host platform is
detected, which is what happens when pip/uv falls back to building from
the sdist.
"""

from __future__ import annotations

import hashlib
import json
import os
import platform
import shutil
import tarfile
import urllib.request
import zipfile
from pathlib import Path

from hatchling.builders.hooks.plugin.interface import BuildHookInterface

DOWNLOAD_URL = "https://github.com/sqlc-dev/sqlc/releases/download/v{version}/{asset}"

# The sqlc release binaries are pure-Go and statically linked, so the Linux
# wheels are valid for both glibc (manylinux) and musl (musllinux) systems.
TARGETS = {
    "linux_amd64": ("tar.gz", "manylinux_2_17_x86_64.manylinux2014_x86_64.musllinux_1_1_x86_64"),
    "linux_arm64": ("tar.gz", "manylinux_2_17_aarch64.manylinux2014_aarch64.musllinux_1_1_aarch64"),
    "darwin_amd64": ("tar.gz", "macosx_11_0_x86_64"),
    "darwin_arm64": ("tar.gz", "macosx_11_0_arm64"),
    "windows_amd64": ("zip", "win_amd64"),
    "windows_arm64": ("zip", "win_arm64"),
}

_ARCH_ALIASES = {"x86_64": "amd64", "amd64": "amd64", "aarch64": "arm64", "arm64": "arm64"}


def detect_host_target() -> str:
    arch = _ARCH_ALIASES.get(platform.machine().lower())
    target = f"{platform.system().lower()}_{arch}"
    if target not in TARGETS:
        raise RuntimeError(
            f"sqlc publishes no binaries for this platform "
            f"({platform.system()} {platform.machine()}); "
            f"supported targets: {', '.join(sorted(TARGETS))}"
        )
    return target


class CustomBuildHook(BuildHookInterface):
    def initialize(self, version: str, build_data: dict) -> None:
        if self.target_name != "wheel":
            return

        target = os.environ.get("SQLC_BIN_TARGET") or detect_host_target()
        if target not in TARGETS:
            raise ValueError(
                f"unknown SQLC_BIN_TARGET {target!r}; expected one of {', '.join(sorted(TARGETS))}"
            )
        ext, wheel_tag = TARGETS[target]

        sqlc_version = self.metadata.version.split(".post")[0]
        asset = f"sqlc_{sqlc_version}_{target}.{ext}"
        binary_name = "sqlc.exe" if target.startswith("windows") else "sqlc"

        cache = Path(self.root) / ".sqlc-cache"
        archive = cache / asset
        if not archive.exists():
            cache.mkdir(exist_ok=True)
            partial = archive.with_name(archive.name + ".part")
            with urllib.request.urlopen(
                DOWNLOAD_URL.format(version=sqlc_version, asset=asset), timeout=60
            ) as resp, open(partial, "wb") as f:
                shutil.copyfileobj(resp, f)
            partial.replace(archive)
        self._verify(archive, sqlc_version, asset)

        binary = cache / target / binary_name
        binary.parent.mkdir(exist_ok=True)
        self._extract(archive, binary_name, binary)
        binary.chmod(0o755)

        build_data["pure_python"] = False
        build_data["infer_tag"] = False
        build_data["tag"] = f"py3-none-{wheel_tag}"
        build_data["force_include"][str(binary)] = f"sqlc_bin/bin/{binary_name}"

    def _verify(self, archive: Path, sqlc_version: str, asset: str) -> None:
        checksums = json.loads((Path(self.root) / "checksums.json").read_text())
        expected = checksums.get(sqlc_version, {}).get(asset)
        if expected is None:
            raise RuntimeError(
                f"no pinned sha256 for {asset} in checksums.json; "
                "run scripts/bump_sqlc.py to pin it"
            )
        digest = hashlib.sha256(archive.read_bytes()).hexdigest()
        if digest != expected:
            archive.unlink()  # drop the bad download so a rebuild re-fetches
            raise RuntimeError(
                f"sha256 mismatch for {asset}: expected {expected}, got {digest}"
            )

    @staticmethod
    def _extract(archive: Path, binary_name: str, dest: Path) -> None:
        if archive.name.endswith(".zip"):
            with zipfile.ZipFile(archive) as zf:
                member = next(
                    n for n in zf.namelist() if n.rsplit("/", 1)[-1] == binary_name
                )
                dest.write_bytes(zf.read(member))
        else:
            with tarfile.open(archive) as tf:
                member = next(
                    m for m in tf.getmembers()
                    if m.isfile() and m.name.rsplit("/", 1)[-1] == binary_name
                )
                dest.write_bytes(tf.extractfile(member).read())

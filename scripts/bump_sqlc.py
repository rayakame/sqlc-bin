#!/usr/bin/env python3
"""Update the package to the latest sqlc release.

Fetches the latest release tag from GitHub, downloads all release archives,
pins their sha256 hashes in checksums.json, and sets the package version in
pyproject.toml. No-op when already up to date.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
API_LATEST = "https://api.github.com/repos/sqlc-dev/sqlc/releases/latest"
DOWNLOAD_URL = "https://github.com/sqlc-dev/sqlc/releases/download/v{version}/{asset}"
ASSETS = [
    "sqlc_{version}_linux_amd64.tar.gz",
    "sqlc_{version}_linux_arm64.tar.gz",
    "sqlc_{version}_darwin_amd64.tar.gz",
    "sqlc_{version}_darwin_arm64.tar.gz",
    "sqlc_{version}_windows_amd64.zip",
    "sqlc_{version}_windows_arm64.zip",
]


def main() -> int:
    with urllib.request.urlopen(API_LATEST) as resp:
        latest = json.load(resp)["tag_name"].lstrip("v")

    pyproject = ROOT / "pyproject.toml"
    text = pyproject.read_text()
    current = re.search(r'^version = "([^"]+)"', text, flags=re.M).group(1)
    if current.split(".post")[0] == latest:
        print(f"already at sqlc {latest}")
        return 0

    checksums_path = ROOT / "checksums.json"
    checksums = json.loads(checksums_path.read_text())
    cache = ROOT / ".sqlc-cache"
    cache.mkdir(exist_ok=True)
    entry = {}
    for template in ASSETS:
        asset = template.format(version=latest)
        print(f"hashing {asset} ...")
        with urllib.request.urlopen(DOWNLOAD_URL.format(version=latest, asset=asset)) as resp:
            data = resp.read()
        (cache / asset).write_bytes(data)
        entry[asset] = hashlib.sha256(data).hexdigest()
    checksums[latest] = entry
    checksums_path.write_text(json.dumps(checksums, indent=2, sort_keys=True) + "\n")

    pyproject.write_text(text.replace(f'version = "{current}"', f'version = "{latest}"', 1))
    print(f"updated {current} -> {latest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import requests

PKG_RE = re.compile(r"package:\s+name='([^']+)'")
LABEL_RE = re.compile(r"application-label(?:-[^:]+)?:'([^']+)'")

@dataclass
class ApkInfo:
    asset_name: str
    app_name: str
    package_id: str
    size_bytes: int
    download_url: str


def find_aapt() -> str:
    env_path = os.environ.get("AAPT_PATH")
    if env_path and Path(env_path).exists():
        return env_path

    for candidate in ("aapt", "aapt.exe"):
        found = shutil.which(candidate)
        if found:
            return found

    raise SystemExit(
        "aapt not found. Install Android build-tools and set AAPT_PATH, "
        "or put aapt on PATH."
    )


def github_session(token: Optional[str]) -> requests.Session:
    s = requests.Session()
    s.headers.update({"Accept": "application/vnd.github+json"})
    if token:
        s.headers.update({"Authorization": f"Bearer {token}"})
    return s


def get_release(session: requests.Session, repo: str, release: str) -> dict:
    if release == "latest":
        url = f"https://api.github.com/repos/{repo}/releases/latest"
    else:
        url = f"https://api.github.com/repos/{repo}/releases/tags/{release}"

    r = session.get(url, timeout=60)
    r.raise_for_status()
    return r.json()


def download_file(session: requests.Session, url: str, out_path: Path) -> None:
    with session.get(url, stream=True, timeout=300) as r:
        r.raise_for_status()
        with out_path.open("wb") as f:
            for chunk in r.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    f.write(chunk)


def extract_badging(aapt: str, apk_path: Path) -> tuple[str, str]:
    proc = subprocess.run(
        [aapt, "dump", "badging", str(apk_path)],
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or f"aapt failed on {apk_path.name}")

    stdout = proc.stdout
    pkg_match = PKG_RE.search(stdout)
    if not pkg_match:
        raise RuntimeError(f"Could not find package name in {apk_path.name}")

    label_match = LABEL_RE.search(stdout)
    package_id = pkg_match.group(1)
    app_name = label_match.group(1) if label_match else apk_path.stem

    return app_name, package_id


def markdown_table(rows: list[ApkInfo], repo: str, release: str) -> str:
    lines = []
    lines.append(f"# APK package IDs for `{repo}`")
    lines.append("")
    lines.append(f"Release source: `{release}`")
    lines.append("")
    lines.append("| App name | Asset file | Package ID | Size |")
    lines.append("|---|---|---:|---:|")
    for row in rows:
        size_mb = row.size_bytes / (1024 * 1024)
        lines.append(
            f"| {row.app_name} | `{row.asset_name}` | `{row.package_id}` | {size_mb:.1f} MB |"
        )
    lines.append("")
    lines.append(f"_Generated automatically from GitHub release assets._")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Download APK assets from a GitHub release and extract package IDs."
    )
    parser.add_argument("--repo", required=True, help="owner/repo")
    parser.add_argument(
        "--release",
        default="latest",
        help="Release tag name or 'latest' (default: latest)",
    )
    parser.add_argument(
        "--output",
        default="apk-package-ids.md",
        help="Markdown output path",
    )
    parser.add_argument(
        "--keep-downloads",
        action="store_true",
        help="Keep downloaded APKs in ./downloads",
    )
    args = parser.parse_args()

    token = os.environ.get("GITHUB_TOKEN")
    session = github_session(token)
    release_data = get_release(session, args.repo, args.release)

    assets = release_data.get("assets", [])
    apk_assets = [
        a for a in assets
        if a.get("name", "").lower().endswith(".apk")
    ]

    if not apk_assets:
        print("No APK assets found in this release.", file=sys.stderr)
        return 1

    aapt = find_aapt()

    download_dir = Path("downloads")
    tmp_dir_obj = None
    if args.keep_downloads:
        download_dir.mkdir(parents=True, exist_ok=True)
    else:
        tmp_dir_obj = tempfile.TemporaryDirectory()
        download_dir = Path(tmp_dir_obj.name)

    results: list[ApkInfo] = []

    try:
        for asset in sorted(apk_assets, key=lambda x: x["name"].lower()):
            asset_name = asset["name"]
            url = asset["browser_download_url"]
            out_path = download_dir / asset_name

            print(f"Downloading {asset_name}...")
            download_file(session, url, out_path)

            print(f"Extracting package ID from {asset_name}...")
            app_name, package_id = extract_badging(aapt, out_path)

            results.append(
                ApkInfo(
                    asset_name=asset_name,
                    app_name=app_name,
                    package_id=package_id,
                    size_bytes=int(asset.get("size", out_path.stat().st_size)),
                    download_url=url,
                )
            )

    finally:
        if tmp_dir_obj is not None:
            tmp_dir_obj.cleanup()

    md = markdown_table(results, args.repo, args.release)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(md, encoding="utf-8")

    print(f"Wrote {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
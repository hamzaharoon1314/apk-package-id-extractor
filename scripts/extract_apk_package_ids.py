#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import time
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

        total = int(r.headers.get("content-length", 0))
        downloaded = 0

        with out_path.open("wb") as f:

            for chunk in r.iter_content(chunk_size=1024 * 1024):

                if chunk:

                    f.write(chunk)

                    downloaded += len(chunk)

                    if total > 0:

                        percent = downloaded / total * 100

                        print(
                            f"\r{out_path.name}: "
                            f"{downloaded // (1024*1024)}MB / "
                            f"{total // (1024*1024)}MB "
                            f"({percent:.1f}%)",
                            end="",
                            flush=True
                        )

        print()


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

def sanitize_filename(name: str) -> str:
    return name.replace("/", "__").replace("\\", "__")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Download APK assets from a GitHub release and extract package IDs."
    )

    parser.add_argument(
        "--repo",
        help="GitHub repo in owner/repo format"
    )

    parser.add_argument(
        "--release",
        default="latest",
        help="Release tag name or 'latest'"
    )

    parser.add_argument(
        "--keep-downloads",
        action="store_true",
        help="Keep downloaded APKs"
    )

    args = parser.parse_args()

    # Ask interactively if not provided
    repo = args.repo

    if not repo:
        repo = input("Enter GitHub repo (owner/repo): ").strip()

    if "/" not in repo:
        print("Invalid repo format. Example: ReVanced/revanced-manager")
        return 1

    safe_repo_name = sanitize_filename(repo)

    # Auto-generate markdown filename
    output_path = Path("docs") / f"{safe_repo_name}.md"

    token = os.environ.get("GITHUB_TOKEN")
    session = github_session(token)

    print(f"Fetching release data for {repo}...")
    release_data = get_release(session, repo, args.release)

    assets = release_data.get("assets", [])

    apk_assets = [
        a for a in assets
        if a.get("name", "").lower().endswith(".apk")
    ]

    if not apk_assets:
        print("No APK assets found.")
        return 1

    aapt = find_aapt()

    download_dir = Path("downloads")
    tmp_dir_obj = None

    if args.keep_downloads:
        download_dir.mkdir(parents=True, exist_ok=True)
    else:
        tmp_dir_obj = tempfile.TemporaryDirectory()
        download_dir = Path(tmp_dir_obj.name)

    results = []

    try:
        for asset in sorted(apk_assets, key=lambda x: x["name"].lower()):

            asset_name = asset["name"]
            url = asset["browser_download_url"]

            out_path = download_dir / asset_name

            start = time.time()
            print(f"\nDownloading: {asset_name}", flush=True)

            download_file(session, url, out_path)

            
            print(f"Extracting package ID...", flush=True)

            try:
                app_name, package_id = extract_badging(aapt, out_path)

                results.append(
                    ApkInfo(
                        asset_name=asset_name,
                        app_name=app_name,
                        package_id=package_id,
                        size_bytes=int(asset.get("size", 0)),
                        download_url=url,
                    )
                )
                
                elapsed = time.time() - start
                print(f"✓ {package_id} ({elapsed:.2f}s)", flush=True)

            except Exception as e:
                print(f"✗ Failed: {e}", flush=True)

    finally:
        if tmp_dir_obj is not None:
            tmp_dir_obj.cleanup()

    md = markdown_table(results, repo, args.release)

    output_path.parent.mkdir(parents=True, exist_ok=True)

    output_path.write_text(md, encoding="utf-8")

    print(f"\nMarkdown updated:")
    print(output_path)

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
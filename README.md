# APK Package ID Extractor

Automatically download APK assets from GitHub Releases, extract Android package IDs using `aapt`, and generate Markdown documentation for every scanned repository.

This project is designed for repositories that publish APKs but do not provide package names / application IDs.

---

# Features

- Downloads all `.apk` assets from a GitHub release
- Extracts:
  - Package ID
  - App name
  - APK filename
  - File size
- Generates Markdown docs automatically
- Updates existing repo docs automatically
- GitHub Actions support
- No local Android SDK setup required for users
- Supports any public GitHub repo with APK releases

---

# Example Output

| App name | Asset file | Package ID |
|---|---|---|
| Instagram | instagram-arm64-v8a.apk | com.instagram.android |
| Discord | discord-revenge.apk | com.discord |
| Duolingo | duolingo-revanced.apk | com.duolingo |

---

# Generated Documentation

All extracted package lists are stored inside:

```text
/docs
```

You can browse all generated package lists here:

```text
https://github.com/YOUR_USERNAME/YOUR_REPO/tree/main/docs
```

Example generated file:

```text
docs/NoName-exe__revanced-extended.md
```

---

# How It Works

1. GitHub Actions runs the Python script
2. Script fetches release assets from a target repo
3. APKs are downloaded temporarily
4. `aapt dump badging` extracts package IDs
5. Markdown documentation is generated
6. Docs are committed back automatically

---

# Requirements

Users only need:

- A GitHub account
- Forked repository
- GitHub Actions enabled

No local setup required if using GitHub Actions.

---

# Setup Guide

## 1. Fork This Repository

Click:

```text
Fork
```

at the top-right of this repository.

This creates your own copy.

---

## 2. Enable GitHub Actions

Inside your fork:

```text
Actions → Enable Workflows
```

---

## 3. Run The Extractor

Go to:

```text
Actions
```

Select:

```text
Update APK package IDs
```

Click:

```text
Run workflow
```

---

## 4. Enter Repository Name

Use format:

```text
OWNER/REPO
```

Example:

```text
NoName-exe/revanced-extended
```

NOT:

```text
https://github.com/OWNER/REPO
```

---

## 5. Optional Release Tag

You may specify:

```text
latest
```

or a specific tag:

```text
v1.2.3
```

---

# Output Files

Generated markdown files are stored in:

```text
/docs
```

File naming format:

```text
OWNER__REPO.md
```

Example:

```text
NoName-exe__revanced-extended.md
```

---

# Updating Existing Files

Running the workflow again for the same repo:

- Updates the existing markdown file
- Replaces outdated package IDs
- Adds newly released APKs

---

# Supported APK Sources

Works with repositories that publish APKs through:

- GitHub Releases
- Release Assets

---

# Local Usage (Optional)

Advanced users may run locally.

## Install Requirements

### Python

Install:

```text
Python 3.10+
```

### Android Build Tools

Install Android SDK Build Tools containing:

```text
aapt
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Run Script

```bash
python scripts/extract_apk_package_ids.py
```

Example:

```bash
python scripts/extract_apk_package_ids.py \
  --repo "NoName-exe/revanced-extended"
```

---

# Repository Structure

```text
.
├── .github/workflows/
│   └── update-apk-package-ids.yml
├── docs/
├── scripts/
│   └── extract_apk_package_ids.py
├── requirements.txt
└── README.md
```

---

# How Package IDs Are Extracted

Uses:

```bash
aapt dump badging app.apk
```

Example output:

```text
package: name='com.instagram.android'
```

This reads the Android manifest directly from the APK.

---

# Why This Exists

Many APK release repositories publish modified APKs without package IDs.

This tool helps users:

- Verify package names
- Identify spoofed apps
- Create automation scripts
- Build APK indexes
- Support package manager tooling

---

# Possible Future Features

- SHA256 export
- JSON output
- HTML website generation
- APK icon extraction
- Play Store links
- Multi-release scanning
- VirusTotal integration
- Telegram/Discord notifications
- Parallel downloads

---

# Contributing

Pull requests are welcome.

Ideas, fixes, and optimizations are appreciated.

---

# Disclaimer

This repository does not host APKs permanently.

APK files are downloaded temporarily during processing.

All rights belong to their respective owners.

---

# License

MIT License
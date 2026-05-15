# APK Package ID & Config Extractor

Automatically scan GitHub release APKs, extract Android package IDs, and generate ready-to-use configs for Discoverium and Obtainium.

The workflow downloads APK assets from a GitHub release, extracts metadata using `aapt`, and publishes:
- Package IDs
- App metadata
- SHA256 hashes
- App icons
- Discoverium/Obtainium configs

> [!IMPORTANT]
> Looking for generated APK package IDs, Discoverium configs, Obtainium-compatible JSON, and tracked repositories?
>
> Go to:
>
> [`docs/README.md`](./docs/README.md)
>
> This index contains all scanned repositories with direct links to generated metadata pages and configs.

---

# Features

- Extract package IDs from APK files
- Generate Discoverium configs
- Generate Obtainium-compatible JSON
- Extract APK icons
- Generate markdown app index
- SHA256 hashing
- Parallel APK processing
- Automatic GitHub Actions workflow
- Supports large APK release repositories

---

# Output Structure

```text
docs/
├── repo-name.md
├── json/
├── discoverium/
└── icons/
```

---

# Generated Data

Each scanned APK includes:
- App name
- Package ID
- APK filename
- Version
- SHA256
- Play Store link
- Discoverium/Obtainium config

---

# How It Works

1. Enter a GitHub repository
2. Workflow downloads release APKs
3. APK metadata is extracted using `aapt`
4. Configs and markdown files are generated automatically
5. Results are pushed to the repository

## 1. Run The Workflow

Open:

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

## 2. Enter Repository

Use format:

```text
OWNER/REPO
```

Example:

```text
NoName-Person/repoName
```

# Example Use Cases

- APK package identification
- Discoverium repositories
- Obtainium sources
- APK metadata indexing
- Android app tracking
- Modded APK repositories
- Automation workflows

---

# Notes

- APKs are downloaded temporarily during processing
- XML adaptive icons are skipped automatically
- Only public GitHub repositories are supported

---

# License

MIT
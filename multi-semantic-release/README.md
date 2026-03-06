# Multi Semantic Release (POC)

A proof-of-concept for running independent semantic versioning across multiple projects in a monorepo.

Built on top of `python-semantic-release==8.1.1` internals. May not be compatible with newer versions — the library's internal APIs changed significantly across minor versions.

## The Problem

`python-semantic-release` is designed for single-project repos. In a monorepo with multiple independently-deployable services, you want each project to:
- Have its own version tag (e.g. `project_1_2023.10.18513`)
- Generate its own `CHANGELOG.md`
- Release independently based on which files changed

## How It Works

`semantic-release.py` wraps `python-semantic-release` internals to:
1. Filter git commits by Angular commit scope (e.g. `feat(project_1): ...`)
2. Compute the next version using **CalVer** (`year.month.dayhourminute`)
3. Update `pyproject.toml`, generate `CHANGELOG.md`, commit, tag, push, and create a GitHub release

The GitHub Actions workflow detects which project directories changed and runs the release script only for those.

## Usage

```bash
poetry install

# Dry run — print next version only
poetry run python semantic-release.py --project=project_1 --project_path=app/project_1 --print_only=true

# Full release
poetry run python semantic-release.py --project=project_1 --project_path=app/project_1
```

## Structure

```
.
├── semantic-release.py         # Core release script
├── app/
│   ├── project_1/              # Sample project 1
│   │   ├── pyproject.toml
│   │   └── CHANGELOG.md
│   └── project_2/              # Sample project 2
│       ├── pyproject.toml
│       └── CHANGELOG.md
└── .github/workflows/
    └── test-semantic.yml       # CI: detect changed dirs, release accordingly
```

## Status

POC — built and tested in 2023. The core idea works but the implementation hooks into `python-semantic-release` private APIs which may have shifted.

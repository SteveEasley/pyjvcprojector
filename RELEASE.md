# Release Process

This project publishes to PyPI using GitHub Actions and Trusted Publishing.

## Prerequisites

- PyPI project has a Trusted Publisher configured for this repository and workflow:
  - Repository: `SteveEasley/pyjvcprojector`
  - Workflow: `publish.yml`
  - Environment: none

## Create a New Release

1. Update package version in `jvcprojector/__init__.py`:
   - Set `__version__ = "X.Y.Z"` (example: `2.0.7`).
2. Run quality checks locally:
   - `uv run prek run --all-files`
   - `uv run pytest`
3. Optionally validate the build with `uv build`.
4. Commit and push the version bump (and any release notes/changelog updates) to `main`.
5. Create and publish a GitHub release:
   - Tag must be `vX.Y.Z` (example: `v2.0.7`).
   - Target branch: `main`.

## What Happens Automatically

Publishing the GitHub release triggers `.github/workflows/publish.yml`, which:

1. Checks out the repository.
2. Verifies release tag version matches `jvcprojector.__version__`:
   - `v2.0.7` tag must match `__version__ = "2.0.7"`.
3. Builds the package (`sdist` + wheel) with `uv build`.
4. Publishes artifacts to PyPI via OIDC Trusted Publishing, which also verifies their metadata.

## Verification

- Confirm the GitHub Actions workflow succeeded.
- Confirm the new version appears on PyPI.
- Optional smoke test in a clean environment:
  - `pip install -U pyjvcprojector==X.Y.Z`

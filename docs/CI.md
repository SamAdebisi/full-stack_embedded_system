# file: docs/CI.md
## GitHub Actions
- `ci.yml` runs on PRs and pushes to `main`. Lints, type-checks, tests, and Docker-builds.
- `release.yml` publishes multi-arch images to GHCR with tags `<tag>` and `latest`.


### Usage
```bash
git tag v1.0.0 && git push origin v1.0.0
# Retired assembly pipeline

Historical chunks and patch scripts are retained for provenance only. They are NOT inputs to the release builder. Their hard-coded paths belong to the former pipeline; do not run them against the current release.

The workflow on `main` previously assembled only a subset of newer features. The consolidation baseline was captured from the complete release `2524f10`, rather than attempting to reconstruct it with that stale workflow.

Current sources live in `../src`, the weapon catalog in `../data`, and the build command is documented in `../MAINTENANCE.md`. Edit those files for future changes.

# Historical navigation experiments

These three tests failed against release `2524f10` before consolidation. They assert mutually incompatible, superseded DOM structures (a body portal, persistent navigation cache, and unified viewport experiment). The current release does not contain those patches. They are preserved here for history, not silently skipped in the active runner.

Current navigation and rendering checks remain in `test-regression-invariants.py`, `test-final-release-invariants.py`, and `test-encounter-action-polish.py`. Offline journey tests cover the state transitions. These are not a replacement for real-device visual testing before future UI changes.

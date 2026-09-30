# Tarnished Covenant maintenance

## Build and verify

From the repository root, with Python 3.10+ and Node 20+:

```sh
python tarnished-covenant/tools/build.py --test
```

This command assembles the page, validates JavaScript, and runs all active offline checks. It does not contact Supabase or open a player room. No package installation is required.

For CI, check committed output without writing anything:

```sh
python tarnished-covenant/tools/build.py --check --test
```

The generated `index.html` and `regional-pools.js` belong in the same commit as their source changes. Build twice if investigating nondeterminism: the second build must produce no diff. Do not edit generated output directly.

## Authoritative files

| Work | Source |
| --- | --- |
| Page shell, script order, stylesheet links | `src/page.html` |
| Core styles | `src/styles.css` |
| Core gameplay and remaining older wrappers | `src/app.js` |
| Weapon draw rules and appeal memory | `src/systems/weapons.js` |
| Weapon region membership, acquisition requirements, calculator references | `data/weapons.json` |
| Imported regional boss lists | `data/boss-pools.json` |
| Gate table ordering/presentation only | `src/acquisition-gates.layout` |
| Boss progression | `src/systems/boss-prerequisites.js` |
| Shared persistence and recovery | `src/systems/shared-sync.js` |
| Two-world clears | `src/systems/world-clears.js` |
| Battle reports, rewards, Masterworks | Named files in `src/systems/` |
| Build UI and calculator | `build-lab.js`, `build-lab.css` |
| Official calculator records | `assets/build/weapon-data-v1.17.json.gz` |
| Regression and functional tests | Root `test-*` files and `tests/*.cjs` |

`{{src/...}}` and `{{generated/...}}` are build-time includes, not browser imports. They preserve the existing execution order and shared lexical scope. Splitting these files into ES modules would require a separate behavioral change and tests. The remaining wrapper layers have not been rewritten.

The `legacy/` directory is historical reference, not executable release input. Never add a new one-off patch there.

## Weapon catalog

Each weapon has a unique stable `id`, its existing display `name`, ordered region memberships, a `calculatorName`, and optional acquisition prerequisites. All memberships preserve current draw order and legacy labels (including the `(+8)` label). Gate layout placeholders reference IDs and contain no prerequisite values.

IDs are authoring identifiers only. Existing saved runs continue to store their original names and shapes; this consolidation introduces no save migration. The two endgame regions still inherit authored pools in `src/app.js`; compatibility tests cover them alongside the 20 imported pools. Legacy restoration code remains in `systems/weapons.js` for compatibility. Weapon type/skill/infusion metadata and regulation calculation records have not yet been merged into the catalog.

When adding a weapon: add its catalog record and region order, resolve its calculator reference, add a gate layout entry if gated, build, and run tests. Do not change IDs on a rename. For deliberate gameplay changes, update the release baseline only after reviewing the exact expected differences; never regenerate it merely to silence a failure.

## Saved-run safety

- Never reset, recreate, migrate, or write the live room to test an app change.
- Offline tests load the shipped JavaScript with startup disabled, blocked network access, synthetic room state, deterministic randomness, and an in-memory revisioned backend.
- `tests/release-baseline.json` contains only synthetic states plus public game data captured from commit `2524f10`; no user save or credentials.
- Compatibility checks protect region metadata/order, acquisition gates, seeded encounters, saved build levels, current assignments, progression, and unknown extension fields.
- Journey tests execute the real appeal, world-clear, report, payout, reconnect, conflict-retry, and Build saver code. They do not validate Supabase server configuration or real mobile rendering.
- `tcNormalizeRunState` remains the normalization boundary; `tcBlockingTransition` remains the screen priority boundary. Keep database functions, storage keys, player slot names, and persisted field meanings stable unless a separately reviewed migration is necessary.

## Release discipline

Read-only verification runs on source pushes and pull requests. The assembly workflow remains manual and does not write a player save. Before a future UI or runtime change, additionally test a disposable room on two devices. Never use the current real run for testing.

For changes users must download, update `TC_BUILD_ID` in the freshness-guard source and bump the Build Lab query versions in `src/page.html` if those assets changed; update corresponding version assertions. Commit sources and generated output together. This consolidation deliberately preserves the current release bytes and cache identifiers.

## Next consolidation steps

1. Replace one wrapper chain at a time with an explicit implementation, starting with shared actions; keep the current offline journeys as the safety net.
2. Move remaining weapon metadata into the catalog only after exact runtime equivalence checks are in place.
3. Unify picker, saving, locked-action, and confirmation presentation in a separately tested UI release.

The first consolidation is intentionally behavior-preserving. It does not claim to have redesigned the UI or tested real-device interactions.

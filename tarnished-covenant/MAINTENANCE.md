# Tarnished Covenant maintenance map

This app is assembled from source chunks, then patched in workflow order. The safest way to keep it maintainable is to avoid creating a new one-off patch for every late bug.

## Where new work belongs

- **Gameplay/data generation:** edit the relevant early feature patch (regions, Chaos, Rites, rewards, Smithing, etc.).
- **Presentation / phone information architecture:** `build-information-architecture.py`.
- **Cross-system state, transition priority, navigation, compatibility fixes, tiny final display invariants:** `build-regression-hardening.py` (the maintenance core).
- **Regression expectations / semantic data checks:** `test-regression-invariants.py`.

Do not edit generated `index.html` by itself. Every production change must be reproducible from the workflow.

## State boundary

`tcNormalizeRunState(state)` is the late-stage normalization boundary. New optional persisted collections or compatibility defaults should be normalized there instead of being independently reconstructed in region travel, rendering, or shared-state updates.

Smithing-specific normalization still lives in `smithingData(state)` and is called by the general normalizer.

## Transition boundary

`tcBlockingTransition(state)` is the authoritative priority list for screens/actions that must be completed before ordinary bottom navigation resumes.

Current priority:

1. Covenant reward reveal
2. Post-battle report
3. Mandatory Corporate / Bell Bearing paperwork
4. New encounter reveal

If a future system can interrupt normal navigation, add it there rather than adding another independent lock check.

## Navigation

Bottom navigation uses one delegated click listener installed by the final `bindNav` override. Do not add per-render bottom-nav listeners.

Feature-specific buttons may still use local listeners where convenient; migrate them to delegated `data-action` routing only when the surrounding screen is being substantially changed. Avoid refactors whose only benefit is stylistic.

## Build rules

Before shipping a structural change:

1. Run the full workflow from chunks through all patches.
2. `test-regression-invariants.py` must pass.
3. Final inline JavaScript must pass `node --check`.
4. Do not weaken a regression assertion just to get a build green; first determine whether the app or the assertion is wrong.
5. Keep the workflow `workflow_dispatch`-only outside temporary validation runs.

## Refactor philosophy

Prefer consolidation when touching an area already under active development, but do not rewrite stable systems merely to make them prettier internally. The regression suite exists so old override layers can be retired gradually and safely rather than through a risky full rewrite.

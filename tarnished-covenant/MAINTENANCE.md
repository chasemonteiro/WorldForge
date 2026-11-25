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
| App-wide visual theme (fonts, colours, icons, layout polish) | `src/theme.css` (loaded last, presentation only) |
| Presentation-only markup tweaks (nav labels, Ledger rows, boon help) | `src/systems/restyle.js` |
| Bundled typefaces | `assets/fonts/` (EB Garamond and Cinzel, SIL OFL; see `THIRD_PARTY_NOTICES.md`) |
| Official calculator records | `assets/build/weapon-data-v1.17.json.gz` |
| Regression and functional tests | Root `test-*` files and `tests/*.cjs` |

`{{src/...}}` and `{{generated/...}}` are build-time includes, not browser imports. They preserve the existing execution order and shared lexical scope. Splitting these files into ES modules would require a separate behavioral change and tests. The remaining wrapper layers have not been rewritten.

The `legacy/` directory is historical reference, not executable release input. Never add a new one-off patch there.

## Weapon catalog

Each weapon has a unique stable `id`, its existing display `name`, ordered region memberships, a `calculatorName`, and optional acquisition prerequisites. All memberships preserve current draw order and legacy labels (including the `(+8)` label). Gate layout placeholders reference IDs and contain no prerequisite values.

IDs are authoring identifiers only. Existing saved runs continue to store their original names and shapes; this consolidation introduces no save migration. The two endgame regions still inherit authored pools in `src/app.js`; compatibility tests cover them alongside the 20 imported pools. Legacy restoration code remains in `systems/weapons.js` for compatibility. Weapon type/skill/infusion metadata and regulation calculation records have not yet been merged into the catalog.

When adding a weapon: add its catalog record and region order, resolve its calculator reference, add a gate layout entry if gated, build, and run tests. Do not change IDs on a rename. For deliberate gameplay changes, update the release baseline only after reviewing the exact expected differences; never regenerate it merely to silence a failure.

## Visual theme

`src/theme.css` is the single place for the current look. It is included at the end of `<body>` so it wins over the older style passes in `src/styles.css`, `build-lab.css` and the one runtime-injected sheet. Its rules use the `:is(#app,html)` prefix, which matches every element but carries id-level weight, so it outranks older class-only rules without piling on more specificity. Nothing in it is read by gameplay code.

Two faces: Cinzel (`--display`) for titles, labels, tabs and the nav; EB Garamond (`--serif`) for reading text and buttons. One global rule sets every element to `var(--tc-ff, var(--serif))`, and any rule that picks a face also sets `--tc-ff`, so children inherit their container's face. To switch a block's face, set both `font-family` and `--tc-ff`. Link arrows are drawn by `<span class="tc-arrow">` (iOS turns the ↗ character into an emoji).

Grace and Encounter are one fixed screen: the page never scrolls, the tracks hide horizontal overflow, and `src/systems/restyle.js` turns one page per sideways swipe (decided during the move, so an iOS touchcancel still counts) by clicking the neighbouring tab, then animates the turn frame by frame. Native scroll-snap is off on these tracks; iOS Safari did not reliably smooth-scroll a container it cannot pan. The header starts 18px below the status-bar inset to stay out of iOS's blurred top edge.

On the Site of Grace and Encounter screens the page reserves exactly the nav's height (`padding-bottom` ≈ 64px + safe area). If the nav changes height, change that padding and `.tc-build-save-row`'s `bottom` with it.

`src/systems/restyle.js` only changes presentation: shorter nav labels, region and lock status on Remembrance rows, and the tap-to-explain boon grid. It reads state through existing helpers and never writes to the run.

The Build screen's Weapon / Stats / Gear tabs only show or hide sections. Every field stays in the DOM, so drafts, autosave and class validation read exactly the same inputs.

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

## Bug pass notes (2026-10-08)

- Region travel (`startNextRegion` hardening wrapper) carries every run-level record (Sanctioned/appeal boss kills, appeal cooldown, Chaos debt, an unfinished shared reward, unknown future fields) and rolls the region's first encounter after history is copied in.
- An invite link on a phone with no saved identity goes to the join screen instead of auto-joining as "Tarnished"; a shared reward reveal also clears once two different identities have seen it.
- `assignment-repair.js` never runs once a world is cleared or while a report/reward is open, rebuilds from the latest state at save time, and saves quietly (`commit(..., {quiet:true})`).
- Build Lab autosave is queued per player slot; saves merge only fields changed since the screen loaded; the field being typed is never rewritten; stats are whole numbers; picking a class keeps higher entered values.
- Weapon data: Elphael weapons wait for Loretta; Troll's Hammer belongs to the Altus Plateau. Baseline seeded scenarios shift from the first changed region onward because the seeded random stream shifts.
- `tests/bugfix-pass.cjs` covers the logic fixes.


## Polish batch (2026-10-13)
All in `src/systems/restyle.js` (end) and the last section of `src/theme.css`; presentation only.
- Sheets: overlays rise in via CSS. On close the app still removes the real element at once; a body MutationObserver drops in a clone (ids, `data-*`, `name`, `for` stripped; inert) that slides away. A same-class overlay added in the same batch counts as a re-render: no exit, no re-entry (`.tc-sheet-instant`).
- `setToast` is replaced (same API): fixed above the bottom bar, eases in and out.
- Count-up: `TC_COUNT_TARGETS`; first sight only records, increases animate.
- `commit` is wrapped to set `html.tc-saving` / `html.tc-saved` (the `.tc-sync` label pulses, then shows a check). Return value and options pass through untouched.
- `.tc-why` notes explain disabled buttons (`tcWhyScan`); hidden buttons get no note.
- Build number fields get `pattern="[0-9]*"`, `step=1`, and a `beforeinput` filter for non-digits.
- Button labels fit (`tcFitButtons`): a label wider than its button, or a single word with under 8px air per side, steps its font down to 70%; buttons sharing a row share the smallest size; past 70% the word may break. Tab bars and icon buttons are skipped.

## Boss-pool correction (2026-11-17)
Chief Bloodfiend (Rivermouth Cave) and Red Bear (Northern Nameless Mausoleum) moved from Gravesite Plain to Ancient Ruins of Rauh: both are reached from Temple Town Ruins on the Rauh side. `assignment-repair.js` now also re-rolls an unstarted encounter whose boss is no longer in its region's pool (never capstones, required/prerequisite targets, or encounters with a world clear); weapons stay unless barred by the new boss. Covered by `tests/boss-pool-repair.cjs`.
- Release check: after a merge, confirm a "pages build and deployment" run exists for the merge commit (`gh api repos/chasemonteiro/WorldForge/actions/runs`). PR #23's merge did not trigger one; a follow-up merge redeployed it.

## Hewg's Surplus (2026-11-24)
`src/systems/hewg-surplus.js`: a Favor shop shown in Ledger → Smithing once every Miner's Bell Bearing is claimed. Items and prices live in `TC_SHOP_ITEMS`; remembrance weapons in `TC_REMEMBRANCE_WEAPONS` (boss → Enia's weapons; spell-only remembrances have none). A remembrance purchase replaces one player's weapon for the current fight only (blocked after a world victory or during a report/shared reward). Purchases are pure builders keyed by a purchase id, so retries can't double-charge. New optional fields: `smithing.shopLog` (kept by a `smithingData` wrapper) and `current.remembranceSwaps`. Covered by `tests/hewg-surplus.cjs`.
- 2026-11-24: Metyr, Mother of Fingers, Count Ymir (her follow-up fight), and their quest weapons (Maternal Staff, Sword of Night) moved from Scadu Altus to Cerulean Coast: the Cathedral needs the Finger Ruins of Rhia bell, which is on the Cerulean Coast. Metyr's remembrance now counts toward Cerulean Coast.
- 2026-11-25: Site of Grace third panel is now "Forge" (`src/systems/forge-tab.js`): the Bell Bearing Hunt hub until every bearing is home, then Hewg's Surplus. Ledger → Smithing links there (`data-forge-open`). The room code moved to the panel foot; the duplicate quick links were dropped.
- 2026-11-25 (later): Forge panel redesigned around one SVG hearth scene (flames and embers when the shop is open, banked coals before). Wares are tiles: Hewg's finest (Masterwork Token, Remembrance Weapon), Covenant documents as wax-seal tiles, Covenant Draw as a sealed lot. Before all bearings, eight bells on a rail (tap for custodian/place and a Commission button). The room code now lives only in Settings.
- 2026-11-25: Grace and Progress panels refreshed (`src/systems/sanctuary-refresh.js`). Grace is a CSS grid (`.tc-grace-refresh`) so the observers that insert the memo, boss overlay, buildcraft row and idle flame can keep doing so in any order; the old pieces are hidden, the painting and flame share one hero, a "next fight" card opens the encounter, and the memo is a pinned parchment slip. Progress hides the old hub grid and adds the road of regions (scrolls on its own, centred on the current region), a ring of remembrance runes (tap for where/when), and run facts from history. Read-only.
- 2026-11-25: Ledger tabs renamed Remembrances · Dossiers · Satchel. The Satchel (`src/systems/ledger-satchel.js`) replaces the Smithing ledger body entirely: Favor purse → Forge, one card per held item grouped "Use it here" / "Use it in the fight" (Go-to buttons set `tcEncounterPanelIndex`), "None held" line, Masterwork credits + trophy tiles. Cards reuse the original action attributes, so spends still go through the original builders. Bell bearing list and Union Discount no longer shown in the Ledger.
- 2026-11-25: Dossiers (`src/systems/ledger-dossiers.js`) replaces `compendiumLedgerMarkup`: region chapters (newest first, current open) with compact rows; row evidence is the original dossier body sliced after `</summary>`. Filter state `tcDossierFilter` (all/capstone/chaos/penalty) is per session.
- 2026-11-25: Remembrances codex (`src/systems/ledger-remembrances.js`): `restyle.js`'s `remembranceLedgerBody` delegates to `tcRemembranceCodexMarkup` when present (restyle is included last, so a plain override would be lost). Grouped by region (base game first), each card shows claimed date / here / open / not reached and Hewg's forge options from `TC_REMEMBRANCE_WEAPONS`.
- 2026-11-25: Encounter tabs restyled (`src/systems/encounter-style.js` + theme section). Decorates existing panels in place (idempotent, re-applied after renders and DOM changes): sentence-case Chaos strip, Boss art hero with the name on it, world-clear buttons drawn as seals (`.tc-world-seal`, same `data-world-clear` handler), weapon cards with Masterwork / shop marks, penalty cards, holdings lines under Appeal/Recall, Chaos/Rite reserve as Satchel cards, and a record line per tab.

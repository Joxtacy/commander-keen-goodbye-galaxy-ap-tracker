# Commander Keen: Goodbye Galaxy - PopTracker Pack

AP tracker pack for the Commander Keen Archipelago world (kodbyte/Archipelago-Keen).

## Structure

- `manifest.json` - Pack metadata and variant definitions
- `items/items.json` - All trackable items with AP item codes (keen\_<id>)
- `locations/` - Locations with access rules and map coordinates
- `maps/` - Map image definitions
- `layouts/` - Per-variant tracker layouts (tabbed: items + maps)
- `scripts/init.lua` - Entry point, loads files per variant
- `scripts/autotracking.lua` - AP auto-tracking with item/location ID mappings
- `images/` - Sprite icons and map images

## Validation

The item/location ID maps in `scripts/autotracking.lua` and `items/items.json`
must stay in lock-step with the apworld's `worlds/keen/{Items,Locations}.py`.
`tools/check_drift.py` enforces this — it loads the apworld source in isolation
(no Archipelago deps needed) and reports any AP id the tracker fails to cover,
any stale tracker id, and SCORE_MAX counter mismatches. Pointsanity (5000-pt
pickups) is intentionally untracked and reported without failing.

```bash
tools/check_drift.py --apworld ../Archipelago-Keen   # or set KEEN_APWORLD
```

Run it after any apworld change that touches items/locations, and before
cutting a release.

## Key references

- APWorld: https://github.com/kodbyte/Archipelago-Keen (branch: keen-ap)
- PopTracker docs: https://github.com/black-sliver/PopTracker/blob/master/doc/PACKS.md
- Item IDs and location IDs must match worlds/keen/Items.py and worlds/keen/Locations.py

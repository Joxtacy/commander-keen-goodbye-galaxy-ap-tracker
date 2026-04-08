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

## Key references

- APWorld: https://github.com/kodbyte/Archipelago-Keen (branch: keen-ap)
- PopTracker docs: https://github.com/black-sliver/PopTracker/blob/master/doc/PACKS.md
- Item IDs and location IDs must match worlds/keen/Items.py and worlds/keen/Locations.py

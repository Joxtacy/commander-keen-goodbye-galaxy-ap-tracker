#!/usr/bin/env python3
"""Place the overworld level-entrance pins on the Keen 4/5 world maps from game
data, so they're reproducible like the level maps.

On the world map (game level 0), each level's entrance is marked in the info
plane by the value 0xC000 + N (N = the level's Gamemaps index; see omnispeak
CK_ScanForLevelEntry). The tracker pin is centred on that footprint, using the
same left=3 / top=2 tile crop the world image uses.

Miragia (CK4 level 9) is the exception: it's the disappearing mirage city, whose
entrance trigger is stored off-screen in the flicker-animation template at the
map bottom and only copied into place when the city is solid. So its 0xC009
marker sits in the template, not the play position — we instead centre its pin on
the Miragia object's spawn block (info value 33, a 6x4 block; see CK4_SpawnMiragia
/ CK4_Miragia0).

Pins are matched to their level by each overworld location's `level_<suffix>`
access rule (e.g. level_bv -> keen4_bv), which is robust against name spelling.

    python3 tools/place_overworld_pins.py        # needs the omnispeak game data
"""
from __future__ import annotations

import importlib.util
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
TRACKER = HERE.parent

# Reuse the game-data decoders and the tracker map-id table.
_spec = importlib.util.spec_from_file_location("render_pointsanity_maps", HERE / "render_pointsanity_maps.py")
R = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(R)
_lspec = importlib.util.spec_from_file_location("render_level_maps", HERE / "render_level_maps.py")
RL = importlib.util.module_from_spec(_lspec)
_lspec.loader.exec_module(RL)

TILE = 16
WORLD_LEVEL = 0          # world map = Gamemaps index 0
CROP = (3, 2)            # world images crop left=3, top=2 (matches level maps)
WORLD_MAP = {4: "Keen 4 - Shadowlands", 5: "Keen 5 - Omegamatic"}

# Miragia (CK4 9): centre on the Miragia object spawn block instead of its
# off-screen 0xC009 template marker.
MIRAGIA_EP, MIRAGIA_N, MIRAGIA_INFO, MIRAGIA_BLOCK = 4, 9, 33, (6, 4)

LEVEL_RULE = re.compile(r"\blevel_([a-z0-9]+)\b")


def _center_px(tiles: list[tuple[int, int]]) -> tuple[int, int]:
    """Pixel centre (on the cropped world image) of a set of footprint tiles."""
    left, top = CROP
    xs = [t[0] for t in tiles]
    ys = [t[1] for t in tiles]
    cx = (min(xs) + max(xs)) / 2
    cy = (min(ys) + max(ys)) / 2
    return round((cx - left) * TILE + TILE // 2), round((cy - top) * TILE + TILE // 2)


def entrance_pixels(ep: int) -> dict[int, tuple[int, int]]:
    """Level Gamemaps-index N -> pin pixel on the world image."""
    gfx = R.Graphics(ep)
    w, h, bg, fg, info = R.Maps(ep).load(WORLD_LEVEL)
    foot: dict[int, list[tuple[int, int]]] = {}
    for y in range(h):
        for x in range(w):
            v = info[y * w + x]
            if 0xC001 <= v <= 0xC012:
                foot.setdefault(v - 0xC000, []).append((x, y))
    out = {n: _center_px(tiles) for n, tiles in foot.items()}

    if ep == MIRAGIA_EP:
        spawn = [(x, y) for y in range(h) for x in range(w) if info[y * w + x] == MIRAGIA_INFO]
        if spawn:
            x0, y0 = spawn[0]
            bw, bh = MIRAGIA_BLOCK
            tiles = [(x0 + dx, y0 + dy) for dx in range(bw) for dy in range(bh)]
            out[MIRAGIA_N] = _center_px(tiles)
    return out


def main() -> None:
    total = 0
    for ep in (4, 5):
        pixels = entrance_pixels(ep)
        # suffix (from level_<suffix> rule) -> pin pixel. MAPID_TO_IDX indices
        # repeat across episodes, so resolve within this episode only.
        prefix = f"keen{ep}_"
        suffix_px: dict[str, tuple[int, int]] = {
            mid[len(prefix):]: pixels[idx]
            for mid, idx in RL.MAPID_TO_IDX.items()
            if mid.startswith(prefix) and idx in pixels
        }

        path = TRACKER / "locations" / f"keen{ep}_locations.json"
        data = json.loads(path.read_text())
        world = WORLD_MAP[ep]
        updated: list[tuple[str, int, int]] = []
        unmatched: list[str] = []

        def visit(node):
            if isinstance(node, dict):
                mls = node.get("map_locations") or []
                world_pins = [ml for ml in mls if isinstance(ml, dict) and ml.get("map") == world]
                if world_pins:
                    rules = " ".join(
                        r for s in (node.get("sections") or []) for r in s.get("access_rules", [])
                    )
                    m = LEVEL_RULE.search(rules)
                    suffix = m.group(1) if m else None
                    if suffix in suffix_px:
                        x, y = suffix_px[suffix]
                        for ml in world_pins:
                            if (ml.get("x"), ml.get("y")) != (x, y):
                                ml["x"], ml["y"] = x, y
                                updated.append((node.get("name", suffix), x, y))
                    else:
                        unmatched.append(node.get("name", "?"))
                for v in node.values():
                    visit(v)
            elif isinstance(node, list):
                for v in node:
                    visit(v)

        visit(data)
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
        total += len(updated)
        print(f"EP{ep}: updated {len(updated)} overworld pins")
        for name, x, y in updated:
            print(f"  {name:36s} -> ({x}, {y})")
        if unmatched:
            print(f"  UNMATCHED (no game entrance): {unmatched}")

    print(f"\nUpdated {total} overworld pins from game data.")


if __name__ == "__main__":
    main()

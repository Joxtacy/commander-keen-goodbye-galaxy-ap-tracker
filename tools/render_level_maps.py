#!/usr/bin/env python3
"""Render every Commander Keen 4/5 tracker level map from the original game data
and stamp all trackable collectibles onto them, so the maps are fully
reproducible from the game (no hand-made art).

This supersedes the old overlay-onto-hand-art approach: instead of compositing
sprites onto pre-existing polished PNGs, it renders each level's background +
foreground from the game (tools/render_pointsanity_maps.render_map), crops it to
the tracker framing, and stamps the collectibles at their exact in-game tiles.

Crop / coordinates
------------------
Each tracker image crops the game's tile grid by a left border of 3 tiles and a
top border that is usually 2 (a few levels trim more empty sky / floor: see
CROP). A collectible at game tile (tx, ty) lands at image pixel centre
((tx-left)*16+8, (ty-top)*16+8). The CROP table was derived once by aligning the
former hand-made art against the game render; it is kept fixed so the existing
location pins (placed against these crops) stay valid.

Collectibles
------------
Gems (Red/Yellow/Blue/Green), the Keen 5 Keycard, the 5000-pt pickups (Ice Cream
Cone / Bag O' Sugar) and the extra-life pickups (Lifewater Flask / Vitalin Keg).
Each is located by scanning the level (info-layer spawns first, then foreground
tiles carrying its misc flag) and drawn with its real in-game icon. Minor point
treasures (gum, soda, ...) are not AP locations and are not stamped.

Output images/Ck?lv??.png are a deterministic function of the game data + this
script. Needs the omnispeak game data that render_pointsanity_maps points at.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
TRACKER = HERE.parent
IMAGES = TRACKER / "images"

# Reuse the renderer's game-data decoders (Graphics, Maps, render_map, scan_pickups).
_spec = importlib.util.spec_from_file_location(
    "render_pointsanity_maps", HERE / "render_pointsanity_maps.py"
)
R = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(R)

TILE = 16

# tracker map-id -> Gamemaps level index (matches maps/keen{4,5}_maps.json order;
# untracked levels — Pyramid of the Forbidden (CK4 14), Korath III (CK5 13) —
# have no tracker map and are intentionally absent).
MAPID_TO_IDX = {
    "keen4_bv": 1, "keen4_sv": 2, "keen4_pp": 3, "keen4_cotd": 4, "keen4_coc": 5,
    "keen4_crys": 6, "keen4_hil": 7, "keen4_sy": 8, "keen4_mir": 9, "keen4_lo": 10,
    "keen4_potm": 11, "keen4_pos": 12, "keen4_potga": 13, "keen4_iot": 15,
    "keen4_iof": 16, "keen4_wow": 17, "keen4_bwbm": 18,
    "keen5_ivs": 1, "keen5_sc": 2, "keen5_dtv": 3, "keen5_efs": 4, "keen5_dtb": 5,
    "keen5_rcc": 6, "keen5_dts": 7, "keen5_nbi": 8, "keen5_dtt": 9, "keen5_bmi": 10,
    "keen5_gdh": 11, "keen5_qed": 12,
}

# Per-level crop in tiles (left, top, right, bottom). Left is always 3; top/bottom
# vary where the original framing trimmed empty sky/floor. Derived once by aligning
# the former hand art against the game render (mean-abs pixel match); kept fixed so
# location pins stay valid. If the art framing ever needs changing, re-derive and
# migrate the affected pins in lock-step.
CROP = {
    "keen4_bv": (3, 2, 1, 2), "keen4_sv": (3, 6, 1, 2), "keen4_pp": (3, 2, 1, 2),
    "keen4_cotd": (3, 2, 1, 2), "keen4_coc": (3, 2, 1, 2), "keen4_crys": (3, 2, 1, 2),
    "keen4_hil": (3, 2, 1, 2), "keen4_sy": (3, 2, 1, 2), "keen4_mir": (3, 2, 1, 2),
    "keen4_lo": (3, 2, 1, 3), "keen4_potm": (3, 2, 1, 2),
    "keen4_pos": (3, 2, 1, 2),  # bottom was 4, but that clipped 2 rows of real
    # cave geometry above the "EDGE OF MAP" border (rows 97-98); 2 matches the norm
    "keen4_potga": (3, 2, 1, 2), "keen4_iot": (3, 2, 1, 2), "keen4_iof": (3, 2, 1, 2),
    "keen4_wow": (3, 2, 1, 2), "keen4_bwbm": (3, 2, 1, 2),
    "keen5_ivs": (3, 4, 1, 2), "keen5_sc": (3, 2, 1, 2), "keen5_dtv": (3, 2, 1, 2),
    "keen5_efs": (3, 2, 1, 2), "keen5_dtb": (3, 2, 1, 2), "keen5_rcc": (3, 2, 1, 2),
    "keen5_dts": (3, 2, 1, 2), "keen5_nbi": (3, 2, 1, 2), "keen5_dtt": (3, 2, 1, 2),
    "keen5_bmi": (3, 2, 1, 2), "keen5_gdh": (3, 2, 1, 2), "keen5_qed": (3, 2, 1, 2),
}

# Trackable collectibles. "item" is the info-plane item number (spawns at
# 57+item); "misc" is the foreground-tile flag (only used by "both"-mode scans).
#
# "scan" picks how positions are found:
#   "info" — info-layer spawns only (info == 57+item). Gems and the Keycard are
#            single collectibles placed this way; matching foreground misc tiles
#            are scenery (gem holders, card-coloured walls), so a foreground scan
#            would over-count.
#   "both" — info-layer spawns then foreground misc tiles (the AP/client order).
#            Point and extra-life pickups are placed either way; counts here match
#            the apworld worksheet / drift check.
#
# The icon is the item's actual in-game pickup sprite, by EGAGRAPH chunk per
# episode ("spr"; the real floating gem/keycard/keg sprite — NOT the gem-holder
# tile). Where an item has no sprite entry for an episode it falls back to the
# foreground tile "tile" (CK4 cone/flask carry their graphic as a fg tile).
# Sprite chunks: gems SPR_GEM_A1..D1, keycard SPR_SECURITYCARD_1, keg SPR_1UP1
# (from omnispeak ck_obj.c CK_ItemSpriteChunks + data/keen{4,5}/GFXCHUNK).
COLLECTIBLES = [
    {"name": "Red Gem", "item": 0, "misc": None, "scan": "info", "eps": (4, 5), "spr": {4: 242, 5: 224}},
    {"name": "Yellow Gem", "item": 1, "misc": None, "scan": "info", "eps": (4, 5), "spr": {4: 244, 5: 226}},
    {"name": "Blue Gem", "item": 2, "misc": None, "scan": "info", "eps": (4, 5), "spr": {4: 246, 5: 228}},
    {"name": "Green Gem", "item": 3, "misc": None, "scan": "info", "eps": (4, 5), "spr": {4: 248, 5: 230}},
    {"name": "Point pickup", "item": 9, "misc": 26, "scan": "both", "eps": (4, 5), "spr": {}, "tile": 26},
    {"name": "Extra life", "item": 10, "misc": 27, "scan": "both", "eps": (4, 5), "spr": {5: 222}, "tile": 27},
    {"name": "Keycard", "item": 13, "misc": None, "scan": "info", "eps": (5,), "spr": {5: 207}},
]


def collectible_icon(gfx, ep, c) -> Image.Image:
    """The item's real in-game pickup sprite for this episode (sprite chunk if
    set, else its foreground tile)."""
    if ep in c.get("spr", {}):
        return gfx.sprite_rgba(c["spr"][ep])
    return gfx.item_graphic(c["tile"], None)


def collectible_tiles(gfx, w, h, fg, info, c) -> list[tuple[int, int]]:
    """Game tiles holding collectible `c` (see the "scan" field)."""
    if c["scan"] == "info":
        val = R.ITEM_INFO_BASE + c["item"]
        return [(x, y) for y in range(h) for x in range(w) if info[y * w + x] == val]
    return [(p["x"], p["y"]) for p in R.scan_pickups(gfx, w, h, fg, info, c["misc"], c["item"])]


def map_id_to_image() -> dict[str, str]:
    out: dict[str, str] = {}
    for ep in (4, 5):
        for entry in json.loads((TRACKER / "maps" / f"keen{ep}_maps.json").read_text()):
            if entry["name"] in MAPID_TO_IDX:
                out[entry["name"]] = Path(entry["img"]).name
    return out


def main() -> None:
    mapid_img = map_id_to_image()
    gfxs = {ep: R.Graphics(ep) for ep in (4, 5)}
    mapses = {ep: R.Maps(ep) for ep in (4, 5)}
    # Pre-decode each episode's collectible icons once.
    icons = {
        ep: [(c, collectible_icon(gfxs[ep], ep, c))
             for c in COLLECTIBLES if ep in c["eps"]]
        for ep in (4, 5)
    }

    total_maps = total_picks = 0
    for mapid, idx in MAPID_TO_IDX.items():
        ep = 4 if mapid.startswith("keen4") else 5
        gfx, maps = gfxs[ep], mapses[ep]
        w, h, bg, fg, info = maps.load(idx)
        left, top, right, bottom = CROP[mapid]

        img = R.render_map(gfx, w, h, bg, fg).convert("RGBA")
        img = img.crop((left * TILE, top * TILE, (w - right) * TILE, (h - bottom) * TILE))
        iw_img, ih_img = img.size

        counts: dict[str, int] = {}
        for c, icon in icons[ep]:
            iw, ih = icon.size
            for tx, ty in collectible_tiles(gfx, w, h, fg, info, c):
                cx = (tx - left) * TILE + TILE // 2
                cy = (ty - top) * TILE + TILE // 2
                if not (0 <= cx < iw_img and 0 <= cy < ih_img):
                    continue
                img.paste(icon, (cx - iw // 2, cy - ih // 2), icon)
                counts[c["name"]] = counts.get(c["name"], 0) + 1

        img.convert("RGB").save(IMAGES / mapid_img[mapid])
        total_maps += 1
        total_picks += sum(counts.values())
        summary = ", ".join(f"{k}×{v}" for k, v in counts.items()) or "(no collectibles)"
        print(f"  {mapid:12s} -> {mapid_img[mapid]:12s} {summary}")

    print(f"\nRendered {total_maps} level maps and stamped {total_picks} collectibles "
          f"— fully from game data.")


if __name__ == "__main__":
    main()

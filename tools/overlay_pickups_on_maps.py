#!/usr/bin/env python3
"""Burn the real in-game 5000-pt and extra-life pickup sprites onto the
tracker's level map images, so pickups hidden inside walls / spawned from the
info layer (invisible in the static map render) become visible.

Unlike tools/render_pointsanity_maps.py — which re-renders whole levels from
scratch into the gitignored reference sets (pointsanity_maps/, extralife_maps/)
— this tool keeps the tracker's own polished level art (images/Ck?lv??.png) and
just stamps the pickup sprites on top, at each pickup's exact in-game position.

Coordinate system (auto-aligned, game-derived)
----------------------------------------------
The tracker level images are cropped from the full level by a per-level,
NON-uniform tile border (left is 3 tiles on every level; top is 2, 4, or 6
depending on the level), so a single hardcoded offset places pickups wrong.
Instead we DERIVE the crop from the game itself: render the whole level from the
game data at 16px/tile (render_pointsanity_maps.render_map) and brute-force the
(left, top) tile offset whose crop best matches the tracker's own art. A pickup
at game tile (tx, ty) then lands at image pixel centre
((tx-left)*16+8, (ty-top)*16+8). This relies only on game data + the image, never
on the (sometimes wrong) tracker location pins. Sand Yego needs no special-case:
it simply aligns to left=3/top=2.

Composited levels
-----------------
A few tracker maps are hand-composited — the level geometry is rearranged to fit
(e.g. Border Village stacks its underground rooms into side panels), so no linear
crop maps game tiles onto them. Those are listed in COMPOSITE and skipped (their
pickups would be misplaced); the alignment residual flags any others.

Re-runnable
-----------
Pristine base maps live in images/_base_levels/ (committed). This tool always
composites from there into images/, so re-running never double-stamps. On first
run it seeds the base dir from the current images/.
"""
from __future__ import annotations

import importlib.util
import json
import shutil
from pathlib import Path

from PIL import Image, ImageChops

HERE = Path(__file__).resolve().parent
TRACKER = HERE.parent
IMAGES = TRACKER / "images"
BASE = IMAGES / "_base_levels"

# Reuse the renderer's game-data decoders (Graphics, Maps, scan_pickups, ITEMS).
_spec = importlib.util.spec_from_file_location(
    "render_pointsanity_maps", HERE / "render_pointsanity_maps.py"
)
R = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(R)

TILE = 16

# Tracker maps whose geometry is hand-rearranged (not a faithful crop), so a
# linear tile->pixel mapping can't place their pickups. Skipped; see docstring.
# (keen4_bv / Border Village was re-rendered faithfully, so it's no longer here.)
COMPOSITE: set[str] = set()

# Residual above this (mean abs per-channel pixel diff at the best alignment)
# means the render and tracker art disagree enough to suspect a composited or
# heavily-edited map — worth an eyeball even if not in COMPOSITE.
RESID_WARN = 25.0

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

def _mean_abs_diff(a: Image.Image, b: Image.Image) -> float:
    """Mean absolute per-channel pixel difference between two equal-size RGB images."""
    hist = ImageChops.difference(a, b).convert("L").histogram()
    n = sum(hist)
    return sum(i * c for i, c in enumerate(hist)) / n if n else 999.0


def find_crop(full: Image.Image, base: Image.Image) -> tuple[int, int, float, float]:
    """Brute-force the (left, top) tile crop that aligns the tracker image `base`
    to a sub-rectangle of the full game render `full`. Returns
    (left, top, residual, gap) where residual is the best mean-abs pixel diff and
    gap is how much worse the runner-up offset is (small gap => ambiguous match)."""
    fw, fh = full.size
    iw, ih = base.size
    scored: list[tuple[float, int, int]] = []
    for left in range(0, 7):
        for top in range(0, fh // TILE - ih // TILE + 1):
            x0, y0 = left * TILE, top * TILE
            if x0 + iw > fw or y0 + ih > fh:
                continue
            scored.append((_mean_abs_diff(full.crop((x0, y0, x0 + iw, y0 + ih)), base), left, top))
    scored.sort()
    best = scored[0]
    gap = (scored[1][0] - best[0]) if len(scored) > 1 else best[0]
    return best[1], best[2], best[0], gap


def map_id_to_image() -> dict[str, str]:
    out: dict[str, str] = {}
    for ep in (4, 5):
        for entry in json.loads((TRACKER / "maps" / f"keen{ep}_maps.json").read_text()):
            if entry["name"] in MAPID_TO_IDX:
                out[entry["name"]] = Path(entry["img"]).name
    return out


def seed_base() -> None:
    """Copy pristine level images into images/_base_levels/ on first run."""
    BASE.mkdir(parents=True, exist_ok=True)
    for fname in set(map_id_to_image().values()):
        dst = BASE / fname
        if not dst.exists():
            shutil.copy2(IMAGES / fname, dst)
            print(f"  seeded base {fname}")


def main() -> None:
    seed_base()
    mapid_img = map_id_to_image()

    # Per episode: load the item sprites once (cone/sugar misc 26; flask/keg misc 27).
    sprites: dict[int, list[tuple[dict, Image.Image]]] = {}
    gfxs: dict[int, R.Graphics] = {}
    mapses: dict[int, R.Maps] = {}
    for ep in (4, 5):
        gfxs[ep] = R.Graphics(ep)
        mapses[ep] = R.Maps(ep)
        sprites[ep] = [
            (item, gfxs[ep].item_graphic(item["misc"], item["sprite"].get(ep)))
            for item in R.ITEMS
        ]

    total_maps = total_picks = 0
    for mapid, idx in MAPID_TO_IDX.items():
        ep = 4 if mapid.startswith("keen4") else 5
        gfx, maps = gfxs[ep], mapses[ep]
        w, h, bg, fg, info = maps.load(idx)

        base_img = Image.open(BASE / mapid_img[mapid]).convert("RGBA")
        iw_img, ih_img = base_img.size

        if mapid in COMPOSITE:
            # Restore the clean composited art in case a prior run stamped it.
            shutil.copy2(BASE / mapid_img[mapid], IMAGES / mapid_img[mapid])
            print(f"  {mapid:12s} -> {mapid_img[mapid]:12s} SKIPPED (composited map; "
                  f"pickups can't be placed by a linear crop)")
            continue

        # Derive the crop from the game itself, not the tracker pins.
        full = R.render_map(gfx, w, h, bg, fg).convert("RGB")
        left, top, resid, gap = find_crop(full, base_img.convert("RGB"))

        img = base_img.copy()
        n_here = 0
        offscreen = 0
        for item, icon in sprites[ep]:
            iw, ih = icon.size
            for p in R.scan_pickups(gfx, w, h, fg, info, item["misc"], item["item"]):
                cx = (p["x"] - left) * TILE + TILE // 2
                cy = (p["y"] - top) * TILE + TILE // 2
                if not (0 <= cx < iw_img and 0 <= cy < ih_img):
                    offscreen += 1
                    continue
                img.paste(icon, (cx - iw // 2, cy - ih // 2), icon)
                n_here += 1

        if n_here == 0:
            continue
        img.convert("RGB").save(IMAGES / mapid_img[mapid])
        total_maps += 1
        total_picks += n_here
        notes = []
        if offscreen:
            notes.append(f"{offscreen} outside image")
        if resid > RESID_WARN:
            notes.append(f"HIGH residual {resid:.0f} — verify alignment")
        note = f"  ({'; '.join(notes)})" if notes else ""
        print(f"  {mapid:12s} -> {mapid_img[mapid]:12s} crop L={left} T={top} "
              f"(resid {resid:4.1f}, gap {gap:4.1f})  {n_here} pickups{note}")

    print(f"\nStamped {total_picks} pickups onto {total_maps} tracker maps "
          f"(base art preserved in {BASE.relative_to(TRACKER)}/; "
          f"{len(COMPOSITE)} composited map(s) skipped).")


if __name__ == "__main__":
    main()

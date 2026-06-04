#!/usr/bin/env python3
"""Generate the pointsanity (5000-pt) tracker glue from the apworld.

Conesanity (CK4 Ice Cream Cones) and sugarsanity (CK5 Bags O' Sugar): each pickup
gets a map pin at its real in-game position; pickups close together are merged
into one pin (proximity clustering), and a pin's sections are split by access
rule and gated behind a `conesanity`/`sugarsanity` toggle.

This script is the source of truth for the generated artifacts; rerun it if the
apworld's pointsanity counts / rules change.

Outputs (written in place):
  - locations/keen4_cone_locations.json
  - locations/keen5_sugar_locations.json
  - locations/keen4_locations.json, locations/keen5_locations.json
      (overworld level pins get a `ref` per cone/sugar section so the pin
      reflects remaining pickups, mirroring the flask/keg roll-up; previous
      pointsanity refs are replaced, hand-authored flask/keg refs are kept)
  - images/ice_cream_cone.png, images/bag_o_sugar.png   (counter icons)
And prints, for pasting into scripts/autotracking.lua:
  - CK4_CONE_LAYOUT / CK5_SUGAR_LAYOUT tables
  - SCORE_MAX cone_count / sugar_count totals

Pin coordinates come from the real in-game tile of each pickup (via
render_pointsanity_maps), transformed to the tracker's cropped level image:
image = (tile - 2) * 16  (the level images trim the 2-tile border).
"""
from __future__ import annotations

import importlib.util
import json
import sys
import types
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
APWORLD = Path("/Users/joxtacy/PrivateProjects/Archipelago-Keen")

POINTS5K_CLASS = 5
TILE = 16
BORDER = 2  # most level images trim a 2-tile border off the top-left
# Per-level (left, top) border-trim override where the level image isn't the
# usual 2 tiles. Sand Yego's image (Ck4lv08, re-rendered faithfully) trims 3
# columns on the left and 0 on the right; the rest stay at 2.
BORDER_OVERRIDE = {(1, 8): (3, 2)}

# level id -> tracker code abbreviation (matches autotracking.lua level_* codes)
ABBR = {
    1: {1: "bv", 2: "sv", 3: "pp", 4: "cotd", 5: "coc", 6: "crys", 7: "hil",
        8: "sy", 9: "mir", 10: "lo", 11: "potm", 12: "pos", 13: "potga",
        14: "potf", 15: "iot", 16: "iof", 17: "wow", 18: "bwbm"},
    2: {1: "ivs", 2: "sc", 3: "dtv", 4: "efs", 5: "dtb", 6: "rcc", 7: "dts",
        8: "nbi", 9: "dtt", 10: "bmi", 11: "gdh", 12: "qed"},
}
EP_CFG = {
    1: {"tracker_ep": "Keen 4", "map_prefix": "keen4_",
        "singular": "Ice Cream Cone", "plural": "Ice Cream Cones",
        "toggle": "conesanity", "counter": "cone_count", "out": "keen4_cone_locations.json",
        "overworld": "keen4_locations.json"},
    2: {"tracker_ep": "Keen 5", "map_prefix": "keen5_",
        "singular": "Bag O' Sugar", "plural": "Bags O' Sugar",
        "toggle": "sugarsanity", "counter": "sugar_count", "out": "keen5_sugar_locations.json",
        "overworld": "keen5_locations.json"},
}
TOKEN_CODE = {"pogo": "pogo", "stunner": "stunner", "wetsuit": "wetsuit"}


# --------------------------------------------------------------------------- #
# Load apworld Locations (isolated, like tools/check_drift.py)                #
# --------------------------------------------------------------------------- #
def load_locations():
    keen = APWORLD / "worlds" / "keen"
    bc = types.ModuleType("BaseClasses")

    class _Base:
        pass

    class ItemClassification:
        progression = useful = filler = trap = skip_balancing = 1

    bc.Location = bc.Item = _Base
    bc.ItemClassification = ItemClassification
    sys.modules["BaseClasses"] = bc
    spec = importlib.util.spec_from_file_location("Locations", keen / "Locations.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def load_rules_dicts():
    """Eval just the two pointsanity rule dicts out of Rules.py (importing the
    module would pull in worlds.generic.Rules)."""
    text = (APWORLD / "worlds" / "keen" / "Rules.py").read_text()

    def block(name):
        i = text.index(f"{name} = ")
        open_i = text.index("{", i)
        depth = 0
        for j in range(open_i, len(text)):
            if text[j] == "{":
                depth += 1
            elif text[j] == "}":
                depth -= 1
                if depth == 0:
                    return eval(text[open_i:j + 1], {"dict": dict})  # noqa: S307
        raise ValueError(name)

    return block("ck4_points5k_rules"), block("ck5_points5k_rules")


# --------------------------------------------------------------------------- #
# Access-rule helpers                                                         #
# --------------------------------------------------------------------------- #
def signature(rule: dict) -> tuple:
    reqs = tuple(sorted(rule.get("requires", ())))
    gems = tuple(rule.get("gems", ()))
    return reqs, gems


def section_label(plural: str, sig: tuple) -> str:
    reqs, gems = sig
    bits = []
    if gems:
        bits.extend(gems)
    if "pogo" in reqs:
        bits.append("Pogo")
    if "stunner" in reqs:
        bits.append("Stunner")
    return f"{plural} ({', '.join(bits)})" if bits else plural


def access_rules(toggle: str, abbr: str, sig: tuple) -> list[str]:
    reqs, gems = sig
    base = [toggle, f"level_{abbr}"]
    for tok in reqs:
        base.append(TOKEN_CODE[tok])
    if not gems:
        return [",".join(base)]
    gem_codes = [f"{abbr}_{g.split()[0].lower()}" for g in gems]
    return [",".join(base + gem_codes), ",".join(base + [f"{abbr}_gemset"])]


# --------------------------------------------------------------------------- #
# Per-pickup pixel coords + proximity clustering                              #
# --------------------------------------------------------------------------- #
CLUSTER_PX = 32  # pickups within this distance share one map pin (~2 tiles)


def tile_to_px(tx: int, ty: int, left: int = BORDER, top: int = BORDER) -> tuple[int, int]:
    """In-game tile -> tracker level-image pixel. The images trim a border off
    the top-left (usually 2 tiles; see BORDER_OVERRIDE); +8 centres on the tile.
    Validated to ~1 tile against the pack's existing gem markers."""
    return (tx - left) * TILE + TILE // 2, (ty - top) * TILE + TILE // 2


def pickup_px():
    """{(ap_ep, level_id): {inst: (px, py)}} from the real in-game tile of each
    5000-pt pickup, clamped to the level image. {} if game data is unavailable."""
    try:
        import render_pointsanity_maps as R
        from PIL import Image
    except Exception as e:  # pragma: no cover
        print(f"  (skipping pin coords: {e})", file=sys.stderr)
        return {}
    maps_cfg = {}
    for ep in (4, 5):
        for m in json.loads((REPO / "maps" / f"keen{ep}_maps.json").read_text()):
            maps_cfg[m["name"]] = m["img"]
    out = {}
    for ep, ap_ep in ((4, 1), (5, 2)):
        g, mp = R.Graphics(ep), R.Maps(ep)
        for idx in R.LEVELS[ep]:
            if idx not in ABBR[ap_ep]:
                continue
            w, h, _bg, fg, info = mp.load(idx)
            picks = R.scan_pickups(g, w, h, fg, info, 26, 9)  # inst-ordered
            if not picks:
                continue
            iw = ih = None
            img_path = maps_cfg.get(EP_CFG[ap_ep]["map_prefix"] + ABBR[ap_ep][idx])
            if img_path:
                iw, ih = Image.open(REPO / img_path).size
            left, top = BORDER_OVERRIDE.get((ap_ep, idx), (BORDER, BORDER))
            per = {}
            for inst, p in enumerate(picks):
                px, py = tile_to_px(p["x"], p["y"], left, top)
                if iw:
                    px, py = max(12, min(px, iw - 12)), max(12, min(py, ih - 12))
                per[inst] = (px, py)
            out[(ap_ep, idx)] = per
    return out


def cluster(items, thresh):
    """Single-linkage cluster items=[(key,(x,y)),...] within `thresh` px.
    Returns list of lists of keys."""
    keys = [k for k, _ in items]
    pos = dict(items)
    parent = {k: k for k in keys}

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    for i, a in enumerate(keys):
        for b in keys[i + 1:]:
            (ax, ay), (bx, by) = pos[a], pos[b]
            if (ax - bx) ** 2 + (ay - by) ** 2 <= thresh * thresh:
                parent[find(a)] = find(b)
    groups: dict = {}
    for k in keys:
        groups.setdefault(find(k), []).append(k)
    return list(groups.values())


def _runs(nums: list[int]):
    """Yield (lo, hi) contiguous runs over a sorted int list."""
    lo = prev = nums[0]
    for n in nums[1:] + [None]:
        if n != prev + 1:
            yield lo, prev
            lo = n
        prev = n


# --------------------------------------------------------------------------- #
# Counter icons                                                               #
# --------------------------------------------------------------------------- #
def write_icons():
    try:
        import render_pointsanity_maps as R
    except Exception as e:  # pragma: no cover
        print(f"  (skipping icons: {e})", file=sys.stderr)
        return
    for ep, fname in ((4, "ice_cream_cone.png"), (5, "bag_o_sugar.png")):
        g = R.Graphics(ep)
        icon = g.item_graphic(26, None).resize((32, 32))
        icon.save(REPO / "images" / fname)
        print(f"  wrote images/{fname}")


# --------------------------------------------------------------------------- #
# Main                                                                        #
# --------------------------------------------------------------------------- #
def main():
    Loc = load_locations()
    ck4_rules, ck5_rules = load_rules_dicts()
    rules_by_ep = {1: ck4_rules, 2: ck5_rules}
    counts_by_ep = {1: Loc.ck4_points5k_counts, 2: Loc.ck5_points5k_counts}
    excluded_by_ep = {1: Loc.ck4_points5k_excluded, 2: Loc.ck5_points5k_excluded}
    display_by_ep = {1: Loc.ck4_points5k_display_index, 2: Loc.ck5_points5k_display_index}
    name_by_ep = {1: Loc.ck4_level_id_to_name_with_potf, 2: Loc.ck5_level_id_to_name}

    coords = pickup_px()
    write_icons()

    for ap_ep in (1, 2):
        cfg = EP_CFG[ap_ep]
        rules, counts = rules_by_ep[ap_ep], counts_by_ep[ap_ep]
        excluded, display = excluded_by_ep[ap_ep], display_by_ep[ap_ep]
        names = name_by_ep[ap_ep]
        entries = []          # locations JSON
        layout_lines = []     # lua layout, grouped per level
        refs_by_level = {}    # overworld node name -> ["<node>/<section>", ...]
        total = 0

        for lvl in sorted(counts):
            count = counts[lvl]
            if count <= 0:
                continue
            abbr = ABBR[ap_ep][lvl]
            level_name = names[lvl]
            map_name = cfg["map_prefix"] + abbr
            level_px = coords.get((ap_ep, lvl), {})

            # per-inst signature + pixel for non-excluded pickups (the display
            # number only feeds the rule-dict lookup; nodes are named by label)
            info = {}
            for inst in range(count):
                if (lvl, inst) in excluded:
                    continue
                disp = display.get((lvl, inst), inst + 1)
                loc_name = f"{level_name} - {cfg['singular']} {disp}"
                info[inst] = {
                    "sig": signature(rules.get(loc_name, {})),
                    "px": level_px.get(inst, (24 + 18 * inst, 24)),
                }
            if not info:
                continue
            total += len(info)

            # One tracker node per access signature, so each label folds into a
            # single counter on both the overworld pin and the level map (the
            # flask/keg roll-up: same label -> one entry + count, not one entry
            # per pickup). Within a signature, proximity-cluster the pickups so
            # every pickup still gets a map pin at its real in-game position;
            # all of a signature's pins share the one counter.
            by_sig, sig_order = {}, []
            for inst in sorted(info):
                sig = info[inst]["sig"]
                if sig not in by_sig:
                    by_sig[sig] = []
                    sig_order.append(sig)
                by_sig[sig].append(inst)

            level_layout = []
            for sig in sig_order:
                members = by_sig[sig]
                sec = section_label(cfg["plural"], sig)
                node = f"{level_name} - {sec}"
                clusters = cluster([(i, info[i]["px"]) for i in members], CLUSTER_PX)
                clusters.sort(key=lambda c: min(c))  # stable, low-inst first
                map_locations = []
                for cl in clusters:
                    cx = round(sum(info[i]["px"][0] for i in cl) / len(cl))
                    cy = round(sum(info[i]["px"][1] for i in cl) / len(cl))
                    map_locations.append({"map": map_name, "x": cx, "y": cy})
                entries.append({
                    "name": node,
                    "map_locations": map_locations,
                    "sections": [{
                        "name": sec,
                        "item_count": len(members),
                        "access_rules": access_rules(cfg["toggle"], abbr, sig),
                    }],
                })
                # roll the section up into the level's overworld pin (mirrors
                # the flask/keg ref). Top-level node => no "Keen N/" prefix.
                refs_by_level.setdefault(level_name, []).append(f"{node}/{sec}")
                for lo, hi in _runs(sorted(members)):
                    level_layout.append(
                        f'\t\t{{lo={lo}, hi={hi}, entry="{node}", section="{sec}"}},')
            layout_lines.extend(level_layout)
            layout_lines.append(f"@LEVEL {lvl}")

        # write locations json
        out_path = REPO / "locations" / cfg["out"]
        out_path.write_text(json.dumps(entries, indent=2) + "\n")
        print(f"\nwrote {out_path.relative_to(REPO)}  ({len(entries)} pins, {total} pickups)")

        # inject overworld roll-up refs so each level's overworld pin reflects
        # remaining cone/sugar checks. Pointsanity refs are the only refs that
        # lack the "<Keen 4|Keen 5>/" prefix (flask/keg refs always carry it),
        # which makes stripping the previous round's refs unambiguous.
        ow_path = REPO / "locations" / cfg["overworld"]
        ow = json.loads(ow_path.read_text())
        prefix = cfg["tracker_ep"] + "/"
        injected = 0
        for root in ow:
            for child in root.get("children", []):
                secs = child.get("sections")
                if secs is None:
                    continue
                kept = [s for s in secs
                        if not ("ref" in s and not s["ref"].startswith(prefix))]
                new_refs = [{"ref": r} for r in refs_by_level.get(child["name"], [])]
                child["sections"] = kept + new_refs
                injected += len(new_refs)
        ow_path.write_text(json.dumps(ow, indent=2) + "\n")
        print(f"injected {injected} pointsanity refs into "
              f"{ow_path.relative_to(REPO)}")

        # emit lua layout grouped by level
        var = "CK4_CONE_LAYOUT" if ap_ep == 1 else "CK5_SUGAR_LAYOUT"
        print(f"\n-- paste into autotracking.lua --\nlocal {var} = {{")
        buf = []
        pending = []
        for line in layout_lines:
            if line.startswith("@LEVEL"):
                lvl = line.split()[1]
                buf.append(f"\t[{lvl}] = {{\n" + "\n".join(pending) + "\n\t},")
                pending = []
            else:
                pending.append(line)
        print("\n".join(buf))
        print("}")
        print(f"SCORE_MAX {cfg['counter']} = {total}")


if __name__ == "__main__":
    main()

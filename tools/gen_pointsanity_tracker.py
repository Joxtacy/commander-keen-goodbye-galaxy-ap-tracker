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
BORDER = 3  # fallback only; real per-level crops come from render_level_maps.CROP
# The level images are cropped by render_level_maps.py using its per-level CROP
# table (left=3 for every level; top is usually 2 but a few trim more empty sky,
# e.g. keen4_sv=6, keen5_ivs=4). A pin's pixel = ((tile-left)*16+8, (tile-top)*16+8)
# MUST use that same crop or the pin drifts off the sprite stamped on the image.
# CROP is the single source of truth — looked up per map in pickup_px() below.

# level id -> tracker code abbreviation (matches autotracking.lua level_* codes)
ABBR = {
    1: {1: "bv", 2: "sv", 3: "pp", 4: "cotd", 5: "coc", 6: "crys", 7: "hil",
        8: "sy", 9: "mir", 10: "lo", 11: "potm", 12: "pos", 13: "potga",
        14: "potf", 15: "iot", 16: "iof", 17: "wow", 18: "bwbm"},
    2: {1: "ivs", 2: "sc", 3: "dtv", 4: "efs", 5: "dtb", 6: "rcc", 7: "dts",
        8: "nbi", 9: "dtt", 10: "bmi", 11: "gdh", 12: "qed", 13: "korath"},
}

# Secret-level abbreviations whose pointsanity is double-gated by an extra
# enable_<ep>_secret_level toggle on top of cone/sugar-sanity.
SECRET_GATE = {"potf": "ck4_secret_level", "korath": "ck5_secret_level"}
# Secret levels are also reached only by traversing another level (POM inchworms
# / the GDH teleporter); a $logic function encodes that cross-level prerequisite
# (see scripts/logic.lua, mirrors Rules.py potf_gate / korath_gate).
SECRET_REACHABLE = {"potf": "$potf_reachable", "korath": "$korath_reachable"}
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
    module would pull in worlds.generic.Rules). Captures both the base literal
    `name = {...}` and any later `name.update({...})` blocks (the secret levels'
    cone/sugar rules are appended as dict comprehensions via .update())."""
    text = (APWORLD / "worlds" / "keen" / "Rules.py").read_text()
    env = {"dict": dict, "range": range}

    def _brace_expr(open_i):
        """Eval the {...} expression starting at the '{' index open_i."""
        depth = 0
        for j in range(open_i, len(text)):
            if text[j] == "{":
                depth += 1
            elif text[j] == "}":
                depth -= 1
                if depth == 0:
                    return eval(text[open_i:j + 1], env)  # noqa: S307
        raise ValueError("unbalanced braces")

    def block(name):
        result = _brace_expr(text.index("{", text.index(f"{name} = ")))
        marker = f"{name}.update("
        pos = 0
        while (i := text.find(marker, pos)) != -1:
            result.update(_brace_expr(text.index("{", i)))
            pos = i + len(marker)
        return result

    return block("ck4_points5k_rules"), block("ck5_points5k_rules")


# --------------------------------------------------------------------------- #
# Access-rule helpers                                                         #
# --------------------------------------------------------------------------- #
def signature(rule: dict) -> tuple:
    reqs = tuple(sorted(rule.get("requires", ())))
    gems = tuple(rule.get("gems", ()))
    return reqs, gems


def _req_suffix(sig: tuple) -> str:
    """' (Green Gem, Pogo)' style suffix for an access signature, or '' if the
    pickup has no requirements."""
    reqs, gems = sig
    bits = list(gems)
    if "pogo" in reqs:
        bits.append("Pogo")
    if "stunner" in reqs:
        bits.append("Stunner")
    return f" ({', '.join(bits)})" if bits else ""


def cluster_label(singular: str, plural: str, disps: list[int], sig: tuple) -> str:
    """Per-cluster node label, e.g. "Bags O' Sugar 7-10 (Pogo)" — the pickup
    display-number range plus the access-requirement suffix. Singular noun for a
    lone pickup; comma-joined runs for the (rare) non-contiguous cluster."""
    noun = singular if len(disps) == 1 else plural
    runs = ", ".join(f"{lo}" if lo == hi else f"{lo}-{hi}"
                     for lo, hi in _runs(sorted(disps)))
    return f"{noun} {runs}{_req_suffix(sig)}"


def access_rules(toggle: str, abbr: str, sig: tuple) -> list[str]:
    reqs, gems = sig
    base = [toggle]
    if abbr in SECRET_GATE:  # secret levels need their enable toggle too
        base.append(SECRET_GATE[abbr])
    if abbr in SECRET_REACHABLE:  # ...plus the cross-level entry prerequisite
        base.append(SECRET_REACHABLE[abbr])
    base.append(f"level_{abbr}")
    for tok in reqs:
        base.append(TOKEN_CODE[tok])
    if not gems:
        return [",".join(base)]

    def gem_code(g):
        # "Red Gem" -> red; "Red Gem 1" -> red1 (POTF's two reds / Korath's two
        # blues each have a trailing index that's part of the tracker item code).
        parts = g.split()
        num = parts[2] if len(parts) > 2 else ""
        return f"{abbr}_{parts[0].lower()}{num}"

    gem_codes = [gem_code(g) for g in gems]
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
        from render_level_maps import CROP
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
            map_name = EP_CFG[ap_ep]["map_prefix"] + ABBR[ap_ep][idx]
            img_path = maps_cfg.get(map_name)
            if img_path:
                iw, ih = Image.open(REPO / img_path).size
            # Use the same per-level crop the renderer applied to the image, so
            # pins land on the stamped sprites (CROP = (left, top, right, bottom)).
            left, top = CROP.get(map_name, (BORDER, BORDER, 1, 2))[:2]
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

            # per-inst signature + display number + pixel for non-excluded
            # pickups. The display number feeds the rule-dict lookup AND the
            # per-cluster node label (e.g. "Bags O' Sugar 7-10").
            info = {}
            for inst in range(count):
                if (lvl, inst) in excluded:
                    continue
                disp = display.get((lvl, inst), inst + 1)
                loc_name = f"{level_name} - {cfg['singular']} {disp}"
                info[inst] = {
                    "sig": signature(rules.get(loc_name, {})),
                    "disp": disp,
                    "px": level_px.get(inst, (24 + 18 * inst, 24)),
                }
            if not info:
                continue
            total += len(info)

            # One tracker node per *physical cluster*: within an access
            # signature, proximity-cluster the pickups, then emit a separate
            # node (own counter + single map pin) for each cluster. So every
            # map pin flips to "done" independently of pins elsewhere in the
            # level that share its access rule — collecting the bags by one
            # door no longer leaves a distant pin stuck. Nodes are named by the
            # pickup display-number range so the names stay unique and tell the
            # player exactly which bags ("Bags O' Sugar 7-10 (Pogo)").
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
                clusters = cluster([(i, info[i]["px"]) for i in members], CLUSTER_PX)
                clusters.sort(key=lambda c: min(c))  # stable, low-inst first
                for cl in clusters:
                    cl = sorted(cl)
                    sec = cluster_label(cfg["singular"], cfg["plural"],
                                        [info[i]["disp"] for i in cl], sig)
                    node = f"{level_name} - {sec}"
                    cx = round(sum(info[i]["px"][0] for i in cl) / len(cl))
                    cy = round(sum(info[i]["px"][1] for i in cl) / len(cl))
                    entries.append({
                        "name": node,
                        "map_locations": [{"map": map_name, "x": cx, "y": cy}],
                        "sections": [{
                            "name": sec,
                            "item_count": len(cl),
                            "access_rules": access_rules(cfg["toggle"], abbr, sig),
                        }],
                    })
                    # roll the section up into the level's overworld pin (mirrors
                    # the flask/keg ref). Top-level node => no "Keen N/" prefix.
                    refs_by_level.setdefault(level_name, []).append(f"{node}/{sec}")
                    for lo, hi in _runs(cl):
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

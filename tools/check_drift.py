#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
Catch drift between the tracker pack and the Commander Keen apworld.

The tracker hand-maintains item/location ID maps (scripts/autotracking.lua,
items/items.json) that must stay in lock-step with the apworld's Items.py /
Locations.py. When the apworld adds, removes, or renumbers a location, the
tracker silently goes stale (e.g. v0.0.9 added Cave of the Descendents flasks
to the location JSON but never wired them into autotracking's flask layout).
This script is the guardrail.

It loads the apworld's Items.py / Locations.py *in isolation* — BaseClasses is
stubbed so no Archipelago dependencies are needed — then compares:

  1. Items:     every AP item id has a `keen_<id>` code in items.json AND a
                key in autotracking.lua's ITEM_MAP (the reset list), with no
                stale entries in either.
  2. Locations: every AP level/gem/keycard/flask/keg id is covered by
                autotracking.lua's LOCATION_MAP (static entries + the
                CK4_FLASK_LAYOUT / CK5_KEG_LAYOUT loops), and none are stale.
  3. Counters:  SCORE_MAX.flask_count / keg_count match the number of
                flask / keg locations the apworld actually emits.

Pointsanity (5000-pt Ice Cream Cones / Bags O' Sugar) is intentionally NOT
tracked by the pack yet; those ids are reported as "known-unimplemented" and
do NOT fail the check. Remove them from KNOWN_UNIMPLEMENTED once tracked.

Usage:
    tools/check_drift.py                         # apworld at ../Archipelago-Keen
    tools/check_drift.py --apworld /path/to/repo
    KEEN_APWORLD=/path/to/repo tools/check_drift.py

Exit code is non-zero if any drift is found (pointsanity excepted).
"""

import argparse
import importlib.util
import json
import os
import re
import sys
import types
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


# --------------------------------------------------------------------------
# Load the apworld's Items.py / Locations.py without the Archipelago framework
# --------------------------------------------------------------------------
def load_apworld(apworld_root: Path):
    keen = apworld_root / "worlds" / "keen"
    if not (keen / "Locations.py").exists():
        sys.exit(f"error: no worlds/keen/Locations.py under {apworld_root}\n"
                 f"       pass --apworld or set KEEN_APWORLD")

    # Items.py / Locations.py only import BaseClasses; stub it.
    bc = types.ModuleType("BaseClasses")

    class _Base:  # stands in for Location / Item (used only as a base class)
        pass

    class ItemClassification:
        progression = useful = filler = trap = skip_balancing = 1

    bc.Location = _Base
    bc.Item = _Base
    bc.ItemClassification = ItemClassification
    sys.modules["BaseClasses"] = bc

    def load(name):
        spec = importlib.util.spec_from_file_location(name, keen / f"{name}.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    return load("Items"), load("Locations")


# --------------------------------------------------------------------------
# Apworld-side expectations
# --------------------------------------------------------------------------
def apworld_facts(Items, Locations):
    def ids(*region_maps):
        out = {}
        for rm in region_maps:
            for region in rm.values():
                out.update(region)  # {name: id}
        return {i: n for n, i in out.items()}  # {id: name}

    core = ids(Locations.ck4_locations_by_region, Locations.ck5_locations_by_region)
    flasks = ids(Locations.ck4_flask_locations_by_region)
    kegs = ids(Locations.ck5_keg_locations_by_region)
    points = ids(Locations.ck4_points5k_locations_by_region,
                 Locations.ck5_points5k_locations_by_region)
    return {
        "item_ids": {i: n for n, i in Items.item_name_to_id.items()},
        "core": core,
        "flasks": flasks,
        "kegs": kegs,
        "points": points,
    }


# --------------------------------------------------------------------------
# Tracker-side parsing
# --------------------------------------------------------------------------
def _matching_brace_block(text: str, start_marker: str) -> str:
    """Return the {...} block (inclusive) following start_marker."""
    i = text.index(start_marker)
    open_i = text.index("{", i)
    depth = 0
    for j in range(open_i, len(text)):
        c = text[j]
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return text[open_i:j + 1]
    raise ValueError(f"unbalanced braces after {start_marker!r}")


def parse_item_codes(items_json: Path) -> set[int]:
    data = json.loads(items_json.read_text())
    out = set()
    for entry in data:
        for code in str(entry.get("codes", "")).split(","):
            m = re.fullmatch(r"keen_(\d+)", code.strip())
            if m:
                out.add(int(m.group(1)))
    return out


def parse_item_map_ids(lua: str) -> set[int]:
    """AP item ids keyed in autotracking.lua's ITEM_MAP (the reset/enumeration
    list). onClear iterates these to reset items on connect, so a gap here means
    an item silently fails to reset."""
    block = _matching_brace_block(lua, "ITEM_MAP = ")
    return {int(m.group(1)) for m in re.finditer(r"\[(\d+)\]\s*=", block)}


def parse_location_ids(lua: str, loc_flask, loc_keg, ep_ck4, ep_ck5) -> set[int]:
    ids: set[int] = set()

    # 1. Static LOCATION_MAP literal: [12100] = "Keen 4/.../Complete"
    block = _matching_brace_block(lua, "LOCATION_MAP = ")
    for m in re.finditer(r"\[(\d+)\]\s*=\s*\"", block):
        ids.add(int(m.group(1)))

    # 2. Flask / keg layout loops. Parse [lvl] keys and their lo/hi segments,
    #    then reproduce the same id via the apworld's own loc_* builders so the
    #    formula is never duplicated here — we only assert *coverage* (which
    #    (lvl, idx) pairs the tracker routes).
    def layout_pairs(marker):
        b = _matching_brace_block(lua, marker)
        pairs = []
        level = None
        for tok in re.finditer(r"\[(\d+)\]\s*=|lo=(\d+),\s*hi=(\d+)", b):
            if tok.group(1) is not None:
                level = int(tok.group(1))
            else:
                lo, hi = int(tok.group(2)), int(tok.group(3))
                for idx in range(lo, hi + 1):
                    pairs.append((level, idx))
        return pairs

    for lvl, idx in layout_pairs("CK4_FLASK_LAYOUT = "):
        ids.add(loc_flask(ep_ck4, lvl, idx))
    for lvl, idx in layout_pairs("CK5_KEG_LAYOUT = "):
        ids.add(loc_keg(ep_ck5, lvl, idx))

    return ids


def parse_score_max(lua: str) -> dict[str, int]:
    m = re.search(r"SCORE_MAX\s*=\s*\{[^}]*flask_count\s*=\s*(\d+)[^}]*"
                  r"keg_count\s*=\s*(\d+)", lua)
    if not m:
        return {}
    return {"flask_count": int(m.group(1)), "keg_count": int(m.group(2))}


# --------------------------------------------------------------------------
# Reporting
# --------------------------------------------------------------------------
def report_set(label, missing, stale, id_to_name):
    problems = 0
    if missing:
        problems += len(missing)
        print(f"\n  ✗ {label}: {len(missing)} in apworld but NOT tracked")
        for i in sorted(missing):
            print(f"      missing  {i}  {id_to_name.get(i, '?')}")
    if stale:
        problems += len(stale)
        print(f"\n  ✗ {label}: {len(stale)} tracked but absent from apworld")
        for i in sorted(stale):
            print(f"      stale    {i}")
    if not missing and not stale:
        print(f"  ✓ {label}: in sync")
    return problems


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apworld", default=os.environ.get("KEEN_APWORLD",
                    str(REPO.parent / "Archipelago-Keen")),
                    help="path to the Archipelago-Keen checkout")
    args = ap.parse_args()

    Items, Locations = load_apworld(Path(args.apworld).resolve())
    apw = apworld_facts(Items, Locations)

    lua = (REPO / "scripts" / "autotracking.lua").read_text()
    tracker_items = parse_item_codes(REPO / "items" / "items.json")
    item_map_ids = parse_item_map_ids(lua)
    tracker_locs = parse_location_ids(
        lua, Locations.loc_flask, Locations.loc_keg,
        Locations.AP_EPISODE_CK4, Locations.AP_EPISODE_CK5)
    score_max = parse_score_max(lua)

    problems = 0
    print("=== Items ===")
    apw_item_ids = set(apw["item_ids"])
    problems += report_set("items.json codes", apw_item_ids - tracker_items,
                           tracker_items - apw_item_ids, apw["item_ids"])
    problems += report_set("autotracking ITEM_MAP", apw_item_ids - item_map_ids,
                           item_map_ids - apw_item_ids, apw["item_ids"])

    print("\n=== Locations (level / gem / keycard / flask / keg) ===")
    tracked_core = {**apw["core"], **apw["flasks"], **apw["kegs"]}
    expected = set(tracked_core)
    # only flag stale ids that aren't pointsanity (those are knowingly absent)
    stale = (tracker_locs - expected) - set(apw["points"])
    problems += report_set("locations", expected - tracker_locs, stale, tracked_core)

    print("\n=== Score counters ===")
    n_flask, n_keg = len(apw["flasks"]), len(apw["kegs"])
    for code, expected_n in (("flask_count", n_flask), ("keg_count", n_keg)):
        got = score_max.get(code)
        if got == expected_n:
            print(f"  ✓ SCORE_MAX.{code} = {got}")
        else:
            problems += 1
            print(f"  ✗ SCORE_MAX.{code} = {got}, apworld emits {expected_n}")

    print("\n=== Pointsanity (known-unimplemented, not failing) ===")
    tracked_points = tracker_locs & set(apw["points"])
    print(f"  ⚠ {len(apw['points'])} pointsanity locations in apworld, "
          f"{len(tracked_points)} tracked")
    print("    (5000-pt Ice Cream Cones / Bags O' Sugar — add tracking to "
          "remove this notice)")

    print()
    if problems:
        print(f"DRIFT: {problems} problem(s) found.")
        sys.exit(1)
    print("No drift. Tracker and apworld agree.")


if __name__ == "__main__":
    main()

# Commander Keen: Goodbye Galaxy - Archipelago PopTracker Pack

A PopTracker pack for the [Commander Keen "Goodbye Galaxy" Archipelago world](https://github.com/kodbyte/Archipelago-Keen) (Episodes 4 & 5).

## Features

- Full item tracking for Keen 4 and Keen 5
- Location tracking with logic matching the apworld rules
- Pogo Stick, Wetsuit, and gem/keycard requirements reflected in access logic
- Gemset support (a gemset unlocks all gems for a level at once)
- Optional secret levels (Pyramid of the Forbidden, Korath III Base) with their own maps, pins, and item panels — shown only when enabled in the seed
- Archipelago auto-tracking via AP connection
- Three variants: Both Episodes, Episode 4 Only, Episode 5 Only
- Both Keen 4 goals supported (read from slot data): the **Bean-With-Bacon
  Megarocket** goal (default) and the **Rescue all Oracles** goal

## Keen 4 goal

The Keen 4 victory icon follows the seed's `ck4_goal` option:

- **Megarocket** (default) — lights when the Bean-With-Bacon Megarocket is
  completed.
- **Rescue all Oracles** (`council_rescue`) — lights once all 8
  council-member levels are completed: The Perilous Pit, Cave of the
  Descendents, Crystalus, Lifewater Oasis, Pyramid of Shadows, Pyramid of the
  Gnosticine Ancients, Isle of Fire, and Well of Wishes. The Bean-With-Bacon
  Megarocket is not required for this goal. An **Oracles Rescued** counter on
  the items panel shows progress (`n/8`) and turns green at 8; it stays greyed
  under the Megarocket goal.

## Secret levels

If the seed enables them, the Pyramid of the Forbidden (Keen 4) and Korath III
Base (Keen 5) appear like any other level — overworld pin, level-map tab, and
entries in the Levels / Gems panels.

Note on their two same-coloured gems: the Pyramid of the Forbidden has two red
gems and Korath III Base has two blue gems. The game reports gem pickups by
colour only, so each pair is a **single** AP check shown at **both** gem spots —
grabbing either one marks both pins. You receive two separate gem items and need
both to open both doors. (This is expected, not a tracking bug.)

## Installation

1. Download the latest release (or this folder as a zip)
2. Place the zip or folder into your PopTracker `packs` directory:
   - Windows: `Documents/PopTracker/packs/`
   - Linux: `~/PopTracker/packs/`
   - macOS: `~/PopTracker/packs/`
3. Open PopTracker and select "Commander Keen: Goodbye Galaxy AP Tracker"
4. Choose your variant (Both, CK4 Only, or CK5 Only)

## Auto-Tracking

Click the "AP" button in PopTracker's menu bar, enter your Archipelago server address and slot name to enable auto-tracking. Items received and locations checked will sync automatically.

## Images

Icons in `images/` are drawn from the game's levels, items, and maps. A few
setting toggles still use a blank placeholder; you're welcome to swap any of
the PNGs for nicer art.

## Credits

- **apworld**: [kodbyte/Archipelago-Keen](https://github.com/kodbyte/Archipelago-Keen)
- **PopTracker**: [black-sliver/PopTracker](https://github.com/black-sliver/PopTracker)
- **Commander Keen**: id Software / Apogee
- [**Commander Keen Wiki**](https://keenwiki.shikadi.net/wiki/Main_Page)

#!/usr/bin/env python3
"""Render full Commander Keen 4/5 level maps from the original game data and
stamp pickups onto them at their exact in-game positions.

Currently produces two map sets (one PNG per level that contains the item):
  - pointsanity_maps/ : 5000-pt pickups (CK4 Ice Cream Cone / CK5 Bag O' Sugar)
  - extralife_maps/   : extra lives    (CK4 Lifewater Flask / CK5 Vitalin Keg)

Why render from scratch instead of reusing the tracker's level images?
The tracker's Ck?lv??.png images are cropped to varying, non-tile-aligned
bounding boxes, so pickup tile coordinates can't be mapped onto them reliably.
Rendering the maps ourselves at exactly 16px/tile with origin (0,0) makes the
mapping exact: pixel = (tileX*16, tileY*16).

Pickups are found by scanning the map itself (authoritative), in the same order
the game / AP client uses: info-layer spawns first (row-major), then foreground
tiles carrying the item's misc flag (row-major).

Inputs:
  - Game data:   <omnispeak>/bin/{EGADICT,EGAHEAD,GFXINFOE,Egagraph,MAPHEAD,
                                   Gamemaps,TILEINFO}.CK{4,5}
  - Cross-check: <apworld>/worlds/keen/docs/pointsanity_ck{4,5}.md (counts only)

Format references (omnispeak src/id_ca.c, id_ti.c):
  - Huffman (CAL_HuffExpand): 256-node dict, head node 254.
  - Carmack + RLEW for map planes.
  - Plane 0 = background -> opaque tiles16 (128B = 4 planes x 32).
    Plane 1 = foreground -> masked  tiles16m (160B = mask + 4 planes x 32).
    Plane 2 = info layer (sprite spawns; value 57+itemNumber).
  - Non-tile chunks (sprite table, sprites) carry a 4-byte expanded-length
    prefix in the compressed data (CAL_ExpandGrChunk).
  - TILEINFO foreground misc byte at tile + numTiles16*2 + numTiles16m*5.
"""
from __future__ import annotations

import re
import struct
from pathlib import Path

from PIL import Image

# ---- paths (edit if your checkouts live elsewhere) -------------------------
HERE = Path(__file__).resolve().parent
TRACKER = HERE.parent
OMNI_BIN = Path("/Users/joxtacy/PrivateProjects/omnispeak-ap/bin")
DOCS = Path("/Users/joxtacy/PrivateProjects/Archipelago-Keen/worlds/keen/docs")

TILE = 16
ITEM_INFO_BASE = 57  # info-plane value 57 == item 0; item N spawns at 57 + N

# Standard EGA 16-colour palette (R, G, B).
EGA = [
    (0x00, 0x00, 0x00), (0x00, 0x00, 0xAA), (0x00, 0xAA, 0x00), (0x00, 0xAA, 0xAA),
    (0xAA, 0x00, 0x00), (0xAA, 0x00, 0xAA), (0xAA, 0x55, 0x00), (0xAA, 0xAA, 0xAA),
    (0x55, 0x55, 0x55), (0x55, 0x55, 0xFF), (0x55, 0xFF, 0x55), (0x55, 0xFF, 0xFF),
    (0xFF, 0x55, 0x55), (0xFF, 0x55, 0xFF), (0xFF, 0xFF, 0x55), (0xFF, 0xFF, 0xFF),
]

# Playable levels: game map index -> display name (names kept stable so the
# 5000-pt output filenames don't change). Overworld/highscore maps are excluded.
LEVELS = {
    4: {
        1: "Border Village", 2: "Slug Village", 3: "The Perilous Pit",
        4: "Cave of the Descendents", 5: "Chasm of Chills", 6: "Crystalus",
        7: "Hilville", 8: "Sand Yego", 9: "Miragia", 10: "Lifewater Oasis",
        11: "Pyramid of the Moons", 12: "Pyramid of Shadows",
        13: "Pyramid of the Gnosticine Ancients", 14: "Pyramid of the Forbidden",
        15: "Isle of Tar", 16: "Isle of Fire", 17: "Well of Wishes",
        18: "BWB Megarocket",
    },
    5: {
        1: "Ion Ventilation System", 2: "Security Center",
        3: "Defense Tunnel Vlook", 4: "Energy Flow Systems",
        5: "Defense Tunnel Burrh", 6: "Regulation Control Center",
        7: "Defense Tunnel Sorra", 8: "Neutrino Burst Injector",
        9: "Defense Tunnel Teln", 10: "Brownian Motion Inducer",
        11: "Gravitational Damping Hub", 12: "Quantum Explosion Dynamo",
        13: "Korath III Base",
    },
}

# Item types to render. `misc` = foreground TILEINFO misc flag; `item` = info-layer
# item number (info value = 57 + item); `sprite` = EGAGRAPH sprite chunk to use
# when an episode has no foreground tile for the item (CK5 keg is info-only).
ITEMS = [
    {
        "out": "pointsanity_maps", "misc": 26, "item": 9,
        "names": {4: "Ice Cream Cone", 5: "Bag O' Sugar"},
        "sprite": {}, "worksheet": True,
    },
    {
        "out": "extralife_maps", "misc": 27, "item": 10,
        "names": {4: "Lifewater Flask", 5: "Vitalin Keg"},
        "sprite": {5: 222}, "worksheet": False,
    },
]


# --------------------------------------------------------------------------- #
# Decompressors                                                               #
# --------------------------------------------------------------------------- #
def huff_expand(src: bytes, explen: int, table: list[tuple[int, int]]) -> bytes:
    out = bytearray()
    head = 254
    bit = 1
    si = 0
    cur = src[si]
    si += 1
    while len(out) < explen:
        head = table[head][1] if (cur & bit) else table[head][0]
        if head > 255:
            head -= 256
        else:
            out.append(head)
            head = 254
            if len(out) == explen:
                break
        bit <<= 1
        if bit == 256:
            if si >= len(src):
                break
            cur = src[si]
            si += 1
            bit = 1
    return bytes(out)


def carmack_expand(src: bytes, explen: int) -> bytes:
    out = bytearray()
    i = 0
    while len(out) < explen:
        lo, hi = src[i], src[i + 1]
        i += 2
        if hi == 0xA7 and lo:           # near pointer
            off = src[i]
            i += 1
            start = len(out) - off * 2
            for k in range(lo * 2):
                out.append(out[start + k])
        elif hi == 0xA8 and lo:         # far pointer
            off = src[i] | (src[i + 1] << 8)
            i += 2
            start = off * 2
            for k in range(lo * 2):
                out.append(out[start + k])
        elif hi == 0xA7 and not lo:     # near exception
            out.append(src[i])
            out.append(0xA7)
            i += 1
        elif hi == 0xA8 and not lo:     # far exception
            out.append(src[i])
            out.append(0xA8)
            i += 1
        else:
            out.append(lo)
            out.append(hi)
    return bytes(out[:explen])


def rlew_expand(src: bytes, explen: int, tag: int) -> bytes:
    out = bytearray()
    i = 0
    while len(out) < explen and i + 1 < len(src):
        w = src[i] | (src[i + 1] << 8)
        i += 2
        if w == tag:
            cnt = src[i] | (src[i + 1] << 8)
            val = src[i + 2] | (src[i + 3] << 8)
            i += 4
            out += struct.pack("<H", val) * cnt
        else:
            out += struct.pack("<H", w)
    return bytes(out[:explen])


# --------------------------------------------------------------------------- #
# Graphics archive                                                            #
# --------------------------------------------------------------------------- #
GFX_FIELDS = [
    "numTiles8", "numTiles8m", "numTiles16", "numTiles16m", "numTiles32", "numTiles32m",
    "offTiles8", "offTiles8m", "offTiles16", "offTiles16m", "offTiles32", "offTiles32m",
    "numBitmaps", "numMasked", "numSprites", "offBitmaps", "offMasked", "offSprites",
    "hdrBitmaps", "hdrMasked", "hdrSprites", "numBinaries", "offBinaries",
]


class Graphics:
    def __init__(self, ep: int):
        b = OMNI_BIN
        dict_bytes = (b / f"EGADICT.CK{ep}").read_bytes()
        self.table = [struct.unpack_from("<HH", dict_bytes, i * 4) for i in range(256)]
        self.head = (b / f"EGAHEAD.CK{ep}").read_bytes()
        self.graph = (b / f"Egagraph.ck{ep}").read_bytes()
        info = struct.unpack_from("<23H", (b / f"GFXINFOE.CK{ep}").read_bytes())
        self.gfx = dict(zip(GFX_FIELDS, info))
        self.nchunks = len(self.head) // 3
        self._tile16: dict[int, list[int]] = {}
        self._tile16m: dict[int, tuple[list[int], list[bool]]] = {}
        self._sprite_table: bytes | None = None
        # TILEINFO: foreground "misc" byte at tile + numTiles16*2 + numTiles16m*5
        self.tileinfo = (b / f"TILEINFO.CK{ep}").read_bytes()
        self._fore_misc_base = self.gfx["numTiles16"] * 2 + self.gfx["numTiles16m"] * 5

    # -- tile attributes --
    def fore_misc(self, tile: int) -> int:
        i = self._fore_misc_base + tile
        return self.tileinfo[i] & 0x7F if i < len(self.tileinfo) else 0

    def first_misc_tile(self, misc: int) -> int | None:
        for t in range(self.gfx["numTiles16m"]):
            if self.fore_misc(t) == misc:
                return t
        return None

    # -- chunk access --
    def chunk_start(self, c: int) -> int:
        o = c * 3
        if o + 2 >= len(self.head):
            return -1
        v = self.head[o] | (self.head[o + 1] << 8) | (self.head[o + 2] << 16)
        return -1 if v == 0xFFFFFF else v

    def chunk_complen(self, c: int) -> int:
        nxt = c + 1
        while nxt < self.nchunks and self.chunk_start(nxt) == -1:
            nxt += 1
        end = self.chunk_start(nxt) if nxt < self.nchunks else len(self.graph)
        return end - self.chunk_start(c)

    def chunk(self, c: int, explen: int) -> bytes:
        start = self.chunk_start(c)
        comp = self.graph[start:start + self.chunk_complen(c)]
        return huff_expand(comp, explen, self.table)

    def chunk_prefixed(self, c: int) -> bytes:
        """Decode a chunk whose expanded length is a 4-byte prefix (sprite table,
        sprites, binaries) rather than a fixed tile size."""
        start = self.chunk_start(c)
        comp = self.graph[start:start + self.chunk_complen(c)]
        explen = struct.unpack_from("<I", comp)[0]
        return huff_expand(comp[4:], explen, self.table)

    # -- graphics --
    def tile16(self, idx: int) -> list[int]:
        """Opaque background tile -> 256 palette indices (row-major)."""
        if idx in self._tile16:
            return self._tile16[idx]
        if self.chunk_start(self.gfx["offTiles16"] + idx) == -1:  # unused slot
            self._tile16[idx] = [0] * 256
            return self._tile16[idx]
        data = self.chunk(self.gfx["offTiles16"] + idx, 128)  # 4 planes x 32B
        px = [0] * 256
        for y in range(16):
            for bx in range(2):
                base = y * 2 + bx
                for bit in range(8):
                    mask = 0x80 >> bit
                    col = 0
                    for p in range(4):
                        if data[p * 32 + base] & mask:
                            col |= 1 << p
                    px[y * 16 + bx * 8 + bit] = col
        self._tile16[idx] = px
        return px

    def tile16m(self, idx: int) -> tuple[list[int], list[bool]]:
        """Masked foreground tile -> (palette indices, transparency mask)."""
        if idx in self._tile16m:
            return self._tile16m[idx]
        if self.chunk_start(self.gfx["offTiles16m"] + idx) == -1:  # unused slot
            self._tile16m[idx] = ([0] * 256, [True] * 256)
            return self._tile16m[idx]
        data = self.chunk(self.gfx["offTiles16m"] + idx, 160)  # mask + 4 planes
        px = [0] * 256
        clear = [False] * 256
        for y in range(16):
            for bx in range(2):
                base = y * 2 + bx
                for bit in range(8):
                    mask = 0x80 >> bit
                    transparent = bool(data[base] & mask)           # plane 0 = mask
                    col = 0
                    for p in range(4):
                        if data[(p + 1) * 32 + base] & mask:
                            col |= 1 << p
                    i = y * 16 + bx * 8 + bit
                    px[i] = col
                    clear[i] = transparent
        self._tile16m[idx] = (px, clear)
        return self._tile16m[idx]

    def tile16m_rgba(self, idx: int) -> Image.Image:
        px, clear = self.tile16m(idx)
        img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
        sp = img.load()
        for y in range(16):
            for x in range(16):
                i = y * 16 + x
                if not clear[i]:
                    sp[x, y] = (*EGA[px[i]], 255)
        return img

    def sprite_rgba(self, chunk: int) -> Image.Image:
        """Decode a masked EGAGRAPH sprite (mask + 4 colour planes) to RGBA."""
        if self._sprite_table is None:
            self._sprite_table = self.chunk_prefixed(self.gfx["hdrSprites"])
        sn = chunk - self.gfx["offSprites"]
        w, h = struct.unpack_from("<HH", self._sprite_table, sn * 18)  # width in bytes
        data = self.chunk_prefixed(chunk)  # w*h*5 (mask + 4 colour planes)
        plane = w * h
        img = Image.new("RGBA", (w * 8, h), (0, 0, 0, 0))
        sp = img.load()
        for y in range(h):
            for bx in range(w):
                base = y * w + bx
                for bit in range(8):
                    m = 0x80 >> bit
                    if data[base] & m:                    # mask set -> transparent
                        continue
                    col = sum(1 << p for p in range(4) if data[(p + 1) * plane + base] & m)
                    sp[bx * 8 + bit, y] = (*EGA[col], 255)
        return img

    def item_graphic(self, misc: int, sprite_chunk: int | None) -> Image.Image:
        """The item's icon: its foreground tile if one carries `misc`, else the
        configured EGAGRAPH sprite."""
        t = self.first_misc_tile(misc)
        if t is not None:
            return self.tile16m_rgba(t)
        if sprite_chunk is not None:
            return self.sprite_rgba(sprite_chunk)
        raise RuntimeError(f"no graphic for misc {misc}")


# --------------------------------------------------------------------------- #
# Maps                                                                        #
# --------------------------------------------------------------------------- #
class Maps:
    def __init__(self, ep: int):
        mh = (OMNI_BIN / f"MAPHEAD.CK{ep}").read_bytes()
        self.gm = (OMNI_BIN / f"Gamemaps.ck{ep}").read_bytes()
        self.tag = struct.unpack_from("<H", mh)[0]
        self.offs = struct.unpack_from("<100i", mh, 2)

    def _plane(self, poff: int, plen: int, w: int, h: int) -> tuple[int, ...]:
        raw = self.gm[poff:poff + plen]
        explen = struct.unpack_from("<H", raw)[0]
        car = carmack_expand(raw[2:], explen)
        rl = rlew_expand(car, w * h * 2, self.tag)
        return struct.unpack(f"<{w * h}H", rl[: w * h * 2])

    def load(self, idx: int):
        o = self.offs[idx]
        po = struct.unpack_from("<3i", self.gm, o)
        pl = struct.unpack_from("<3H", self.gm, o + 12)
        w, h = struct.unpack_from("<2H", self.gm, o + 18)
        bg = self._plane(po[0], pl[0], w, h)
        fg = self._plane(po[1], pl[1], w, h)
        info = self._plane(po[2], pl[2], w, h)
        return w, h, bg, fg, info


def render_map(gfx: Graphics, w: int, h: int, bg, fg) -> Image.Image:
    img = Image.new("RGB", (w * TILE, h * TILE))
    pix = img.load()
    for ty in range(h):
        for tx in range(w):
            t = ty * w + tx
            back = gfx.tile16(bg[t])
            fi = fg[t]
            fore = gfx.tile16m(fi) if fi else None
            ox, oy = tx * TILE, ty * TILE
            for y in range(16):
                for x in range(16):
                    p = y * 16 + x
                    col = back[p]
                    if fore is not None and not fore[1][p]:
                        col = fore[0][p]
                    pix[ox + x, oy + y] = EGA[col]
    return img


# --------------------------------------------------------------------------- #
# Pickup scan + worksheet cross-check                                         #
# --------------------------------------------------------------------------- #
def scan_pickups(gfx: Graphics, w: int, h: int, fg, info, misc: int, item: int) -> list[dict]:
    """Pickups in AP/client scan order: info-layer spawns first (row-major),
    then foreground tiles carrying `misc` (row-major)."""
    info_val = ITEM_INFO_BASE + item
    picks: list[dict] = []
    for y in range(h):
        for x in range(w):
            if info[y * w + x] == info_val:
                picks.append({"x": x, "y": y})
    for y in range(h):
        for x in range(w):
            if gfx.fore_misc(fg[y * w + x]) == misc:
                picks.append({"x": x, "y": y})
    return picks


ROW_RE = re.compile(r"^\|\s*(\d+)\s*\|\s*\(\s*(\d+),\s*(\d+)\)\s*\|\s*(\w+)")


def worksheet_counts(ep: int) -> dict[str, int]:
    path = DOCS / f"pointsanity_ck{ep}.md"
    if not path.exists():
        return {}
    counts: dict[str, int] = {}
    cur = None
    for line in path.read_text().splitlines():
        if line.startswith("## "):
            cur = re.sub(r"\s*\(.*\)\s*$", "", line[3:]).strip()
            counts[cur] = 0
        elif cur is not None and ROW_RE.match(line):
            counts[cur] += 1
    return counts


# --------------------------------------------------------------------------- #
# Main                                                                        #
# --------------------------------------------------------------------------- #
def main():
    total = 0
    for ep in (4, 5):
        gfx = Graphics(ep)
        maps = Maps(ep)
        base_cache: dict[int, Image.Image] = {}
        for item in ITEMS:
            out_dir = TRACKER / item["out"]
            out_dir.mkdir(parents=True, exist_ok=True)
            icon = item["item_graphic"] = gfx.item_graphic(item["misc"], item["sprite"].get(ep))
            iw, ih = icon.size
            counts = worksheet_counts(ep) if item["worksheet"] else {}
            for idx, name in LEVELS[ep].items():
                w, h, bg, fg, info = maps.load(idx)
                picks = scan_pickups(gfx, w, h, fg, info, item["misc"], item["item"])
                if not picks:
                    continue
                exp = counts.get(name)
                if exp is not None and exp != len(picks):
                    print(f"  ! CK{ep} {name}: scan {len(picks)} != worksheet {exp}")
                if idx not in base_cache:
                    base_cache[idx] = render_map(gfx, w, h, bg, fg).convert("RGBA")
                img = base_cache[idx].copy()
                for p in picks:
                    cx = p["x"] * TILE + TILE // 2
                    cy = p["y"] * TILE + TILE // 2
                    img.paste(icon, (cx - iw // 2, cy - ih // 2), icon)
                slug = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")
                out = out_dir / f"ck{ep}_{slug}.png"
                img.convert("RGB").save(out)
                total += 1
                print(f"  CK{ep} {name}: {len(picks)} {item['names'][ep]}(s) -> {item['out']}/{out.name}")
    print(f"\nWrote {total} maps. Each pickup is stamped with its in-game sprite at native scale.")


if __name__ == "__main__":
    main()

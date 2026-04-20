#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["websockets"]
# ///
"""
Drive the Keen PopTracker pack's auto map switching without the game.

Connects to an Archipelago server and pushes DataStorage `Set` operations
against `keen_current_level_<slot_id>` so the tracker's onMapChange
handler fires.

Usage (uv auto-installs deps):
    uv run tools/test_map_switch.py --uri ws://archipelago.gg:38281 --slot MySlot [--password p]

Or if you prefer pip:
    pip install websockets
    python tools/test_map_switch.py --uri ws://archipelago.gg:38281 --slot MySlot

Then at the REPL, enter "<episode> <level>" per line:
    1 0     # CK4 Overworld
    1 6     # CK4 Crystalus
    2 12    # CK5 QED
    q       # quit

Episodes: 1=CK4, 2=CK5. Level 0 is the overworld. Level numbers match
CK4_MAP_TABS / CK5_MAP_TABS in scripts/autotracking.lua.

Note: don't run this while the real game is connected to the same slot —
AP will boot one of them.
"""

import argparse
import asyncio
import json
import sys

import websockets


async def recv_until(ws, cmd):
    while True:
        for pkt in json.loads(await ws.recv()):
            if pkt.get("cmd") == cmd:
                return pkt
            if pkt.get("cmd") == "ConnectionRefused":
                raise SystemExit(f"ConnectionRefused: {pkt.get('errors')}")


async def run(uri, slot, password, game):
    async with websockets.connect(uri, max_size=None) as ws:
        await recv_until(ws, "RoomInfo")
        await ws.send(json.dumps([{
            "cmd": "Connect",
            "game": game,
            "name": slot,
            "password": password,
            "uuid": "keen-tracker-test",
            "version": {"major": 0, "minor": 5, "build": 0, "class": "Version"},
            "items_handling": 0,
            "tags": ["TextOnly"],
            "slot_data": False,
        }]))
        connected = await recv_until(ws, "Connected")
        slot_id = connected["slot"]
        key = f"keen_current_level_{slot_id}"
        print(f"connected, slot_id={slot_id}, key={key}")
        print("enter '<episode> <level>' (or 'q'):")

        loop = asyncio.get_event_loop()
        while True:
            line = (await loop.run_in_executor(None, sys.stdin.readline)).strip()
            if not line or line == "q":
                return
            try:
                ep, lvl = map(int, line.split())
            except ValueError:
                print("expected: <episode> <level>")
                continue
            await ws.send(json.dumps([{
                "cmd": "Set",
                "key": key,
                "default": None,
                "want_reply": False,
                "operations": [{"operation": "replace",
                                "value": {"level": lvl, "episode": ep}}],
            }]))
            print(f"  -> Set {key} = {{level: {lvl}, episode: {ep}}}")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--uri", required=True,
                   help="ws://host:port or wss://host:port")
    p.add_argument("--slot", required=True)
    p.add_argument("--password", default="")
    p.add_argument("--game", default="Commander Keen")
    args = p.parse_args()
    try:
        asyncio.run(run(args.uri, args.slot, args.password, args.game))
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()

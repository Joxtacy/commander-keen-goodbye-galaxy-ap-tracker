# Render every tracker level map from the game data and stamp all collectibles
# (gems, keycards, point + extra-life pickups). Fully reproduces images/Ck?lv??.png
# (needs the omnispeak game data that tools/render_pointsanity_maps.py points at).
render-maps:
    python3 tools/render_level_maps.py

zip:
    zip -r keen_goodbye_galaxy_ap_tracker.zip manifest.json versions.json items/ locations/ maps/ layouts/ scripts/ images/ -x "*.jj/*" "*.git/*" "*.claude/*" "scripts/map_coords.py"

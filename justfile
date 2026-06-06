# Stamp the real in-game pickup sprites onto the tracker level maps.
# Re-renders images/Ck?lv??.png from the pristine art in images/_base_levels/,
# auto-aligning each level against the game render (needs the omnispeak game data
# that tools/render_pointsanity_maps.py points at).
overlay-maps:
    python3 tools/overlay_pickups_on_maps.py

zip:
    zip -r keen_goodbye_galaxy_ap_tracker.zip manifest.json versions.json items/ locations/ maps/ layouts/ scripts/ images/ -x "*.jj/*" "*.git/*" "*.claude/*" "scripts/map_coords.py" "images/_base_levels/*"

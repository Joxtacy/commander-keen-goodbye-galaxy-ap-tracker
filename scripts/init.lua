-- Commander Keen: Goodbye Galaxy AP Tracker
-- init.lua

-- Load items
Tracker:AddItems("items/items.json")

-- Load logic helpers (Lua access rule functions used by locations)
ScriptHost:LoadScript("scripts/logic.lua")

-- Load locations and layout based on variant
local variant = Tracker.ActiveVariantUID

if variant == "ck4_only" then
    Tracker:AddLocations("locations/keen4_locations.json")
    Tracker:AddLocations("locations/keen4_level_maps.json")
    Tracker:AddLocations("locations/keen4_cone_locations.json")
    Tracker:AddMaps("maps/keen4_maps.json")
    Tracker:AddLayouts("layouts/tracker_ck4.json")
elseif variant == "ck5_only" then
    Tracker:AddLocations("locations/keen5_locations.json")
    Tracker:AddLocations("locations/keen5_level_maps.json")
    Tracker:AddLocations("locations/keen5_sugar_locations.json")
    Tracker:AddMaps("maps/keen5_maps.json")
    Tracker:AddLayouts("layouts/tracker_ck5.json")
else
    -- "both" variant (default)
    Tracker:AddLocations("locations/keen4_locations.json")
    Tracker:AddLocations("locations/keen4_level_maps.json")
    Tracker:AddLocations("locations/keen4_cone_locations.json")
    Tracker:AddLocations("locations/keen5_locations.json")
    Tracker:AddLocations("locations/keen5_level_maps.json")
    Tracker:AddLocations("locations/keen5_sugar_locations.json")
    Tracker:AddMaps("maps/keen4_maps.json")
    Tracker:AddMaps("maps/keen5_maps.json")
    Tracker:AddLayouts("layouts/tracker_both.json")
end

-- Load AP autotracking. manifest.json already requires PopTracker >= 0.25.4,
-- which is well past the version that introduced AP support, so load it
-- unconditionally rather than re-checking PopVersion (a lexicographic string
-- compare that is both fragile and redundant here).
ScriptHost:LoadScript("scripts/autotracking.lua")

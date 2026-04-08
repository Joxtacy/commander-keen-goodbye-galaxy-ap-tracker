-- autotracking.lua
-- Archipelago auto-tracking for Commander Keen: Goodbye Galaxy

-- Episode selection from slot_data (0=both, 1=ck4, 2=ck5)
EPISODE_SELECT = 0
-- Gemsets setting from slot_data (0=off, 1=on)
ENABLE_GEMSETS = 1

-- Final level location IDs for victory tracking
CK4_VICTORY_LOCATION = 13800 -- Bean-With-Bacon Megarocket Complete
CK5_VICTORY_LOCATION = 15200 -- Quantum Explosion Dynamo Complete

-- Individual gem codes (for initializing progressive stages)
-- Map AP item IDs to PopTracker item codes
ITEM_MAP = {
	-- Common items
	[101] = "pogo",
	[102] = "stunner",

	-- CK4 unique items
	[103] = "wetsuit",

	-- CK4 level items
	[1001] = "level_bv",
	[1002] = "level_sv",
	[1003] = "level_pp",
	[1004] = "level_cotd",
	[1005] = "level_coc",
	[1006] = "level_crys",
	[1007] = "level_hil",
	[1008] = "level_sy",
	[1009] = "level_mir",
	[1010] = "level_lo",
	[1011] = "level_potm",
	[1012] = "level_pos",
	[1013] = "level_potga",
	[1015] = "level_iot",
	[1016] = "level_iof",
	[1017] = "level_wow",
	[1018] = "level_bwbm",

	-- CK4 gem items
	[100300] = "pp_red",
	[100302] = "pp_blue",
	[100400] = "cotd_red",
	[100401] = "cotd_yellow",
	[100600] = "crys_red",
	[100601] = "crys_yellow",
	[100602] = "crys_blue",
	[100603] = "crys_green",
	[100803] = "sy_green",
	[101003] = "lo_green",
	[101101] = "potm_yellow",
	[101202] = "pos_blue",
	[101300] = "potga_red",
	[101303] = "potga_green",
	[101500] = "iot_red",
	[101501] = "iot_yellow",
	[101502] = "iot_blue",
	[101601] = "iof_yellow",
	[101602] = "iof_blue",

	-- CK4 gemset items
	[100399] = "pp_gemset",
	[100499] = "cotd_gemset",
	[100699] = "crys_gemset",
	[100899] = "sy_gemset",
	[101099] = "lo_gemset",
	[101199] = "potm_gemset",
	[101299] = "pos_gemset",
	[101399] = "potga_gemset",
	[101599] = "iot_gemset",
	[101699] = "iof_gemset",

	-- CK5 level items
	[2001] = "level_ivs",
	[2002] = "level_sc",
	[2003] = "level_dtv",
	[2004] = "level_efs",
	[2005] = "level_dtb",
	[2006] = "level_rcc",
	[2007] = "level_dts",
	[2008] = "level_nbi",
	[2009] = "level_dtt",
	[2010] = "level_bmi",
	[2011] = "level_gdh",
	[2012] = "level_qed",

	-- CK5 gem items
	[200200] = "sc_red",
	[200202] = "sc_blue",
	[200300] = "dtv_red",
	[200301] = "dtv_yellow",
	[200400] = "efs_red",
	[200401] = "efs_yellow",
	[200402] = "efs_blue",
	[200403] = "efs_green",
	[200500] = "dtb_red",
	[200501] = "dtb_yellow",
	[200502] = "dtb_blue",
	[200503] = "dtb_green",
	[200600] = "rcc_red",
	[200601] = "rcc_yellow",
	[200602] = "rcc_blue",
	[200701] = "dts_yellow",
	[200800] = "nbi_red",
	[200802] = "nbi_blue",
	[200900] = "dtt_red",
	[200901] = "dtt_yellow",
	[200902] = "dtt_blue",
	[200903] = "dtt_green",
	[201001] = "bmi_yellow",
	[201002] = "bmi_blue",
	[201100] = "gdh_red",
	[201103] = "gdh_green",
	[201200] = "qed_red",
	[201201] = "qed_yellow",
	[201202] = "qed_blue",
	[201203] = "qed_green",

	-- CK5 keycard items
	[200204] = "sc_keycard",
	[200304] = "dtv_keycard",
	[200504] = "dtb_keycard",
	[200704] = "dts_keycard",
	[200904] = "dtt_keycard",
	[201104] = "gdh_keycard",

	-- CK5 gemset items
	[200299] = "sc_gemset",
	[200399] = "dtv_gemset",
	[200499] = "efs_gemset",
	[200599] = "dtb_gemset",
	[200699] = "rcc_gemset",
	[200799] = "dts_gemset",
	[200899] = "nbi_gemset",
	[200999] = "dtt_gemset",
	[201099] = "bmi_gemset",
	[201199] = "gdh_gemset",
	[201299] = "qed_gemset",

	-- Filler
	[900] = "extra_keen",
	[901] = "stunner_ammo",
}

-- Map AP location IDs to PopTracker location names
-- Built from Locations.py: loc_level_complete / loc_keygem / loc_keycard formulas
LOCATION_MAP = {
	-- CK4 level completes
	[12100] = "Border Village/Complete",
	[12200] = "Slug Village/Complete",
	[12300] = "The Perilous Pit/Complete",
	[12400] = "Cave of the Descendents/Complete",
	[12500] = "Chasm of Chills/Complete",
	[12600] = "Crystalus/Complete",
	[12700] = "Hilville/Complete",
	[12800] = "Sand Yego/Complete",
	[12900] = "Miragia/Complete",
	[13000] = "Lifewater Oasis/Complete",
	[13100] = "Pyramid of the Moons/Complete",
	[13200] = "Pyramid of Shadows/Complete",
	[13300] = "Pyramid of the Gnosticine Ancients/Complete",
	[13500] = "Isle of Tar/Complete",
	[13600] = "Isle of Fire/Complete",
	[13700] = "Well of Wishes/Complete",
	[13800] = "Bean-With-Bacon Megarocket/Complete",
	-- CK4 gems
	[22300] = "The Perilous Pit/Red Gem",
	[22302] = "The Perilous Pit/Blue Gem",
	[22400] = "Cave of the Descendents/Red Gem",
	[22401] = "Cave of the Descendents/Yellow Gem",
	[22600] = "Crystalus/Red Gem",
	[22601] = "Crystalus/Yellow Gem",
	[22602] = "Crystalus/Blue Gem",
	[22603] = "Crystalus/Green Gem",
	[22803] = "Sand Yego/Green Gem",
	[23003] = "Lifewater Oasis/Green Gem",
	[23101] = "Pyramid of the Moons/Yellow Gem",
	[23202] = "Pyramid of Shadows/Blue Gem",
	[23300] = "Pyramid of the Gnosticine Ancients/Red Gem",
	[23303] = "Pyramid of the Gnosticine Ancients/Green Gem",
	[23500] = "Isle of Tar/Red Gem",
	[23501] = "Isle of Tar/Yellow Gem",
	[23502] = "Isle of Tar/Blue Gem",
	[23601] = "Isle of Fire/Yellow Gem",
	[23602] = "Isle of Fire/Blue Gem",
	-- CK5 level completes
	[14100] = "Ion Ventilation System/Complete",
	[14200] = "Security Center/Complete",
	[14300] = "Defense Tunnel Vlook/Complete",
	[14400] = "Energy Flow Systems/Complete",
	[14500] = "Defense Tunnel Burrh/Complete",
	[14600] = "Regulation Control Center/Complete",
	[14700] = "Defense Tunnel Sorra/Complete",
	[14800] = "Neutrino Burst Injector/Complete",
	[14900] = "Defense Tunnel Teln/Complete",
	[15000] = "Brownian Motion Inducer/Complete",
	[15100] = "Gravitational Damping Hub/Complete",
	[15200] = "Quantum Explosion Dynamo/Complete",
	-- CK5 gems
	[24200] = "Security Center/Red Gem",
	[24202] = "Security Center/Blue Gem",
	[24300] = "Defense Tunnel Vlook/Red Gem",
	[24301] = "Defense Tunnel Vlook/Yellow Gem",
	[24400] = "Energy Flow Systems/Red Gem",
	[24401] = "Energy Flow Systems/Yellow Gem",
	[24402] = "Energy Flow Systems/Blue Gem",
	[24403] = "Energy Flow Systems/Green Gem",
	[24500] = "Defense Tunnel Burrh/Red Gem",
	[24501] = "Defense Tunnel Burrh/Yellow Gem",
	[24502] = "Defense Tunnel Burrh/Blue Gem",
	[24503] = "Defense Tunnel Burrh/Green Gem",
	[24600] = "Regulation Control Center/Red Gem",
	[24601] = "Regulation Control Center/Yellow Gem",
	[24602] = "Regulation Control Center/Blue Gem",
	[24701] = "Defense Tunnel Sorra/Yellow Gem",
	[24800] = "Neutrino Burst Injector/Red Gem",
	[24802] = "Neutrino Burst Injector/Blue Gem",
	[24900] = "Defense Tunnel Teln/Red Gem",
	[24901] = "Defense Tunnel Teln/Yellow Gem",
	[24902] = "Defense Tunnel Teln/Blue Gem",
	[24903] = "Defense Tunnel Teln/Green Gem",
	[25001] = "Brownian Motion Inducer/Yellow Gem",
	[25002] = "Brownian Motion Inducer/Blue Gem",
	[25100] = "Gravitational Damping Hub/Red Gem",
	[25103] = "Gravitational Damping Hub/Green Gem",
	[25200] = "Quantum Explosion Dynamo/Red Gem",
	[25201] = "Quantum Explosion Dynamo/Yellow Gem",
	[25202] = "Quantum Explosion Dynamo/Blue Gem",
	[25203] = "Quantum Explosion Dynamo/Green Gem",
	-- CK5 keycards
	[34200] = "Security Center/Keycard",
	[34300] = "Defense Tunnel Vlook/Keycard",
	[34500] = "Defense Tunnel Burrh/Keycard",
	[34700] = "Defense Tunnel Sorra/Keycard",
	[34900] = "Defense Tunnel Teln/Keycard",
	[35100] = "Gravitational Damping Hub/Keycard",
}

-- ============================================================
-- Handlers
-- ============================================================

function onClear(slot_data)
	-- Read settings from slot_data
	if slot_data and slot_data["episode_select"] then
		EPISODE_SELECT = slot_data["episode_select"]
	else
		EPISODE_SELECT = 0
	end

	if slot_data and slot_data["enable_gemsets"] ~= nil then
		ENABLE_GEMSETS = slot_data["enable_gemsets"]
	else
		ENABLE_GEMSETS = 1
	end

	-- Set the gemsets setting toggle
	local gemsets_setting = Tracker:FindObjectForCode("gemsets")
	if gemsets_setting then
		gemsets_setting.Active = (ENABLE_GEMSETS == 1)
	end

	-- Reset all tracked items
	for _, code in pairs(ITEM_MAP) do
		local obj = Tracker:FindObjectForCode(code)
		if obj then
			if obj.Type == "toggle" or obj.Type == "toggle_badged" then
				obj.Active = false
			elseif obj.Type == "progressive" then
				obj.CurrentStage = 0
			elseif obj.Type == "consumable" then
				obj.AcquiredCount = 0
			end
		end
	end

	-- Reset victory items
	for _, code in ipairs({ "ck4_victory", "ck5_victory" }) do
		local obj = Tracker:FindObjectForCode(code)
		if obj then
			obj.Active = false
		end
	end

	-- Reset all locations
	for _, loc_path in pairs(LOCATION_MAP) do
		local loc = Tracker:FindObjectForCode("@" .. loc_path)
		if loc then
			loc.AvailableChestCount = loc.ChestCount
		end
	end
end

function onItem(index, item_id, item_name, player_number)
	local code = ITEM_MAP[item_id]
	if not code then
		-- print("Unknown item ID: " .. tostring(item_id))
		return
	end

	local obj = Tracker:FindObjectForCode(code)
	if not obj then
		-- print("Could not find object for code: " .. code)
		return
	end

	if obj.Type == "toggle" or obj.Type == "toggle_badged" then
		obj.Active = true
	elseif obj.Type == "progressive" then
		obj.CurrentStage = obj.CurrentStage + 1
	elseif obj.Type == "consumable" then
		obj.AcquiredCount = obj.AcquiredCount + 1
	end
end

function onLocation(location_id, location_name)
	local loc_path = LOCATION_MAP[location_id]
	if not loc_path then
		-- print("Unknown location ID: " .. tostring(location_id))
		return
	end

	local loc = Tracker:FindObjectForCode("@" .. loc_path)
	if loc then
		loc.AvailableChestCount = loc.AvailableChestCount - 1
	end

	-- Victory tracking: flag when final levels are completed
	if location_id == CK4_VICTORY_LOCATION then
		local obj = Tracker:FindObjectForCode("ck4_victory")
		if obj then
			obj.Active = true
		end
	elseif location_id == CK5_VICTORY_LOCATION then
		local obj = Tracker:FindObjectForCode("ck5_victory")
		if obj then
			obj.Active = true
		end
	end
end

-- Register AP handlers
Archipelago:AddClearHandler("keen_clear_handler", onClear)
Archipelago:AddItemHandler("keen_item_handler", onItem)
Archipelago:AddLocationHandler("keen_location_handler", onLocation)

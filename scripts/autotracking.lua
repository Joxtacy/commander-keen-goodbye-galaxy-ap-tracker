-- autotracking.lua
-- Archipelago auto-tracking for Commander Keen: Goodbye Galaxy

-- Episode selection from slot_data (0=both, 1=ck4, 2=ck5)
EPISODE_SELECT = 0
-- Gemsets setting from slot_data (0=off, 1=on)
ENABLE_GEMSETS = 1
-- Flasksanity (CK4 Lifewater Flask pickups) toggle from slot_data
ENABLE_FLASKSANITY = 0
-- Kegsanity (CK5 Vitalin Keg pickups) toggle from slot_data
ENABLE_KEGSANITY = 0
-- Conesanity (CK4 Ice Cream Cone 5000-pt pickups) toggle from slot_data
ENABLE_CONESANITY = 0
-- Sugarsanity (CK5 Bag O' Sugar 5000-pt pickups) toggle from slot_data
ENABLE_SUGARSANITY = 0
-- Secret-level toggles from slot_data (CK4 = Pyramid of the Forbidden,
-- CK5 = Korath III Base; 0=off, 1=on)
ENABLE_CK4_SECRET_LEVEL = 0
ENABLE_CK5_SECRET_LEVEL = 0

-- Final level location IDs for victory tracking
CK4_VICTORY_LOCATION = 13800 -- Bean-With-Bacon Megarocket Complete
CK5_VICTORY_LOCATION = 15200 -- Quantum Explosion Dynamo Complete

-- AP item id -> readable label. The id is the contract (it matches
-- worlds/keen/Items.py); both onItem and onClear resolve objects via the
-- "keen_<id>" code every item declares in items.json, so the labels here are
-- documentation and the keys serve as the list of items to reset on connect.
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
	[1014] = "level_potf",
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
	[101400] = "potf_red1",
	[101410] = "potf_red2",
	[101401] = "potf_yellow",
	[101402] = "potf_blue",
	[101403] = "potf_green",
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
	[101499] = "potf_gemset",
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
	[2013] = "level_korath",

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
	[201301] = "korath_yellow",
	[201302] = "korath_blue1",
	[201312] = "korath_blue2",
	[201303] = "korath_green",

	-- CK5 keycard items
	[200204] = "sc_keycard",
	[200304] = "dtv_keycard",
	[200504] = "dtb_keycard",
	[200704] = "dts_keycard",
	[200904] = "dtt_keycard",
	[201104] = "gdh_keycard",
	[201304] = "korath_keycard",

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
	[201399] = "korath_gemset",

	-- Filler
	[900] = "extra_keen",
	[901] = "stunner_ammo",
}

-- Map AP location IDs to PopTracker location names
-- Built from Locations.py: loc_level_complete / loc_keygem / loc_keycard formulas
LOCATION_MAP = {
	-- CK4 level completes
	[12100] = "Keen 4/Border Village/Complete",
	[12200] = "Keen 4/Slug Village/Complete",
	[12300] = "Keen 4/The Perilous Pit/Complete",
	[12400] = "Keen 4/Cave of the Descendents/Complete",
	[12500] = "Keen 4/Chasm of Chills/Complete",
	[12600] = "Keen 4/Crystalus/Complete",
	[12700] = "Keen 4/Hilville/Complete",
	[12800] = "Keen 4/Sand Yego/Complete",
	[12900] = "Keen 4/Miragia/Complete",
	[13000] = "Keen 4/Lifewater Oasis/Complete",
	[13100] = "Keen 4/Pyramid of the Moons/Complete",
	[13200] = "Keen 4/Pyramid of Shadows/Complete",
	[13300] = "Keen 4/Pyramid of the Gnosticine Ancients/Complete",
	[13400] = "Keen 4/Pyramid of the Forbidden/Complete",
	[13500] = "Keen 4/Isle of Tar/Complete",
	[13600] = "Keen 4/Isle of Fire/Complete",
	[13700] = "Keen 4/Well of Wishes/Complete",
	[13800] = "Keen 4/Bean-With-Bacon Megarocket/Complete",
	-- CK4 gems
	[22300] = "Keen 4/The Perilous Pit/Red Gem",
	[22302] = "Keen 4/The Perilous Pit/Blue Gem",
	[22400] = "Keen 4/Cave of the Descendents/Red Gem",
	[22401] = "Keen 4/Cave of the Descendents/Yellow Gem",
	[22600] = "Keen 4/Crystalus/Red Gem",
	[22601] = "Keen 4/Crystalus/Yellow Gem",
	[22602] = "Keen 4/Crystalus/Blue Gem",
	[22603] = "Keen 4/Crystalus/Green Gem",
	[22803] = "Keen 4/Sand Yego/Green Gem",
	[23003] = "Keen 4/Lifewater Oasis/Green Gem",
	[23101] = "Keen 4/Pyramid of the Moons/Yellow Gem",
	[23202] = "Keen 4/Pyramid of Shadows/Blue Gem",
	[23300] = "Keen 4/Pyramid of the Gnosticine Ancients/Red Gem",
	[23303] = "Keen 4/Pyramid of the Gnosticine Ancients/Green Gem",
	[23400] = "Keen 4/Pyramid of the Forbidden/Red Gem",
	[23401] = "Keen 4/Pyramid of the Forbidden/Yellow Gem",
	[23402] = "Keen 4/Pyramid of the Forbidden/Blue Gem",
	[23403] = "Keen 4/Pyramid of the Forbidden/Green Gem",
	[23500] = "Keen 4/Isle of Tar/Red Gem",
	[23501] = "Keen 4/Isle of Tar/Yellow Gem",
	[23502] = "Keen 4/Isle of Tar/Blue Gem",
	[23601] = "Keen 4/Isle of Fire/Yellow Gem",
	[23602] = "Keen 4/Isle of Fire/Blue Gem",
	-- CK5 level completes
	[14100] = "Keen 5/Ion Ventilation System/Complete",
	[14200] = "Keen 5/Security Center/Complete",
	[14300] = "Keen 5/Defense Tunnel Vlook/Complete",
	[14400] = "Keen 5/Energy Flow Systems/Complete",
	[14500] = "Keen 5/Defense Tunnel Burrh/Complete",
	[14600] = "Keen 5/Regulation Control Center/Complete",
	[14700] = "Keen 5/Defense Tunnel Sorra/Complete",
	[14800] = "Keen 5/Neutrino Burst Injector/Complete",
	[14900] = "Keen 5/Defense Tunnel Teln/Complete",
	[15000] = "Keen 5/Brownian Motion Inducer/Complete",
	[15100] = "Keen 5/Gravitational Damping Hub/Complete",
	[15200] = "Keen 5/Quantum Explosion Dynamo/Complete",
	[15300] = "Keen 5/Korath III Base/Complete",
	-- CK5 gems
	[24200] = "Keen 5/Security Center/Red Gem",
	[24202] = "Keen 5/Security Center/Blue Gem",
	[24300] = "Keen 5/Defense Tunnel Vlook/Red Gem",
	[24301] = "Keen 5/Defense Tunnel Vlook/Yellow Gem",
	[24400] = "Keen 5/Energy Flow Systems/Red Gem",
	[24401] = "Keen 5/Energy Flow Systems/Yellow Gem",
	[24402] = "Keen 5/Energy Flow Systems/Blue Gem",
	[24403] = "Keen 5/Energy Flow Systems/Green Gem",
	[24500] = "Keen 5/Defense Tunnel Burrh/Red Gem",
	[24501] = "Keen 5/Defense Tunnel Burrh/Yellow Gem",
	[24502] = "Keen 5/Defense Tunnel Burrh/Blue Gem",
	[24503] = "Keen 5/Defense Tunnel Burrh/Green Gem",
	[24600] = "Keen 5/Regulation Control Center/Red Gem",
	[24601] = "Keen 5/Regulation Control Center/Yellow Gem",
	[24602] = "Keen 5/Regulation Control Center/Blue Gem",
	[24701] = "Keen 5/Defense Tunnel Sorra/Yellow Gem",
	[24800] = "Keen 5/Neutrino Burst Injector/Red Gem",
	[24802] = "Keen 5/Neutrino Burst Injector/Blue Gem",
	[24900] = "Keen 5/Defense Tunnel Teln/Red Gem",
	[24901] = "Keen 5/Defense Tunnel Teln/Yellow Gem",
	[24902] = "Keen 5/Defense Tunnel Teln/Blue Gem",
	[24903] = "Keen 5/Defense Tunnel Teln/Green Gem",
	[25001] = "Keen 5/Brownian Motion Inducer/Yellow Gem",
	[25002] = "Keen 5/Brownian Motion Inducer/Blue Gem",
	[25100] = "Keen 5/Gravitational Damping Hub/Red Gem",
	[25103] = "Keen 5/Gravitational Damping Hub/Green Gem",
	[25200] = "Keen 5/Quantum Explosion Dynamo/Red Gem",
	[25201] = "Keen 5/Quantum Explosion Dynamo/Yellow Gem",
	[25202] = "Keen 5/Quantum Explosion Dynamo/Blue Gem",
	[25203] = "Keen 5/Quantum Explosion Dynamo/Green Gem",
	[25301] = "Keen 5/Korath III Base/Yellow Gem",
	[25302] = "Keen 5/Korath III Base/Blue Gem",
	[25303] = "Keen 5/Korath III Base/Green Gem",
	-- CK5 keycards
	[34200] = "Keen 5/Security Center/Keycard",
	[34300] = "Keen 5/Defense Tunnel Vlook/Keycard",
	[34500] = "Keen 5/Defense Tunnel Burrh/Keycard",
	[34700] = "Keen 5/Defense Tunnel Sorra/Keycard",
	[34900] = "Keen 5/Defense Tunnel Teln/Keycard",
	[35100] = "Keen 5/Gravitational Damping Hub/Keycard",
	[35300] = "Keen 5/Korath III Base/Keycard",
}

-- Flasksanity (CK4 Lifewater Flasks) and Kegsanity (CK5 Vitalin Kegs).
-- Each engine idx maps to the extracted "<Level> - Lifewater Flasks" /
-- "<Level> - Vitalin Kegs" tracker entry where its marker lives. Levels that
-- have flasks/kegs split across multiple clusters (PoS, POTGA, IoT, SC, DTV)
-- get one entry per cluster, and each idx is routed to its specific entry +
-- section so the per-marker status is accurate.
-- IDs: LOC_FLASK = 60000 + 1*2000 + lvl*100 + idx
--      LOC_KEG   = 50000 + 2*2000 + lvl*100 + idx
-- The apworld excludes PP flasks 0-1, COTD flasks 0-1, LO flasks 0-4 and
-- POTGA flask 0; those IDs are never sent and therefore not mapped.
local CK4_FLASK_LAYOUT = {
	[1]  = {{lo=0, hi=6, entry="Border Village - Lifewater Flasks",                  section="Lifewater Flasks"}},
	[4]  = {{lo=0, hi=1, entry="Cave of the Descendents - Lifewater Flasks",         section="Lifewater Flasks"}},
	[5]  = {{lo=0, hi=0, entry="Chasm of Chills - Lifewater Flasks",                 section="Lifewater Flasks"}},
	[7]  = {{lo=0, hi=0, entry="Hilville - Lifewater Flasks",                        section="Lifewater Flasks"}},
	[8]  = {{lo=0, hi=0, entry="Sand Yego - Lifewater Flasks",                       section="Lifewater Flasks"}},
	[9]  = {{lo=0, hi=0, entry="Miragia - Lifewater Flasks",                         section="Lifewater Flasks"}},
	[11] = {{lo=0, hi=0, entry="Pyramid of the Moons - Lifewater Flasks",            section="Lifewater Flasks"}},
	[12] = {
		{lo=0, hi=0, entry="Pyramid of Shadows - Lifewater Flask 1",                 section="Lifewater Flask (Stunner)"},
		{lo=1, hi=7, entry="Pyramid of Shadows - Lifewater Flasks 2-8",              section="Lifewater Flasks (Stunner)"},
	},
	-- POTGA: apworld's Rules.py labels engine idx 1 (lone at y=92) as "Flask 2"
	-- requiring stunner, but in-game the lone flask actually needs pogo. The
	-- two paired flasks at y=65 (idx 2 & 3) both need stunner. We surface the
	-- markers under the names the player sees (Flasks 2-3 paired stunner,
	-- Flask 4 lone pogo); see suspected-apworld-bugs memory.
	[13] = {
		{lo=1, hi=1, entry="Pyramid of the Gnosticine Ancients - Lifewater Flask 4",   section="Lifewater Flask (Pogo)"},
		{lo=2, hi=3, entry="Pyramid of the Gnosticine Ancients - Lifewater Flasks 2-3", section="Lifewater Flasks (Stunner)"},
	},
	[14] = {{lo=0, hi=1, entry="Pyramid of the Forbidden - Lifewater Flasks",         section="Lifewater Flasks"}},
	[15] = {
		{lo=0, hi=0, entry="Isle of Tar - Lifewater Flask 1",                        section="Lifewater Flask (Pogo)"},
		{lo=1, hi=1, entry="Isle of Tar - Lifewater Flask 2",                        section="Lifewater Flask (Pogo)"},
	},
	[16] = {{lo=0, hi=0, entry="Isle of Fire - Lifewater Flasks",                    section="Lifewater Flasks"}},
	[17] = {{lo=0, hi=0, entry="Well of Wishes - Lifewater Flasks",                  section="Lifewater Flasks"}},
}
local CK5_KEG_LAYOUT = {
	[1]  = {{lo=0, hi=9, entry="Ion Ventilation System - Vitalin Kegs",     section="Vitalin Kegs"}},
	[2]  = {
		{lo=0, hi=0, entry="Security Center - Vitalin Keg 1",               section="Vitalin Keg (Blue Gem)"},
		{lo=1, hi=1, entry="Security Center - Vitalin Keg 2",               section="Vitalin Keg"},
	},
	[3]  = {
		{lo=0, hi=0, entry="Defense Tunnel Vlook - Vitalin Keg 1",          section="Vitalin Keg (Yellow Gem+Pogo)"},
		{lo=1, hi=1, entry="Defense Tunnel Vlook - Vitalin Keg 2",          section="Vitalin Keg"},
	},
	[4]  = {{lo=0, hi=0, entry="Energy Flow Systems - Vitalin Kegs",        section="Vitalin Kegs"}},
	[5]  = {{lo=0, hi=1, entry="Defense Tunnel Burrh - Vitalin Kegs",       section="Vitalin Kegs"}},
	[9]  = {{lo=0, hi=0, entry="Defense Tunnel Teln - Vitalin Kegs",        section="Vitalin Kegs"}},
	[10] = {{lo=0, hi=0, entry="Brownian Motion Inducer - Vitalin Kegs",    section="Vitalin Kegs"}},
	[11] = {{lo=0, hi=0, entry="Gravitational Damping Hub - Vitalin Kegs",  section="Vitalin Kegs"}},
	[12] = {{lo=0, hi=1, entry="Quantum Explosion Dynamo - Vitalin Kegs",   section="Vitalin Kegs"}},
	[13] = {
		{lo=0, hi=0, entry="Korath III Base - Vitalin Keg 1",             section="Vitalin Keg"},
		{lo=1, hi=1, entry="Korath III Base - Vitalin Keg 2",             section="Vitalin Keg"},
	},
}
-- Exact flask/keg location-id sets, built alongside LOCATION_MAP from the
-- layout tables above. onLocation tests membership in these to bump the score
-- counters, so the counted ids are exactly the tracked ones (no id-range guess).
FLASK_IDS = {}
KEG_IDS = {}
for lvl_id, segments in pairs(CK4_FLASK_LAYOUT) do
	for _, seg in ipairs(segments) do
		for idx = seg.lo, seg.hi do
			local id = 60000 + 1 * 2000 + lvl_id * 100 + idx
			LOCATION_MAP[id] = "Keen 4/" .. seg.entry .. "/" .. seg.section
			FLASK_IDS[id] = true
		end
	end
end
for lvl_id, segments in pairs(CK5_KEG_LAYOUT) do
	for _, seg in ipairs(segments) do
		for idx = seg.lo, seg.hi do
			local id = 50000 + 2 * 2000 + lvl_id * 100 + idx
			LOCATION_MAP[id] = "Keen 5/" .. seg.entry .. "/" .. seg.section
			KEG_IDS[id] = true
		end
	end
end

-- Conesanity (CK4 Ice Cream Cones) and Sugarsanity (CK5 Bags O' Sugar): the
-- 5000-pt pickups. Each entry is a map pin at the pickups' real in-game
-- position; pickups close together share one pin, and a pin's sections are
-- split by access rule. Generated by tools/gen_pointsanity_tracker.py (which
-- also writes the matching location JSON); rerun it if the apworld's
-- pointsanity counts/rules change.
-- ID: LOC_POINTS5K = 100000 + 5*100000 + ep*20000 + lvl*1000 + inst
--   = 600000 + ep*20000 + lvl*1000 + inst   (ep 1 = CK4, 2 = CK5)
local function loc_points5k(ep, lvl, inst)
	return 600000 + ep * 20000 + lvl * 1000 + inst
end
local CK4_CONE_LAYOUT = {
	[2] = {
		{lo=0, hi=0, entry="Slug Village - Ice Cream Cone 1 (Pogo)", section="Ice Cream Cone 1 (Pogo)"},
		{lo=1, hi=1, entry="Slug Village - Ice Cream Cone 2", section="Ice Cream Cone 2"},
		{lo=2, hi=2, entry="Slug Village - Ice Cream Cone 3", section="Ice Cream Cone 3"},
	},
	[3] = {
		{lo=0, hi=0, entry="The Perilous Pit - Ice Cream Cone 1 (Pogo)", section="Ice Cream Cone 1 (Pogo)"},
	},
	[4] = {
		{lo=0, hi=1, entry="Cave of the Descendents - Ice Cream Cones 1-2", section="Ice Cream Cones 1-2"},
		{lo=2, hi=3, entry="Cave of the Descendents - Ice Cream Cones 3-4", section="Ice Cream Cones 3-4"},
		{lo=4, hi=7, entry="Cave of the Descendents - Ice Cream Cones 5-8", section="Ice Cream Cones 5-8"},
		{lo=8, hi=8, entry="Cave of the Descendents - Ice Cream Cone 9", section="Ice Cream Cone 9"},
		{lo=9, hi=9, entry="Cave of the Descendents - Ice Cream Cone 10", section="Ice Cream Cone 10"},
		{lo=10, hi=10, entry="Cave of the Descendents - Ice Cream Cone 11 (Pogo)", section="Ice Cream Cone 11 (Pogo)"},
	},
	[5] = {
		{lo=0, hi=0, entry="Chasm of Chills - Ice Cream Cone 1", section="Ice Cream Cone 1"},
		{lo=1, hi=1, entry="Chasm of Chills - Ice Cream Cone 2", section="Ice Cream Cone 2"},
		{lo=3, hi=3, entry="Chasm of Chills - Ice Cream Cones 4, 6", section="Ice Cream Cones 4, 6"},
		{lo=5, hi=5, entry="Chasm of Chills - Ice Cream Cones 4, 6", section="Ice Cream Cones 4, 6"},
		{lo=4, hi=4, entry="Chasm of Chills - Ice Cream Cones 5, 7", section="Ice Cream Cones 5, 7"},
		{lo=6, hi=6, entry="Chasm of Chills - Ice Cream Cones 5, 7", section="Ice Cream Cones 5, 7"},
		{lo=2, hi=2, entry="Chasm of Chills - Ice Cream Cone 3 (Pogo)", section="Ice Cream Cone 3 (Pogo)"},
	},
	[6] = {
		{lo=0, hi=1, entry="Crystalus - Ice Cream Cones 1-2 (Pogo)", section="Ice Cream Cones 1-2 (Pogo)"},
		{lo=2, hi=2, entry="Crystalus - Ice Cream Cone 3 (Blue Gem)", section="Ice Cream Cone 3 (Blue Gem)"},
	},
	[7] = {
		{lo=0, hi=0, entry="Hilville - Ice Cream Cone 1 (Pogo)", section="Ice Cream Cone 1 (Pogo)"},
	},
	[8] = {
		{lo=0, hi=0, entry="Sand Yego - Ice Cream Cone 1 (Pogo)", section="Ice Cream Cone 1 (Pogo)"},
		{lo=2, hi=2, entry="Sand Yego - Ice Cream Cone 3 (Pogo)", section="Ice Cream Cone 3 (Pogo)"},
		{lo=1, hi=1, entry="Sand Yego - Ice Cream Cone 2", section="Ice Cream Cone 2"},
		{lo=3, hi=3, entry="Sand Yego - Ice Cream Cone 4", section="Ice Cream Cone 4"},
	},
	[9] = {
		{lo=0, hi=1, entry="Miragia - Ice Cream Cones 1-2 (Pogo)", section="Ice Cream Cones 1-2 (Pogo)"},
		{lo=2, hi=4, entry="Miragia - Ice Cream Cones 3-5", section="Ice Cream Cones 3-5"},
	},
	[11] = {
		{lo=0, hi=5, entry="Pyramid of the Moons - Ice Cream Cones 1-6 (Pogo)", section="Ice Cream Cones 1-6 (Pogo)"},
	},
	[12] = {
		{lo=0, hi=0, entry="Pyramid of Shadows - Ice Cream Cone 1", section="Ice Cream Cone 1"},
	},
	[13] = {
		{lo=0, hi=0, entry="Pyramid of the Gnosticine Ancients - Ice Cream Cone 1 (Pogo)", section="Ice Cream Cone 1 (Pogo)"},
	},
	[14] = {
		{lo=0, hi=9, entry="Pyramid of the Forbidden - Ice Cream Cones 1-10", section="Ice Cream Cones 1-10"},
		{lo=10, hi=13, entry="Pyramid of the Forbidden - Ice Cream Cones 11-14", section="Ice Cream Cones 11-14"},
	},
	[15] = {
		{lo=0, hi=0, entry="Isle of Tar - Ice Cream Cone 1 (Pogo)", section="Ice Cream Cone 1 (Pogo)"},
		{lo=1, hi=1, entry="Isle of Tar - Ice Cream Cone 2", section="Ice Cream Cone 2"},
		{lo=2, hi=2, entry="Isle of Tar - Ice Cream Cone 3", section="Ice Cream Cone 3"},
	},
	[16] = {
		{lo=0, hi=4, entry="Isle of Fire - Ice Cream Cones 1-5 (Pogo)", section="Ice Cream Cones 1-5 (Pogo)"},
	},
}
local CK5_SUGAR_LAYOUT = {
	[2] = {
		{lo=0, hi=1, entry="Security Center - Bags O' Sugar 1-2, 5-6 (Blue Gem)", section="Bags O' Sugar 1-2, 5-6 (Blue Gem)"},
		{lo=4, hi=5, entry="Security Center - Bags O' Sugar 1-2, 5-6 (Blue Gem)", section="Bags O' Sugar 1-2, 5-6 (Blue Gem)"},
		{lo=2, hi=3, entry="Security Center - Bags O' Sugar 3-4, 7-8 (Blue Gem)", section="Bags O' Sugar 3-4, 7-8 (Blue Gem)"},
		{lo=6, hi=7, entry="Security Center - Bags O' Sugar 3-4, 7-8 (Blue Gem)", section="Bags O' Sugar 3-4, 7-8 (Blue Gem)"},
		{lo=10, hi=13, entry="Security Center - Bags O' Sugar 11-14 (Blue Gem)", section="Bags O' Sugar 11-14 (Blue Gem)"},
		{lo=14, hi=19, entry="Security Center - Bags O' Sugar 15-20 (Pogo)", section="Bags O' Sugar 15-20 (Pogo)"},
		{lo=20, hi=23, entry="Security Center - Bags O' Sugar 21-24", section="Bags O' Sugar 21-24"},
		{lo=24, hi=27, entry="Security Center - Bags O' Sugar 25-28", section="Bags O' Sugar 25-28"},
	},
	[3] = {
		{lo=0, hi=1, entry="Defense Tunnel Vlook - Bags O' Sugar 1-2, 4-5", section="Bags O' Sugar 1-2, 4-5"},
		{lo=3, hi=4, entry="Defense Tunnel Vlook - Bags O' Sugar 1-2, 4-5", section="Bags O' Sugar 1-2, 4-5"},
		{lo=2, hi=2, entry="Defense Tunnel Vlook - Bags O' Sugar 3, 6-7", section="Bags O' Sugar 3, 6-7"},
		{lo=5, hi=6, entry="Defense Tunnel Vlook - Bags O' Sugar 3, 6-7", section="Bags O' Sugar 3, 6-7"},
	},
	[4] = {
		{lo=0, hi=3, entry="Energy Flow Systems - Bags O' Sugar 1-4", section="Bags O' Sugar 1-4"},
		{lo=4, hi=5, entry="Energy Flow Systems - Bags O' Sugar 5-6", section="Bags O' Sugar 5-6"},
		{lo=6, hi=9, entry="Energy Flow Systems - Bags O' Sugar 7-10", section="Bags O' Sugar 7-10"},
	},
	[5] = {
		{lo=0, hi=3, entry="Defense Tunnel Burrh - Bags O' Sugar 1-4 (Red Gem, Pogo)", section="Bags O' Sugar 1-4 (Red Gem, Pogo)"},
	},
	[7] = {
		{lo=0, hi=2, entry="Defense Tunnel Sorra - Bags O' Sugar 1-3", section="Bags O' Sugar 1-3"},
		{lo=3, hi=12, entry="Defense Tunnel Sorra - Bags O' Sugar 4-13", section="Bags O' Sugar 4-13"},
	},
	[8] = {
		{lo=0, hi=1, entry="Neutrino Burst Injector - Bags O' Sugar 1-2 (Pogo)", section="Bags O' Sugar 1-2 (Pogo)"},
		{lo=2, hi=3, entry="Neutrino Burst Injector - Bags O' Sugar 3-4", section="Bags O' Sugar 3-4"},
	},
	[9] = {
		{lo=0, hi=1, entry="Defense Tunnel Teln - Bags O' Sugar 1-2 (Yellow Gem, Blue Gem)", section="Bags O' Sugar 1-2 (Yellow Gem, Blue Gem)"},
		{lo=2, hi=5, entry="Defense Tunnel Teln - Bags O' Sugar 3-6 (Yellow Gem, Blue Gem)", section="Bags O' Sugar 3-6 (Yellow Gem, Blue Gem)"},
		{lo=6, hi=9, entry="Defense Tunnel Teln - Bags O' Sugar 7-10 (Yellow Gem)", section="Bags O' Sugar 7-10 (Yellow Gem)"},
	},
	[10] = {
		{lo=0, hi=3, entry="Brownian Motion Inducer - Bags O' Sugar 1-4", section="Bags O' Sugar 1-4"},
		{lo=4, hi=7, entry="Brownian Motion Inducer - Bags O' Sugar 5-8", section="Bags O' Sugar 5-8"},
	},
	[11] = {
		{lo=0, hi=5, entry="Gravitational Damping Hub - Bags O' Sugar 1-6 (Green Gem, Pogo)", section="Bags O' Sugar 1-6 (Green Gem, Pogo)"},
		{lo=6, hi=9, entry="Gravitational Damping Hub - Bags O' Sugar 7-10 (Pogo)", section="Bags O' Sugar 7-10 (Pogo)"},
		{lo=10, hi=12, entry="Gravitational Damping Hub - Bags O' Sugar 11-13 (Pogo)", section="Bags O' Sugar 11-13 (Pogo)"},
		{lo=13, hi=14, entry="Gravitational Damping Hub - Bags O' Sugar 14-15", section="Bags O' Sugar 14-15"},
	},
	[12] = {
		{lo=0, hi=5, entry="Quantum Explosion Dynamo - Bags O' Sugar 1-6 (Red Gem, Yellow Gem, Blue Gem, Green Gem, Pogo)", section="Bags O' Sugar 1-6 (Red Gem, Yellow Gem, Blue Gem, Green Gem, Pogo)"},
		{lo=6, hi=8, entry="Quantum Explosion Dynamo - Bags O' Sugar 7-9 (Pogo)", section="Bags O' Sugar 7-9 (Pogo)"},
	},
	[13] = {
		{lo=0, hi=3, entry="Korath III Base - Bags O' Sugar 1-4", section="Bags O' Sugar 1-4"},
		{lo=4, hi=19, entry="Korath III Base - Bags O' Sugar 5-20", section="Bags O' Sugar 5-20"},
	},
}
CONE_IDS = {}
SUGAR_IDS = {}
-- Cone/sugar entries are top-level location nodes in their own JSON files
-- (mirroring keen4_level_maps.json's flat-node pattern), so their @-paths are
-- "<entry>/<section>" with no "Keen 4"/"Keen 5" parent prefix.
for lvl_id, segments in pairs(CK4_CONE_LAYOUT) do
	for _, seg in ipairs(segments) do
		for idx = seg.lo, seg.hi do
			local id = loc_points5k(1, lvl_id, idx)
			LOCATION_MAP[id] = seg.entry .. "/" .. seg.section
			CONE_IDS[id] = true
		end
	end
end
for lvl_id, segments in pairs(CK5_SUGAR_LAYOUT) do
	for _, seg in ipairs(segments) do
		for idx = seg.lo, seg.hi do
			local id = loc_points5k(2, lvl_id, idx)
			LOCATION_MAP[id] = seg.entry .. "/" .. seg.section
			SUGAR_IDS[id] = true
		end
	end
end

-- Map game level numbers to layout tab titles for auto map switching
-- Tab titles must match exactly what's in the layout JSON
CK4_MAP_TABS = {
	[0] = "Overworld",
	[1] = "Border Village",
	[2] = "Slug Village",
	[3] = "Perilous Pit",
	[4] = "Cave of Desc.",
	[5] = "Chasm of Chills",
	[6] = "Crystalus",
	[7] = "Hilville",
	[8] = "Sand Yego",
	[9] = "Miragia",
	[10] = "Lifewater Oasis",
	[11] = "Pyr. of Moons",
	[12] = "Pyr. of Shadows",
	[13] = "Pyr. of Gnost.",
	[14] = "Pyr. Forbidden",
	[15] = "Isle of Tar",
	[16] = "Isle of Fire",
	[17] = "Well of Wishes",
	[18] = "BWBM",
}

CK5_MAP_TABS = {
	[0] = "Overworld",
	[1] = "Ion Vent. Sys.",
	[2] = "Security Ctr.",
	[3] = "DT Vlook",
	[4] = "Energy Flow",
	[5] = "DT Burrh",
	[6] = "Reg. Control",
	[7] = "DT Sorra",
	[8] = "Neutrino Burst",
	[9] = "DT Teln",
	[10] = "Brownian Mot.",
	[11] = "Grav. Damp.",
	[12] = "QED",
	[13] = "Korath III",
}

-- DataStorage key for current level (set after connecting)
MAP_KEY = nil

-- ============================================================
-- Helpers
-- ============================================================

-- Lua-side counters for the score-item progress widgets. The widgets are
-- declared as toggles in items.json (rather than consumables) because the
-- consumable widget paints its own AcquiredCount as a badge that always
-- overrides BadgeText/SetOverlay once the count is non-zero — which left
-- "X/N" only visible at zero. Toggles have no default badge so the text
-- shows through at every count.
SCORE_COUNT = { flask_count = 0, keg_count = 0, cone_count = 0, sugar_count = 0 }
SCORE_MAX   = { flask_count = 31, keg_count = 24, cone_count = 65, sugar_count = 126 }

-- Update the items-panel score-item counter widget. If `count` is given,
-- it replaces the running count for this code; otherwise the existing value
-- is re-displayed. obj.Active is bound to whether the corresponding sanity
-- option is enabled for this run (so the icon stays colored when the user
-- is tracking flasks/kegs and stays grey when they aren't), not to whether
-- any have been collected yet. Writes BadgeText (PopTracker 0.31.0+) and
-- SetOverlay (older API) plus a green-when-full tint, all wrapped in pcall.
function update_score_overlay(code, count)
	local obj = Tracker:FindObjectForCode(code)
	if not obj then return end
	if count ~= nil then SCORE_COUNT[code] = count end
	local n = SCORE_COUNT[code] or 0
	local max = SCORE_MAX[code] or 0
	local enabled = false
	if code == "flask_count" then
		enabled = (ENABLE_FLASKSANITY == 1)
	elseif code == "keg_count" then
		enabled = (ENABLE_KEGSANITY == 1)
	elseif code == "cone_count" then
		enabled = (ENABLE_CONESANITY == 1)
	elseif code == "sugar_count" then
		enabled = (ENABLE_SUGARSANITY == 1)
	end
	pcall(function() obj.Active = enabled end)
	local text = string.format("%d/%d", n, max)
	local color = n >= max and "#00FF00" or "#FFFFFF"
	pcall(function() obj.BadgeText = text end)
	pcall(function() obj.BadgeTextColor = color end)
	if obj.SetOverlay then pcall(function() obj:SetOverlay(text) end) end
	if obj.SetOverlayColor then pcall(function() obj:SetOverlayColor(color) end) end
end

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

	if slot_data and slot_data["enable_flasksanity"] ~= nil then
		ENABLE_FLASKSANITY = slot_data["enable_flasksanity"]
	else
		ENABLE_FLASKSANITY = 0
	end

	if slot_data and slot_data["enable_kegsanity"] ~= nil then
		ENABLE_KEGSANITY = slot_data["enable_kegsanity"]
	else
		ENABLE_KEGSANITY = 0
	end

	if slot_data and slot_data["enable_conesanity"] ~= nil then
		ENABLE_CONESANITY = slot_data["enable_conesanity"]
	else
		ENABLE_CONESANITY = 0
	end

	if slot_data and slot_data["enable_sugarsanity"] ~= nil then
		ENABLE_SUGARSANITY = slot_data["enable_sugarsanity"]
	else
		ENABLE_SUGARSANITY = 0
	end

	if slot_data and slot_data["enable_ck4_secret_level"] ~= nil then
		ENABLE_CK4_SECRET_LEVEL = slot_data["enable_ck4_secret_level"]
	else
		ENABLE_CK4_SECRET_LEVEL = 0
	end

	if slot_data and slot_data["enable_ck5_secret_level"] ~= nil then
		ENABLE_CK5_SECRET_LEVEL = slot_data["enable_ck5_secret_level"]
	else
		ENABLE_CK5_SECRET_LEVEL = 0
	end

	-- Set the gemsets setting toggle
	local gemsets_setting = Tracker:FindObjectForCode("gemsets")
	if gemsets_setting then
		gemsets_setting.Active = (ENABLE_GEMSETS == 1)
	end

	-- Set the flasksanity / kegsanity toggles (gate CK4 Lifewater Flask /
	-- CK5 Vitalin Keg section access_rules).
	local flasksanity_setting = Tracker:FindObjectForCode("flasksanity")
	if flasksanity_setting then
		flasksanity_setting.Active = (ENABLE_FLASKSANITY == 1)
	end
	local kegsanity_setting = Tracker:FindObjectForCode("kegsanity")
	if kegsanity_setting then
		kegsanity_setting.Active = (ENABLE_KEGSANITY == 1)
	end
	local conesanity_setting = Tracker:FindObjectForCode("conesanity")
	if conesanity_setting then
		conesanity_setting.Active = (ENABLE_CONESANITY == 1)
	end
	local sugarsanity_setting = Tracker:FindObjectForCode("sugarsanity")
	if sugarsanity_setting then
		sugarsanity_setting.Active = (ENABLE_SUGARSANITY == 1)
	end

	-- Secret-level toggles (gate the Pyramid of the Forbidden / Korath III
	-- Base section visibility_rules).
	local ck4_secret_setting = Tracker:FindObjectForCode("ck4_secret_level")
	if ck4_secret_setting then
		ck4_secret_setting.Active = (ENABLE_CK4_SECRET_LEVEL == 1)
	end
	local ck5_secret_setting = Tracker:FindObjectForCode("ck5_secret_level")
	if ck5_secret_setting then
		ck5_secret_setting.Active = (ENABLE_CK5_SECRET_LEVEL == 1)
	end

	-- Reset all tracked items. ITEM_MAP's keys are the AP item ids; resolve
	-- each object by its "keen_<id>" code, same as onItem.
	for item_id, _ in pairs(ITEM_MAP) do
		local obj = Tracker:FindObjectForCode("keen_" .. item_id)
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

	-- Reset score-item progress counters (bumped from onLocation)
	update_score_overlay("flask_count", 0)
	update_score_overlay("keg_count", 0)
	update_score_overlay("cone_count", 0)
	update_score_overlay("sugar_count", 0)

	-- Reset all locations
	for _, loc_path in pairs(LOCATION_MAP) do
		local loc = Tracker:FindObjectForCode("@" .. loc_path)
		if loc then
			loc.AvailableChestCount = loc.ChestCount
		end
	end

	-- Subscribe to DataStorage for auto map switching
	if Archipelago.PlayerNumber and Archipelago.PlayerNumber > -1 then
		MAP_KEY = "keen_current_level_" .. tostring(Archipelago.PlayerNumber)
		Archipelago:SetNotify({ MAP_KEY })
		Archipelago:Get({ MAP_KEY })
	end
end

function onItem(index, item_id, item_name, player_number)
	-- Every AP item declares a "keen_<id>" code in items.json, so resolve the
	-- object straight from the id. Unknown ids resolve to nil and are ignored.
	local obj = Tracker:FindObjectForCode("keen_" .. item_id)
	if not obj then
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

	-- Score-item counters on the items panel. FLASK_IDS / KEG_IDS are the exact
	-- id sets derived from the flask/keg layout tables (see where they're built).
	if FLASK_IDS[location_id] then
		update_score_overlay("flask_count", (SCORE_COUNT["flask_count"] or 0) + 1)
	elseif KEG_IDS[location_id] then
		update_score_overlay("keg_count", (SCORE_COUNT["keg_count"] or 0) + 1)
	elseif CONE_IDS[location_id] then
		update_score_overlay("cone_count", (SCORE_COUNT["cone_count"] or 0) + 1)
	elseif SUGAR_IDS[location_id] then
		update_score_overlay("sugar_count", (SCORE_COUNT["sugar_count"] or 0) + 1)
	end
end

function onMapChange(key, value, old_value)
	-- Only switch if automap toggle is enabled
	local automap = Tracker:FindObjectForCode("automap")
	if not automap or not automap.Active then
		return
	end

	-- value is { level = N, episode = M } from DataStorage
	if type(value) ~= "table" then
		return
	end

	local level = value["level"]
	local ep = value["episode"]
	if not level or not ep then
		return
	end

	local tab = nil
	if ep == 1 then
		tab = CK4_MAP_TABS[level]
		-- For "both" variant, switch to the Keen 4 episode tab first
		Tracker:UiHint("ActivateTab", "Keen 4")
	elseif ep == 2 then
		tab = CK5_MAP_TABS[level]
		Tracker:UiHint("ActivateTab", "Keen 5")
	end

	if tab then
		Tracker:UiHint("ActivateTab", tab)
	end
end

-- Register AP handlers
Archipelago:AddClearHandler("keen_clear_handler", onClear)
Archipelago:AddItemHandler("keen_item_handler", onItem)
Archipelago:AddLocationHandler("keen_location_handler", onLocation)
Archipelago:AddSetReplyHandler("keen_map_handler", onMapChange)
Archipelago:AddRetrievedHandler("keen_map_retrieved", onMapChange)

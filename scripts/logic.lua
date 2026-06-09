-- logic.lua
-- Custom access rule functions for final-level gating.
-- BWBM (CK4) requires all other CK4 levels to be completable.
-- QED (CK5) Complete gates on ck5_endgame_reachable only — same as the
-- other QED-region locations. Unlike BWBM, the apworld's QED Complete rule
-- (Rules.py) is NOT a can_reach() chain over the other CK5 levels; it is
-- just level_qed + pogo + the four QED gems, sitting inside the End Game
-- region, whose entry the region graph gates on the four hub levels
-- (EFS, RCC, NBI, BMI) being completable.

-- Helper: check if an item code is active.
-- Uses ProviderCountForCode which correctly handles progressive items
-- (codes are only active at the stage that declares them).
local function has(code)
    return Tracker:ProviderCountForCode(code) > 0
end

-- Helper: check if a level's completion requirements are met.
-- A level is completable when:  level unlock  AND  optional pogo/wetsuit/stunner/keycard
-- AND  (all required gems  OR  gemset).
-- gem_or_pogo: when true, owning pogo is an *alternative* to the gem/gemset
-- requirement (e.g. POTM's over-the-top exit, which skips the yellow-gem door).
-- This is distinct from the `pogo` arg, which makes pogo an additional AND.
local function level_completable(level, gems, gemset, pogo, wetsuit, keycard, stunner, gem_or_pogo)
    if not has(level) then return false end
    if pogo and not has("pogo") then return false end
    if wetsuit and not has("wetsuit") then return false end
    if stunner and not has("stunner") then return false end
    if keycard and not has(keycard) then return false end
    if gems then
        local all_gems = true
        for _, g in ipairs(gems) do
            if not has(g) then all_gems = false; break end
        end
        local satisfied = all_gems or has(gemset)
        if gem_or_pogo then satisfied = satisfied or has("pogo") end
        if not satisfied then return false end
    end
    return true
end

-- All 16 CK4 levels (other than BWBM) completable
function ck4_all_completable()
    if not level_completable("level_bv") then return 0 end
    if not level_completable("level_sv") then return 0 end
    if not level_completable("level_pp",    {"pp_red","pp_blue"},         "pp_gemset")    then return 0 end
    if not level_completable("level_cotd",  {"cotd_yellow"},             "cotd_gemset",  true)  then return 0 end
    if not level_completable("level_coc")   then return 0 end
    if not level_completable("level_crys",  {"crys_blue"},               "crys_gemset")  then return 0 end
    if not level_completable("level_hil")   then return 0 end
    if not level_completable("level_sy",    {"sy_green"},                "sy_gemset",    true)  then return 0 end
    if not level_completable("level_mir",   nil, nil,                                     true)  then return 0 end
    if not level_completable("level_lo",    {"lo_green"},                "lo_gemset")    then return 0 end
    -- POTM has three exits: yellow-gem door, secret exit (also yellow), and an
    -- over-the-top route reachable with pogo alone (no yellow). gem_or_pogo=true.
    if not level_completable("level_potm",  {"potm_yellow"},             "potm_gemset",  false, false, nil, false, true) then return 0 end
    if not level_completable("level_pos",   {"pos_blue"},                "pos_gemset",   false, false, nil, true) then return 0 end
    if not level_completable("level_potga", {"potga_red","potga_green"}, "potga_gemset", true)  then return 0 end
    -- IoT completion uses the over-the-top pogo route, which skips the Blue
    -- Gem door entirely, so only pogo (+ wetsuit region gate) is needed.
    if not level_completable("level_iot",   nil, nil,                                    true, true) then return 0 end
    if not level_completable("level_iof",   {"iof_yellow","iof_blue"},   "iof_gemset",  false, true) then return 0 end
    if not level_completable("level_wow",   nil, nil,                                    false, true) then return 0 end
    return 1
end

-- Council-rescue goal: the 8 council-member levels completable. Mirrors the
-- per-level requirements in ck4_all_completable for exactly those 8 levels
-- (The Perilous Pit, Cave of the Descendents, Crystalus, Lifewater Oasis,
-- Pyramid of Shadows, Pyramid of the Gnosticine Ancients, Isle of Fire, Well of
-- Wishes). Used to drive the council goal's reachability indicator; the BWBM
-- and the other non-council levels are not required for this goal.
function ck4_council_goal_completable()
    if not level_completable("level_pp",    {"pp_red","pp_blue"},         "pp_gemset")    then return 0 end
    if not level_completable("level_cotd",  {"cotd_yellow"},             "cotd_gemset",  true)  then return 0 end
    if not level_completable("level_crys",  {"crys_blue"},               "crys_gemset")  then return 0 end
    if not level_completable("level_lo",    {"lo_green"},                "lo_gemset")    then return 0 end
    if not level_completable("level_pos",   {"pos_blue"},                "pos_gemset",   false, false, nil, true) then return 0 end
    if not level_completable("level_potga", {"potga_red","potga_green"}, "potga_gemset", true)  then return 0 end
    if not level_completable("level_iof",   {"iof_yellow","iof_blue"},   "iof_gemset",  false, true) then return 0 end
    if not level_completable("level_wow",   nil, nil,                                    false, true) then return 0 end
    return 1
end

-- Shared CK5 hub-level gem requirements. RCC/NBI/BMI gate identically wherever
-- they appear (End Game region entry and per-level completion), so define them
-- once. EFS is deliberately NOT shared: the End Game region gate needs all four
-- EFS gems, but the EFS Complete location needs only the Green Gem — each call
-- site spells out its own EFS requirement.
local RCC_GEMS = {"rcc_red", "rcc_yellow", "rcc_blue"}
local NBI_GEMS = {"nbi_red", "nbi_blue"}
local BMI_GEMS = {"bmi_yellow", "bmi_blue"}

-- End Game region gate: EFS, RCC, NBI, BMI must be completable
-- (matches Regions.py K5 Hub → End Game connection). All four are
-- requires_pogo=True in Rules.py, so each completability check passes pogo;
-- EFS here needs all four gems, matching the region gate.
function ck5_endgame_reachable()
    if not level_completable("level_efs", {"efs_red", "efs_yellow", "efs_blue", "efs_green"}, "efs_gemset", true) then return 0 end
    if not level_completable("level_rcc", RCC_GEMS, "rcc_gemset", true) then return 0 end
    if not level_completable("level_nbi", NBI_GEMS, "nbi_gemset", true) then return 0 end
    if not level_completable("level_bmi", BMI_GEMS, "bmi_gemset", true) then return 0 end
    return 1
end

-- Secret-level entry gates (cross-level prerequisites; match Rules.py
-- potf_gate / korath_gate). A secret level is only physically reachable by
-- traversing another level, so its locations need that level's progress too.

-- Pyramid of the Forbidden: its entrance only opens after gathering the
-- inchworms in the Pyramid of the Moons, behind POM's yellow-gem door — i.e.
-- POM unlocked + its Yellow Gem (== being able to complete POM).
function potf_reachable()
    if level_completable("level_potm", {"potm_yellow"}, "potm_gemset") then return 1 end
    return 0
end

-- Korath III Base: reached via the hidden teleporter deep in the Gravitational
-- Damping Hub, past the Hub's green + red doors — GDH unlocked + its Green and
-- Red gems + pogo (the GDH Vitalin Keg's reach, plus the red gem).
function korath_reachable()
    if level_completable("level_gdh", {"gdh_green", "gdh_red"}, "gdh_gemset", true) then return 1 end
    return 0
end



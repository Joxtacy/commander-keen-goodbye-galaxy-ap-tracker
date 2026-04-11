-- logic.lua
-- Custom access rule functions for final-level gating.
-- BWBM (CK4) requires all other CK4 levels to be completable.
-- QED (CK5) requires the End Game region to be reachable.

-- Helper: check if an item code is active.
-- Uses ProviderCountForCode which correctly handles progressive items
-- (codes are only active at the stage that declares them).
local function has(code)
    return Tracker:ProviderCountForCode(code) > 0
end

-- Helper: check if a level's completion requirements are met.
-- A level is completable when:  level unlock  AND  optional pogo/wetsuit/keycard
-- AND  (all required gems  OR  gemset).
local function level_completable(level, gems, gemset, pogo, wetsuit, keycard)
    if not has(level) then return false end
    if pogo and not has("pogo") then return false end
    if wetsuit and not has("wetsuit") then return false end
    if keycard and not has(keycard) then return false end
    if gems then
        local all_gems = true
        for _, g in ipairs(gems) do
            if not has(g) then all_gems = false; break end
        end
        if not all_gems and not has(gemset) then return false end
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
    if not level_completable("level_potm",  {"potm_yellow"},             "potm_gemset")  then return 0 end
    if not level_completable("level_pos",   {"pos_blue"},                "pos_gemset")   then return 0 end
    if not level_completable("level_potga", {"potga_red","potga_green"}, "potga_gemset", true)  then return 0 end
    if not level_completable("level_iot",   {"iot_blue"},                "iot_gemset",   true, true) then return 0 end
    if not level_completable("level_iof",   {"iof_yellow","iof_blue"},   "iof_gemset",  false, true) then return 0 end
    if not level_completable("level_wow",   nil, nil,                                    false, true) then return 0 end
    return 1
end

-- End Game region gate: EFS, RCC, NBI, BMI must be completable
-- (matches Regions.py K5 Hub → End Game connection)
function ck5_endgame_reachable()
    -- Energy Flow Systems: level + all 4 gems or gemset
    if not (has("level_efs") and (
        (has("efs_red") and has("efs_yellow") and has("efs_blue") and has("efs_green")) or
        has("efs_gemset")
    )) then return 0 end
    -- Regulation Control Center: level + R+Y+B gems or gemset
    if not (has("level_rcc") and (
        (has("rcc_red") and has("rcc_yellow") and has("rcc_blue")) or
        has("rcc_gemset")
    )) then return 0 end
    -- Neutrino Burst Injector: level + R+B gems or gemset
    if not (has("level_nbi") and (
        (has("nbi_red") and has("nbi_blue")) or
        has("nbi_gemset")
    )) then return 0 end
    -- Brownian Motion Inducer: level + Y+B gems or gemset
    if not (has("level_bmi") and (
        (has("bmi_yellow") and has("bmi_blue")) or
        has("bmi_gemset")
    )) then return 0 end
    return 1
end


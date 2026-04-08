-- logic.lua
-- Custom access rule functions for final-level gating.
-- BWBM (CK4) and QED (CK5) require all other episode levels to be completable.

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

-- All 11 CK5 levels (other than QED) completable
function ck5_all_completable()
    if not level_completable("level_ivs") then return 0 end
    if not level_completable("level_sc",  {"sc_blue"},                       "sc_gemset",  false, false, "sc_keycard")  then return 0 end
    if not level_completable("level_dtv", {"dtv_yellow"},                    "dtv_gemset", false, false, "dtv_keycard") then return 0 end
    if not level_completable("level_efs", {"efs_green"},                     "efs_gemset", true)  then return 0 end
    if not level_completable("level_dtb", {"dtb_red"},                       "dtb_gemset", false, false, "dtb_keycard") then return 0 end
    if not level_completable("level_rcc", {"rcc_red","rcc_yellow","rcc_blue"}, "rcc_gemset", true) then return 0 end
    if not level_completable("level_dts", {"dts_yellow"},                    "dts_gemset", false, false, "dts_keycard") then return 0 end
    if not level_completable("level_nbi", {"nbi_red","nbi_blue"},            "nbi_gemset", true)  then return 0 end
    if not level_completable("level_dtt", {"dtt_yellow","dtt_blue"},          "dtt_gemset", false, false, "dtt_keycard") then return 0 end
    if not level_completable("level_bmi", {"bmi_yellow","bmi_blue"},          "bmi_gemset", true)  then return 0 end
    if not level_completable("level_gdh", {"gdh_green"},                     "gdh_gemset", true, false, "gdh_keycard") then return 0 end
    return 1
end

#!/usr/bin/env lua
-- Unit tests for scripts/logic.lua (the tracker's access-rule functions).
--
-- logic.lua only depends on the global Tracker:ProviderCountForCode(code), so
-- we stub Tracker with a settable owned-items set, load logic.lua, and assert
-- ck4_all_completable / ck5_endgame_reachable / ck5_all_completable across
-- realistic ownership scenarios — including a regression for the QED Complete
-- bug (all-completable must enforce the End Game region's all-four-EFS-gems
-- gate, not just per-level completion that needs only the EFS Green Gem).
--
-- Run:  lua tools/test_logic.lua   (exit 0 = all pass)

-- --- Tracker stub -------------------------------------------------------
local owned = {}
Tracker = {}
function Tracker:ProviderCountForCode(code)
    return owned[code] and 1 or 0
end

-- Load the code under test (resolve relative to this script).
local here = (arg[0]:match("(.*/)") or "./")
dofile(here .. "../scripts/logic.lua")

-- --- Tiny assert framework ---------------------------------------------
local pass, fail = 0, 0
local function check(name, got, want)
    if got == want then
        pass = pass + 1
    else
        fail = fail + 1
        print(string.format("FAIL: %s — got %s, want %s",
            name, tostring(got), tostring(want)))
    end
end

local function own(...)
    owned = {}
    for _, list in ipairs({ ... }) do
        for _, code in ipairs(list) do owned[code] = true end
    end
end

local function without(list, ...)
    local rm = {}
    for _, code in ipairs({ ... }) do rm[code] = true end
    local out = {}
    for _, code in ipairs(list) do
        if not rm[code] then out[#out + 1] = code end
    end
    return out
end

-- --- Fixtures (mirror Rules.py requirements) ---------------------------
-- CK5 End Game region gate: EFS (all 4 gems), RCC (R+Y+B), NBI (R+B),
-- BMI (Y+B), all requiring pogo.
local CK5_ENDGAME = {
    "pogo", "level_efs", "level_rcc", "level_nbi", "level_bmi",
    "efs_red", "efs_yellow", "efs_blue", "efs_green",
    "rcc_red", "rcc_yellow", "rcc_blue", "nbi_red", "nbi_blue",
    "bmi_yellow", "bmi_blue",
}
local CK5_ENDGAME_GEMSET = {
    "pogo", "level_efs", "level_rcc", "level_nbi", "level_bmi",
    "efs_gemset", "rcc_gemset", "nbi_gemset", "bmi_gemset",
}

-- Every CK5 level (except QED) completable, individual gems.
local CK5_FULL = {
    "pogo",
    "level_ivs", "level_sc", "level_dtv", "level_dtb", "level_dts",
    "level_dtt", "level_efs", "level_rcc", "level_nbi", "level_bmi", "level_gdh",
    "sc_keycard", "dtv_keycard", "dtb_keycard", "dts_keycard",
    "dtt_keycard", "gdh_keycard",
    "sc_blue", "dtv_yellow", "dtb_red", "dts_yellow", "dtt_yellow", "dtt_blue",
    "efs_red", "efs_yellow", "efs_blue", "efs_green",
    "rcc_red", "rcc_yellow", "rcc_blue", "nbi_red", "nbi_blue",
    "bmi_yellow", "bmi_blue", "gdh_green",
}
local CK5_FULL_GEMSET = {
    "pogo",
    "level_ivs", "level_sc", "level_dtv", "level_dtb", "level_dts",
    "level_dtt", "level_efs", "level_rcc", "level_nbi", "level_bmi", "level_gdh",
    "sc_keycard", "dtv_keycard", "dtb_keycard", "dts_keycard",
    "dtt_keycard", "gdh_keycard",
    "sc_gemset", "dtv_gemset", "dtb_gemset", "dts_gemset", "dtt_gemset",
    "efs_gemset", "rcc_gemset", "nbi_gemset", "bmi_gemset", "gdh_gemset",
}

-- Every CK4 level (except BWBM) completable, individual gems.
local CK4_FULL = {
    "pogo", "wetsuit", "stunner",
    "level_bv", "level_sv", "level_pp", "level_cotd", "level_coc", "level_crys",
    "level_hil", "level_sy", "level_mir", "level_lo", "level_potm", "level_pos",
    "level_potga", "level_iot", "level_iof", "level_wow",
    "pp_red", "pp_blue", "cotd_yellow", "crys_blue", "sy_green", "lo_green",
    "potm_yellow", "pos_blue", "potga_red", "potga_green", "iot_blue",
    "iof_yellow", "iof_blue",
}
local CK4_FULL_GEMSET = {
    "pogo", "wetsuit", "stunner",
    "level_bv", "level_sv", "level_pp", "level_cotd", "level_coc", "level_crys",
    "level_hil", "level_sy", "level_mir", "level_lo", "level_potm", "level_pos",
    "level_potga", "level_iot", "level_iof", "level_wow",
    "pp_gemset", "cotd_gemset", "crys_gemset", "sy_gemset", "lo_gemset",
    "potm_gemset", "pos_gemset", "potga_gemset", "iot_gemset", "iof_gemset",
}

-- --- ck5_endgame_reachable ---------------------------------------------
own(CK5_ENDGAME)
check("endgame: full gems", ck5_endgame_reachable(), 1)
own(CK5_ENDGAME_GEMSET)
check("endgame: gemsets", ck5_endgame_reachable(), 1)
own(without(CK5_ENDGAME, "pogo"))
check("endgame: no pogo", ck5_endgame_reachable(), 0)
own(without(CK5_ENDGAME, "efs_red"))
check("endgame: EFS needs all 4 gems", ck5_endgame_reachable(), 0)
own(without(CK5_ENDGAME, "level_bmi"))
check("endgame: missing a hub level", ck5_endgame_reachable(), 0)
own({})
check("endgame: nothing owned", ck5_endgame_reachable(), 0)

-- --- ck5_all_completable -----------------------------------------------
own(CK5_FULL)
check("ck5 all: full", ck5_all_completable(), 1)
own(CK5_FULL_GEMSET)
check("ck5 all: gemsets", ck5_all_completable(), 1)
-- Regression: EFS Green alone satisfies per-level completion, but the End Game
-- region gate still needs all four EFS gems. Pre-fix this returned 1.
own(without(CK5_FULL, "efs_red", "efs_yellow", "efs_blue"))
check("ck5 all: REGRESSION endgame gate (EFS green only)",
    ck5_all_completable(), 0)
own(without(CK5_FULL, "sc_keycard"))
check("ck5 all: missing a keycard", ck5_all_completable(), 0)
own(without(CK5_FULL, "gdh_green"))
check("ck5 all: missing a gem", ck5_all_completable(), 0)
own({})
check("ck5 all: nothing owned", ck5_all_completable(), 0)

-- --- ck4_all_completable -----------------------------------------------
own(CK4_FULL)
check("ck4 all: full", ck4_all_completable(), 1)
own(CK4_FULL_GEMSET)
check("ck4 all: gemsets", ck4_all_completable(), 1)
own(without(CK4_FULL, "pogo"))
check("ck4 all: no pogo (COTD/SY/MIR/POTGA/IOT gate)",
    ck4_all_completable(), 0)
own(without(CK4_FULL, "wetsuit"))
check("ck4 all: no wetsuit (IOT/IOF/WOW gate)", ck4_all_completable(), 0)
own(without(CK4_FULL, "stunner"))
check("ck4 all: no stunner (POS gate)", ck4_all_completable(), 0)
own(without(CK4_FULL, "pp_red"))
check("ck4 all: missing a gem", ck4_all_completable(), 0)
own({})
check("ck4 all: nothing owned", ck4_all_completable(), 0)

-- --- Summary -----------------------------------------------------------
print(string.format("\n%d passed, %d failed", pass, fail))
os.exit(fail == 0 and 0 or 1)

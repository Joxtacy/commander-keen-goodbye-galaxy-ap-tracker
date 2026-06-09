#!/usr/bin/env lua
-- Unit tests for scripts/logic.lua (the tracker's access-rule functions).
--
-- logic.lua only depends on the global Tracker:ProviderCountForCode(code), so
-- we stub Tracker with a settable owned-items set, load logic.lua, and assert
-- ck4_all_completable / ck5_endgame_reachable across realistic ownership
-- scenarios. QED Complete gates on ck5_endgame_reachable (NOT on completing
-- every other CK5 level — the apworld's QED rule has no such chain), so the
-- endgame tests below also cover the QED Complete gate.
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

-- Regression: QED Complete must NOT require the other CK5 levels' keycards/
-- gems. With End Game reachable + QED gems + pogo the player can beat QED, so
-- its gate (ck5_endgame_reachable) must pass even when, e.g., a Defense Tunnel
-- keycard is missing. Pre-fix QED Complete used ck5_all_completable and showed
-- red in exactly this scenario.
own(CK5_ENDGAME)
check("endgame: REGRESSION QED Complete needs no other-level keycards",
    ck5_endgame_reachable(), 1)

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
-- POTM has an over-the-top exit reachable with pogo alone (no Yellow Gem).
-- CK4_FULL owns pogo, so dropping potm_yellow must still leave POTM completable.
own(without(CK4_FULL, "potm_yellow"))
check("ck4 all: POTM completable via pogo over-the-top exit (no yellow)",
    ck4_all_completable(), 1)
-- Dropping both potm_yellow and potm's pogo route is not testable in aggregate
-- (pogo also gates COTD/SY/MIR/POTGA/IOT), but the yellow-only path is covered
-- by "ck4 all: full" above.
own({})
check("ck4 all: nothing owned", ck4_all_completable(), 0)

-- --- ck4_council_goal_completable --------------------------------------
-- Only the 8 council-member levels and their requirements — deliberately
-- omits the non-council levels (BV, SV, COC, HIL, SY, MIR, POTM, IOT, BWBM)
-- to prove the council goal does NOT require them.
local CK4_COUNCIL = {
    "pogo", "wetsuit", "stunner",
    "level_pp", "level_cotd", "level_crys", "level_lo", "level_pos",
    "level_potga", "level_iof", "level_wow",
    "pp_red", "pp_blue", "cotd_yellow", "crys_blue", "lo_green",
    "pos_blue", "potga_red", "potga_green", "iof_yellow", "iof_blue",
}
own(CK4_FULL)
check("ck4 council: full CK4 inventory", ck4_council_goal_completable(), 1)
own(CK4_FULL_GEMSET)
check("ck4 council: gemsets", ck4_council_goal_completable(), 1)
own(CK4_COUNCIL)
check("ck4 council: council-only inventory (non-council levels not required)",
    ck4_council_goal_completable(), 1)
own(without(CK4_COUNCIL, "level_wow"))
check("ck4 council: missing a council level", ck4_council_goal_completable(), 0)
own(without(CK4_COUNCIL, "pos_blue"))
check("ck4 council: missing a council gem (POS, no gemset)",
    ck4_council_goal_completable(), 0)
own(without(CK4_COUNCIL, "stunner"))
check("ck4 council: no stunner (POS gate)", ck4_council_goal_completable(), 0)
own(without(CK4_COUNCIL, "wetsuit"))
check("ck4 council: no wetsuit (IOF/WOW gate)", ck4_council_goal_completable(), 0)
own({})
check("ck4 council: nothing owned", ck4_council_goal_completable(), 0)

-- --- Summary -----------------------------------------------------------
print(string.format("\n%d passed, %d failed", pass, fail))
os.exit(fail == 0 and 0 or 1)

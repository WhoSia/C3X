#!/usr/bin/env python3
"""January prospective TT pair court post-outcome physical event survival audit.

Audits ALL 16 frozen source games and both prespecified selectors, not just
cases with a favorable response. This audit is descriptive after outcomes.
"""
import argparse,hashlib,json
from collections import Counter
from pathlib import Path

SHA="9d7ff1d8c5e019a5ab5b95441468da0ad49951adc756b8669db7853b82649470"
def need(v,s):
    if not v:raise RuntimeError("C3X018_JAN_PAIR_AUDIT_"+s)
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--native",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    b=Path(a.native).read_bytes()
    need(hashlib.sha256(b).hexdigest()==SHA,"SOURCE_RAW_SHA")
    j=json.loads(b);need(len(j["cases"])==16,"DENOMINATOR")
    tally=Counter();rows=[];uniques=set()
    for c in j["cases"]:
        need(c["status"]=="VALID","INVALID_SOURCE_GAME")
        for typ in ("STRICT","BROAD"):
            r=c["selectors"][typ]
            if r["status"]=="NO_ELIGIBLE_PAIR":
                tally[typ+"_no_eligible"]+=1
                continue
            pair=r["selected_passive_pair"]
            id_key=(c["id"],tuple(pair["root_calls"]),
                  tuple(pair["physical"][k] for k in ("key64","slot","epoch")))
            uniques.add(id_key)
            arms=r["arms"];first,second=pair["root_calls"]
            need(arms["FIRST"]["blocked"]==arms["SECOND"]["blocked"]==1,
                 "BOTH_SOURCE_SINGLETONS_MUST_EACH_FIRE")
            need(arms["ZERO"]["blocked"]==0,"NEGATIVE_SHAM")
            need(arms["BOTH"]["UCI"]==arms["FIRST"]["UCI"],
                 "BOTH_AND_FIRST_FULL_CORE_NONIDENTICAL")
            tally[typ+"_pair_count"]+=1
            tally[typ+"_both_source_calls_realized"]+=r["both_source_calls_realized"]
            tally[typ+"_both_equal_first_full_core"]+=1
            tally[typ+"_first_full_core_changed"]+=arms["FIRST"]["full_core_changed"]
            tally[typ+"_second_full_core_changed"]+=arms["SECOND"]["full_core_changed"]
            tally[typ+"_both_root_flip"]+=arms["BOTH"]["bestmove_changed"]
            group_events=arms["BOTH"]["source_block_events"]
            need(group_events and group_events[0]["root_call"]==first,
                 "FIRST_SOURCE_READER_NOT_ACTUAL_FIRST_BLOCK")
            missed=(len(group_events)==1)
            second_enter=any(e["kind"]=="window_enter" and
                             e.get("root_call")==second
                             for e in arms["BOTH"]["source_root_events"])
            same_physical_at_second=[
                e for e in arms["BOTH"]["physical_reader_payloads"]
                if e["reader_root_call"]==second]
            if missed:
                need(second_enter,"MISSING_SECOND_ROOT_CALL_ENTRY_FOR_SCREEN")
                need(not same_physical_at_second,
                     "SECOND_ROOT_V_VALUE_SNAPSHOT_PRESENT_BUT_UNBLOCKED")
                tally[typ+"_second_root_call_entered_but_source_TT_value_read_absent"]+=1
            else:
                need(len(group_events)==2 and group_events[1]["root_call"]==second,
                     "BOTH_READER_EVENTS_DID_NOT_MATCH_PAIR")
            rows.append({"game_id":c["id"],"selector":typ,
                "selected_root_calls":[first,second],
                "actual_group_reader_blocks":[e["root_call"] for e in group_events],
                "both_full_UCI_equals_first":True,
                "second_root_call_entered":second_enter,
                "second_same_target_pre_gate_value_snapshots":len(same_physical_at_second),
                "both_source_calls_realized":r["both_source_calls_realized"],
                "group_bestmove_changed":arms["BOTH"]["bestmove_changed"],
                "first_full_UCI_changed":arms["FIRST"]["full_core_changed"],
                "second_full_UCI_changed":arms["SECOND"]["full_core_changed"]})
    need(len(rows)==31 and len(uniques)==25,"PAIR_CARDINALITY")
    need(sum(x["both_source_calls_realized"] for x in rows)==2,"TWO_REALIZED_PAIRS")
    need(sum(not x["both_source_calls_realized"] for x in rows)==29,"TWENTYNINE_LOST_PAIRS")
    need(not any(x["group_bestmove_changed"] for x in rows),"JANUARY_PAIR_ROOT_EFFECT_UNEXPECTED")
    result={
      "schema":"c3x018-Jan2026-independent-cross-window-pair-source-contact-survival-audit-v1",
      "source_native_SHA256":SHA,
      "study_status":"POST_OUTCOME_DESCRIPTIVE_NOT_NEW_PREREGISTRATION",
      "new_external_game_count":16,
      "original_strict_eligible":15,"original_broad_eligible":16,
      "pair_selector_records":31,
      "physically_distinct_within_game_candidate_pairs":25,
      "same_pair_chosen_by_two_selectors":6,
      "both_source_calls_fired_in_group":2,
      "only_first_selected_source_call_fired_in_group":29,
      "all_thirty_one_group_final_UCI_equal_first_only":True,
      "all_29_second_root_call_window_entry_observed":True,
      "all_29_second_same_physical_TT_pre_gate_value_reads_absent":True,
      "per_selector_tallies":dict(tally),
      "all_source_records":rows,
      "interpretation":"First physically selected reader gate screens the second nominated physical value-as-evaluation reader from the observed source stream while later root search CALL still executes, or two selected source reads both fire but later gate causes no marginal final UCI difference.",
      "rival_causes_to_identify_next":[
        "The old position Zobrist key is not visited in the second root subsearch",
        "The key is visited but TT probe misses or points to a replaced payload",
        "A TT probe occurs but the bound-qualified TT value-as-eval consumption branch is not eligible",
        "The source-relative writer age/window threshold changes without changing TT probe identity"],
      "limits":[
        "Source root call existence does not imply identity of recursive search nodes across counterfactual arms",
        "31 selector arms include six overlaps of exact game-target-call pair, not 31 independent experiments",
        "Prespecified J2,J3,J4 all failed; later source diagnostics cannot rescue their independent test",
        "All 16 source passive streams reached first 2048 reader cap; not an exhaustive search census",
        "The raw TT value witness is generated before optional V source guard; it cannot alone prove a block"]
    }
    path=Path(a.out);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("C3X018_JANUARY_PAIR_INTERVENTION_SURVIVAL_AUDIT",
          json.dumps({"game_count":16,"role_arms":31,"unique_source_pairs":25,
                      "second_window_entered_but_same_TT_value_read_absent":29,
                      "both_realized":2,"all_group_equals_first_UCI":True},sort_keys=True))
if __name__=="__main__":main()

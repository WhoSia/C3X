#!/usr/bin/env python3
"""C3X 0.14 descriptive posthoc structural census of pinned physical TT ancestry.

Never treats nested worlds / cold repeats as independent, or exploratory
event strata as precommitted causal predictive laws.
"""
import argparse,hashlib,json,collections
from pathlib import Path

RAW_SHA="a152935764727ca5533181fe0c2747b6c1aecf996b87542cb30178f0a39592d2"
BOUND={1:"UPPER",2:"LOWER",3:"EXACT"}
SITES={1:"TABLEBASE",2:"STATIC_EVAL_SAVE",3:"PROBCUT",
       4:"MAIN_TERMINAL",5:"Q_STAND_PAT",6:"Q_TERMINAL",0:"UNATTRIBUTED"}

def get(path):
    b=Path(path).read_bytes()
    if hashlib.sha256(b).hexdigest()!=RAW_SHA:raise RuntimeError("RAW_NATIVE_TT_SOURCE_CHANGED")
    x=json.loads(b)
    assert x["schema"]=="c3x-014-source-native-TT-physical-slot-last-writer-and-single-consumer-v1"
    assert x["source_game_groups"]==14 and x["legally_reached_worlds"]==28
    assert x["actual_engine_processes"]==224
    assert x["complete_all_four_arms_parent_native_exact_equivalence"]==224
    assert x["technical_cold_repro_worlds"]==28
    assert x["all_ONE_MAIN_blocked_exactly_one_return"]==56
    assert not x["P1_four_sealed_holdout_groups_opened"]
    return x
def summarize(src):
    first=[r for r in src["actual_raw_world_runs"] if r["cold_repeat"]==1]
    assert len(first)==28 and len({r["source_group"] for r in first})==14
    assert all(r["all_four_arms_original_224_run_behavior_identical"] for r in first)
    fields={
      "first_blocked_native_depth":lambda r:r["one_first_blocked_consumer_and_last_writer"]["first_blocked_depth"],
      "first_blocked_native_ply":lambda r:r["one_first_blocked_consumer_and_last_writer"]["first_blocked_ply"],
      "first_blocked_TT_bound":lambda r:r["one_first_blocked_consumer_and_last_writer"]["first_blocked_bound"],
      "first_last_writer_source":lambda r:r["one_first_blocked_consumer_and_last_writer"]["first_writer_site"]}
    strata={}
    for key,fn in fields.items():
        groups=collections.defaultdict(list)
        for r in first:groups[str(fn(r))].append(r)
        d={}
        for name,rows in sorted(groups.items(),key=lambda z:int(z[0])):
            changed=[r["white_cp_OFF_ONE_MAIN_MAIN"][0]!=r["white_cp_OFF_ONE_MAIN_MAIN"][1] for r in rows]
            root=[r["bestmoves_OFF_ONE_MAIN_MAIN"][0]!=r["bestmoves_OFF_ONE_MAIN_MAIN"][1] for r in rows]
            signs=[(r["white_cp_OFF_ONE_MAIN_MAIN"][0] is not None and
                    r["white_cp_OFF_ONE_MAIN_MAIN"][1] is not None and
                    r["white_cp_OFF_ONE_MAIN_MAIN"][0]*r["white_cp_OFF_ONE_MAIN_MAIN"][1]<0) for r in rows]
            d[name]={"worlds":len(rows),"cp_gap_changed":sum(changed),"UCI_root_label_changed":sum(root),
                     "strict_cp_sign_inverted":sum(signs)}
        strata[key]=d
    hist={}
    for r in first:hist.setdefault(r["source_group"],{})[r["world"]]=r
    assert len(hist)==14 and all(set(v)=={"PLAYED_HISTORY","CONCEPT_SHAM_HISTORY"} for v in hist.values())
    pair=[]
    for group,worlds in sorted(hist.items()):
        play=worlds["PLAYED_HISTORY"];sham=worlds["CONCEPT_SHAM_HISTORY"]
        a=play["one_first_blocked_consumer_and_last_writer"]
        b=sham["one_first_blocked_consumer_and_last_writer"]
        pair.append({"source_group":group,"round":play["source_round"],
          "same_chess_pawn_feature_contrast":True,"different_legal_last_black_move":play["original_black_move"]!=sham["original_black_move"],
          "first_blocked_pos_key_same":a["first_blocked_key"]==b["first_blocked_key"],
          "first_blocked_source_writer_site_same":a["first_writer_site"]==b["first_writer_site"],
          "first_blocked_depth_same":a["first_blocked_depth"]==b["first_blocked_depth"],
          "played_world_one_return_cp_shift":play["white_cp_OFF_ONE_MAIN_MAIN"][1]-play["white_cp_OFF_ONE_MAIN_MAIN"][0],
          "sham_world_one_return_cp_shift":sham["white_cp_OFF_ONE_MAIN_MAIN"][1]-sham["white_cp_OFF_ONE_MAIN_MAIN"][0]})
    writer_seqs=[r["one_first_blocked_consumer_and_last_writer"]["first_writer_sequence"] for r in first]
    site_saves=[r["one_slot_summary"]["saves"] for r in first]
    result={
       "schema":"c3x-014-source-native-first-TT-return-event-structure-posthoc-census-v1",
       "single_formal_phase":"C3X 0.14","P_internal_only":True,
       "actual_source_sha256":RAW_SHA,"source_group_count":14,"worlds":28,
       "independent_chess_game_groups":14,"cold_repeats_excluded_as_new_independent_units":True,
       "analysis_is_posthoc_exploratory_not_frozen_predictive_test":True,
       "strata_by_actual_first_TT_consumer_depth_ply_bound_writer_site":strata,
       "writer_site_decoding":{str(k):v for k,v in SITES.items()},
       "TT_bound_decoding":{str(k):v for k,v in BOUND.items()},
       "first_blocked_TT_writer_sequence_min_median_max":[min(writer_seqs),sorted(writer_seqs)[len(writer_seqs)//2-1:len(writer_seqs)//2+1],max(writer_seqs)],
       "first_blocked_has_previous_different_key_slot_reuses_worlds":sum(r["one_first_blocked_consumer_and_last_writer"]["first_writer_slot_replacements"]>0 for r in first),
       "other_physical_slots_reused_different_fullkey_in_search_worlds":sum(r["one_slot_summary"]["other_fullkey_slot_reuses"]>0 for r in first),
       "slots_with_any_last_writer_full64key_match_worlds":sum(r["one_first_blocked_consumer_and_last_writer"]["first_writer_key_match"] for r in first),
       "number_TTEntry_save_calls_per_ONE_MAIN_search_min_max":[min(site_saves),max(site_saves)],
       "source_pair_14_legally_reached_chess_world_differences":pair,
       "first_blocked_event_key_same_between_pair_count":sum(x["first_blocked_pos_key_same"] for x in pair),
       "first_blocked_producer_category_same_between_pair_count":sum(x["first_blocked_source_writer_site_same"] for x in pair),
       "first_blocked_depth_same_between_pair_count":sum(x["first_blocked_depth_same"] for x in pair),
       "method_limitations":[
         "All reported subgroup cells are discovered after the search results; do NOT use significance tests as independent confirmatory evidence.",
         "The native TT word stores only low16 key bits in a 3-entry physical cluster; the separate sidecar measures full-key writer/slot relationships for source-verified runs.",
         "Physical last writer site is not whole program-value provenance or chess-domain causal mediator.",
         "Same source pawn feature contrast across legal alternative board contexts does not mean identical engine initial position or event key.",
         "No 0.15 or 0.16 formal research stage is opened by this census."
       ],
       "P1_four_source_game_holdout_opened":False}
    return result

def main():
    p=argparse.ArgumentParser();p.add_argument("--input",required=True);p.add_argument("--out-json",required=True);p.add_argument("--out-md",required=True)
    a=p.parse_args();out=summarize(get(a.input))
    Path(a.out_json).write_text(json.dumps(out,indent=2,ensure_ascii=False)+"\n")
    lines=["# C3X 0.14 — Actual TT Event Producer–Consumer Structural Census",
           "Posthoc exploratory descriptive counts, 14 prior development game groups; 28 nested legal worlds.",
           "Only C3X 0.14 formally open; no premature 0.15 or 0.16."]
    for dimension,groups in out["strata_by_actual_first_TT_consumer_depth_ply_bound_writer_site"].items():
        lines.append("## "+dimension)
        lines.append("| Observed value | Source worlds | Cp-gap changed | UCI root label changed | Strict sign inverse |")
        lines.append("|---|---:|---:|---:|---:|")
        for k,v in groups.items():
            lines.append(f"| {k} | {v['worlds']} | {v['cp_gap_changed']} | {v['UCI_root_label_changed']} | {v['strict_cp_sign_inverted']} |")
    lines.append("## Constraints")
    lines.extend("- "+z for z in out["method_limitations"])
    Path(a.out_md).write_text("\n\n".join(lines)+"\n")
    assert out["source_group_count"]==14 and out["worlds"]==28
    assert out["slots_with_any_last_writer_full64key_match_worlds"]==28
    assert out["first_blocked_has_previous_different_key_slot_reuses_worlds"]==0
    assert out["other_physical_slots_reused_different_fullkey_in_search_worlds"]==10
    print("C3X014_NATIVE_TT_EVENT_STRUCTURE_CENSUS_PASS",json.dumps({
        "groups":out["source_group_count"],"worlds":out["worlds"],
        "depth_strata":out["strata_by_actual_first_TT_consumer_depth_ply_bound_writer_site"]["first_blocked_native_depth"],
        "bound_strata":out["strata_by_actual_first_TT_consumer_depth_ply_bound_writer_site"]["first_blocked_TT_bound"],
        "global_other_key_reuse_worlds":out["other_physical_slots_reused_different_fullkey_in_search_worlds"]}),flush=True)
if __name__=="__main__":main()

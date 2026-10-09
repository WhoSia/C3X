#!/usr/bin/env python3
"""C3X 0.14 source pinned first-64 true main TT-return census.

Only OFF native engine; 28 preselected legal history worlds × cold 2.
Cross-check whole root search vs previous 168-process SF16 OFF baseline.
"""
from __future__ import annotations
import argparse,hashlib,json,collections
from pathlib import Path
from c3x_014_single_TT_event_pathway_court import run,semantic

SOURCE_SHA="0080f4f108471137f8d9d0908e3c879e33351ad8bdd4fbf0fdda83d47f6075b2"
PRIOR_SHA="742ec105c73c6e7ec28de2c843a452df6fb7d4e95f10e16d3ce90956184e4a7c"
CAP=64
ORIG_PATH=("picker_main_nodes","picker_main_ttmove","lmr_invoked","lmr_with_reduction",
 "history_quiet_update","history_continuation_update","main_evaluate_calls",
 "main_tt_eval_reads","main_alpha_beta_move_cutoffs","main_tt_save_terminal",
 "first_blocked_key","first_blocked_ply","first_blocked_depth",
 "first_blocked_bound","first_blocked_tt_value","first_blocked_beta",
 "first_eligible_key","first_eligible_ply","first_eligible_depth",
 "first_eligible_bound","first_eligible_tt_value","first_eligible_beta")
WRITERS={1:"MAIN_TABLEBASE",2:"MAIN_STATIC_EVAL",3:"MAIN_PROBCUT",
         4:"MAIN_TERMINAL",5:"QSEARCH_EARLY",6:"QSEARCH_TERMINAL"}
BOUNDS={1:"UPPER",2:"LOWER",3:"EXACT"}
def filehash(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def require(x,msg):
    if not x:raise RuntimeError(msg)
def normalized(z):
    q=semantic(z);q["ranks"]={str(k):v for k,v in q["ranks"].items()}
    return q
def compare(z,old):
    require(normalized(z)==normalized(old),"CENSUS_LOGGER_CHANGED_UCI_CHESS_OUTPUT")
    require(z["native_tt"]==old["native_tt"],"CENSUS_LOGGER_CHANGED_NATIVE_EP9")
    require(z["native_completed"]==old["native_completed"],"CENSUS_LOGGER_CHANGED_TRUE_COMPLETED_DEPTH")
    for name in ORIG_PATH:
        require(z["mechanism_path"][name]==old["mechanism_path"][name],
                "CENSUS_LOGGER_CHANGED_NATIVE_SEARCH_PATH_"+name)
    a,b=z["slot_writer_summary"],old["slot_writer_summary"]
    for name in ("saves","full","move_only","no_op","recycled","probes","probe_hits"):
        require(a[name]==b[name],"CENSUS_LOGGER_CHANGED_NATIVE_TT_WRITER_"+name)
    # New observational sidecar lookups occur for EACH recorded return, and
    # do not call Stockfish TT.probe. All such lookups MUST be exact fullkey.
    k=z["tt_natural_return_census"]["recorded"]
    require(a["first_key_match"]==b["first_key_match"]+k,
            "TAPE_SIDE_CAR_READ_INCREMENT_NOT_EXACT")
    require(a["first_unknown"]==b["first_unknown"] and
            a["first_key_mismatch"]==b["first_key_mismatch"],
            "TAPE_INTRODUCED_UNACCOUNTED_MISSING_WRITER")
def make_worlds(source):
    found=[g for g in source["cases"] if g["concept_changing_world"] and g["concept_preserving_world"]]
    require(len(found)==14,"FROZEN_GAMES_NOT_14")
    for g in found:
        for world,black,fen in (
          ("PLAYED_HISTORY",g["original_black18"],g["original_legal_history_root_fen"]),
          ("CONCEPT_SHAM_HISTORY",g["concept_preserving_world"]["black18_uci"],
             g["concept_preserving_world"]["root_full_FEN"])):
            yield g,world,fen,g["first_17_ply_path_uci"]+[black]

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",required=True);p.add_argument("--previous",required=True)
    p.add_argument("--bin",required=True);p.add_argument("--out",required=True)
    args=p.parse_args()
    require(filehash(args.source)==SOURCE_SHA,"SOURCE_FROZEN_SHA")
    require(filehash(args.previous)==PRIOR_SHA,"PARENT_ACTUAL_168_SF16_SHA")
    src=json.loads(Path(args.source).read_bytes())
    prior=json.loads(Path(args.previous).read_bytes())
    require(prior["schema"]=="c3x-014-sf16-exact-first-returnable-event-and-writer-ply-depth-context-v1","PARENT_SCHEMA")
    require(prior["new_native_engine_processes"]==168 and
            prior["OFF_ONE_MAIN_MAIN_first_eligible_full_event_identical_in_all_28_worlds"]==28,
            "NOT_PREVIOUSLY_MATCHED_SOURCE_EVENT")
    old={(z["group"],z["world"],z["cold"]):z for z in prior["all_cold_native_arm_outcomes"]}
    require(len(old)==56,"BASELINE_56")
    cells=[]
    for i,(g,world,fen,hist) in enumerate(make_worlds(src),1):
        for cold in (1,2):
            r=run(args.bin,fen,g["root_candidate_pair"],hist,"OFF",capture_return_tape=True)
            compare(r,old[(g["source_group"],world,cold)]["arms"]["OFF"])
            events=r["tt_natural_return_prefix"]
            for e in events:
                require(e["writer_known"]==1,"FIRST64_NATIVE_UNKNOWN_PRODUCER")
                require(e["full64_match"]==1 and e["key"]==e["writer_key"],
                        "SOURCE_NATIVE_FULLKEY_WRITER_MISMATCH")
                require(e["tt_bound"]==e["writer_bound"],"BOUND_RECORD_MISMATCH")
                require(e["writer_class"] in WRITERS,"UNKNOWN_SF16_WRITER_CLASS")
                require(e["tt_bound"] in BOUNDS,"UNKNOWN_SF16_BOUND")
                require(e["slot"] in (0,1,2),"TT_SLOT_GEOMETRY_INVALID")
                require(e["depth"]<=e["writer_depth"],"RETURN_WITH_SHALLOW_UNQUALIFIED_DEPTH")
                require(e["tt_value"]>=e["beta"] if e["tt_bound"]==2 else
                        (e["tt_value"]<e["beta"] if e["tt_bound"]==1 else True),
                        "RETURN_BOUND_INCOMPATIBLE_WITH_BETA")
            first=events[0]
            parent=old[(g["source_group"],world,cold)]["exact_pretreatment_first_event"]
            for field,expected in (
                ("key",parent["first_eligible_key"]),
                ("ply",parent["first_eligible_ply"]),
                ("depth",parent["first_eligible_depth"]),
                ("tt_bound",parent["first_eligible_bound"]),
                ("tt_value",parent["first_eligible_tt_value"]),
                ("beta",parent["first_eligible_beta"])):
                require(first[field]==expected,"SOURCE_EVENT_FIRST_MUST_MATCH_PREVIOUS_"+field)
            row={"source_group":g["source_group"],"official_round":g["official_original_game_headers"]["Round"],
                "legal_world":world,"cold_repeat":cold,"history":hist,
                "full_FEN":fen,"white_root_candidates":g["root_candidate_pair"],
                "real_main_tt_returns_all":r["tt_natural_return_census"]["taken_total"],
                "prefix_K":CAP,"actual_event_prefix":events,"native":r}
            cells.append(row)
            print("C3X014_SOURCE_TT_TAKEN_EVENT_PREFIX_REAL",i,row["official_round"],
                  world,cold,"actual_taken",row["real_main_tt_returns_all"],
                  "prefix",len(events),
                  "writer_types",dict(collections.Counter(WRITERS[e["writer_class"]] for e in events)),flush=True)
    require(len(cells)==56,"MISSING_FROZEN_WORLD_CELLS")
    matched=0
    for g,world,_,_ in make_worlds(src):
        pair=[z for z in cells if z["source_group"]==g["source_group"] and z["legal_world"]==world]
        require(len(pair)==2,"DUPLICATE_COLD_WORLD")
        if pair[0]["native"]==pair[1]["native"]:matched+=1
    require(matched==28,"COLD_TT_EVENT_SEQUENCE_NOT_REPRODUCIBLE")
    first=[z for z in cells if z["cold_repeat"]==1]
    events=[e for z in first for e in z["actual_event_prefix"]]
    def tally(field,mapping=None):
        return dict(collections.Counter(mapping.get(e[field],e[field]) if mapping else e[field] for e in events))
    def hist(seq):
        return dict(collections.Counter(seq))
    result={"schema":"c3x-014-naturally-taken-first64-main-TT-return-producer-and-alpha-beta-census-v1",
      "formal_study":"C3X 0.14","no_new_formal_P_substage":True,
      "source_worlds_sha256":SOURCE_SHA,"previous_native_matched_first_event_sha256":PRIOR_SHA,
      "groups":14,"worlds":28,"technical_cold_restarts":2,
      "actual_native_SF16_engine_processes":56,
      "native_output_and_preexisting_path_replayed_against_previous":56,
      "native_cold_world_event_sequence_equal":matched,
      "prefix_cap_per_world":CAP,
      "first_cold_all_actual_naturally_taken_TT_return_count":sum(z["real_main_tt_returns_all"] for z in first),
      "first_cold_bounded_prefix_event_count":len(events),
      "worlds_with_at_least_K_returns":sum(z["real_main_tt_returns_all"]>=CAP for z in first),
      "first_cold_writer_class_distribution_over_prefix":tally("writer_class",WRITERS),
      "first_cold_bound_distribution_over_prefix":tally("tt_bound",BOUNDS),
      "first_cold_depth_difference_distribution":hist(e["writer_depth"]-e["depth"] for e in events),
      "first_cold_writer_key_64bit_matches":sum(e["full64_match"]==1 for e in events),
      "first_cold_events_reused_slots_with_another_key":sum(e["slot_replacements"]>0 for e in events),
      "first_cold_return_events_from_same_ply_writer":sum(e["ply"]==e["writer_ply"] for e in events),
      "first_cold_return_events_with_nontrivial_beta_window":sum(e["alpha"]<e["beta"] for e in events),
      "each_source_group_world_census_and_full_raw_engine":cells,
      "P1_four_sealed_game_holdout_opened":False,
      "causal_value_production_subtrees_fully_identified":False,
      "latent_stockfish_strategic_concept_discovered":False,
      "scientific_limits":[
         "First 64 chronologically taken main TT bound returns form a prefix, not random sample. All-count denominator and coverage retained.",
         "Event-level observations are nested within 28 legal worlds from 14 already studied games; never use event count as statistical chess games.",
         "Last native full-field TTEntry save class and saved bound/score do not establish full alpha-beta recursive ancestry or chess strategy ontology.",
         "Depth, rule50/TT-bound guards are native SF16, with one global thread, fixed depth12 and pinned original source.",
         "An exact full64 sidecar key match is stronger than native lower16 stored key match but does not rule out all engine TT hash collisions.",
         "This experiment observes OFF naturally taken TT returns; MAIN blocked-path counterfactuals may reach different later TT events."
      ]}
    out=Path(args.out);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    print("C3X014_FIRST64_TT_NATURAL_RETURN_CENSUS_VERDICT",json.dumps({
      "worlds":28,"runs":56,"cold_pairs":matched,
      "return_total":result["first_cold_all_actual_naturally_taken_TT_return_count"],
      "prefix_count":len(events),
      "writers":result["first_cold_writer_class_distribution_over_prefix"],
      "bounds":result["first_cold_bound_distribution_over_prefix"],
      "full64_matches":result["first_cold_writer_key_64bit_matches"],
      "slot_reuses":result["first_cold_events_reused_slots_with_another_key"]}),flush=True)
if __name__=="__main__":main()

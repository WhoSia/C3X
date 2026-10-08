#!/usr/bin/env python3
"""C3X 0.14 in-stage internal P3 — depth-indexed native TT response surface.

Uses the already-exposed 16 P2 developmental games. NEVER loads the P1 holdout.
No equality of computation, true minimax, chess strategy or mediator identified.
"""
from __future__ import annotations
import argparse,hashlib,json,statistics
from collections import defaultdict
from pathlib import Path
from c3x_014_p2_new16_native_tt_score_choice_court import run,eq,h

PARENT_SHA="0fd87345c9cc4b0e23f8fac6c669ec328254178da424268303e99ee6159f81e3"
DEPTHS=(11,12,13)
REPEATS=(1,2)

def sign(x):
    if x is None:return "CENSORED"
    if x>0:return "POSITIVE"
    if x<0:return "NEGATIVE"
    return "TIE"

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--p2-source-panel",required=True)
    ap.add_argument("--clean",required=True)
    ap.add_argument("--ep9",required=True)
    ap.add_argument("--out",required=True)
    a=ap.parse_args()
    if h(a.p2_source_panel)!=PARENT_SHA:
        raise SystemExit("P3_PARENT_NATIVE_DATA_SHA256_FAILURE")
    p=json.loads(Path(a.p2_source_panel).read_bytes())
    assert p["schema"]=="c3x-014-p2-real-new16-group-typed-native-tt-score-choice-court-v1"
    assert len(p["cases"])==64 and p["clean_vs_sham_exact_all"] and not p["p1_four_holdout_games_opened"]
    groups=[x for x in p["cases"] if x["depth"]==12 and x["repeat"]==1]
    assert len(groups)==16 and len({x["group"] for x in groups})==16
    cases=[]
    for idx,source in enumerate(groups,start=1):
        for d in DEPTHS:
            for cold in REPEATS:
                args=(source["fen"],source["pair"],d)
                clean=run(a.clean,*args,"CLEAN")
                off=run(a.ep9,*args,"OFF")
                sham=eq(clean)==eq(off)
                main=run(a.ep9,*args,"MAIN")
                if main["tt"].get("mode")!=1 or main["tt"]["q_blocked"]!=0:
                    raise RuntimeError("P3_INSTRUMENT_WRONG_NATIVE_SITE")
                offgap=off["signed_white_cp_gap"];maingap=main["signed_white_cp_gap"]
                strict=(offgap is not None and maingap is not None and offgap*maingap<0)
                boundary_tie=(offgap is not None and maingap is not None and (offgap==0 or maingap==0))
                nodes_off=off["final_MultiPV"][1]["nodes"]
                nodes_main=main["final_MultiPV"][1]["nodes"]
                case={
                    "source_group_hash":source["group"],
                    "source_game_id":source["game"],
                    "round":source["round"],
                    "full_root_fen":source["fen"],
                    "legal_pair":source["pair"],
                    "requested_equal_depth":d,
                    "cold_repeat":cold,
                    "clean":clean,"off":off,"main":main,
                    "clean_vs_instrumented_off_sham_exact":sham,
                    "observed_native_MAIN_cutoffs_blocked":main["tt"]["main_blocked"],
                    "off_root_white_cp_gap":offgap,
                    "main_root_white_cp_gap":maingap,
                    "signed_gap_status_off":sign(offgap),
                    "signed_gap_status_MAIN":sign(maingap),
                    "strict_nonzero_cp_sign_inversion":strict,
                    "zero_margin_endpoint":boundary_tie,
                    "bestmove_label_changed":off["bestmove"]!=main["bestmove"],
                    "same_requested_depth_not_equal_nodes":nodes_off!=nodes_main,
                    "rank1_reported_nodes_off":nodes_off,
                    "rank1_reported_nodes_main":nodes_main,
                    "MAIN_vs_OFF_rank1_node_ratio":nodes_main/nodes_off if nodes_off else None
                }
                cases.append(case)
                print("P3_FIXED_DEPTH",idx,source["round"],"d",d,"cold",cold,
                    "sham",sham,"gap",offgap,maingap,"sign",strict,
                    "move",off["bestmove"],main["bestmove"],
                    "nodes",nodes_off,nodes_main,flush=True)
    assert len(cases)==96
    equal_all=all(c["clean_vs_instrumented_off_sham_exact"] for c in cases)
    paired=0
    for g in groups:
        for depth in DEPTHS:
            pair=[c for c in cases if c["source_group_hash"]==g["group"] and c["requested_equal_depth"]==depth]
            assert len(pair)==2
            a1,a2=pair
            if all(eq(a1[z])==eq(a2[z]) for z in ("clean","off","main")):paired+=1
    perdepth={}
    for d in DEPTHS:
        samples=[c for c in cases if c["requested_equal_depth"]==d and c["cold_repeat"]==1]
        perdepth[str(d)]={
            "source_game_group_count":len(samples),
            "strict_cp_sign_inversion_count":sum(c["strict_nonzero_cp_sign_inversion"] for c in samples),
            "bestmove_label_change_count":sum(c["bestmove_label_changed"] for c in samples),
            "changed_bestmove_at_zero_margin_count":sum(c["bestmove_label_changed"] and c["zero_margin_endpoint"] for c in samples),
            "native_MAIN_cutoff_blocked_groups":sum(c["observed_native_MAIN_cutoffs_blocked"]>0 for c in samples),
            "gap_shift_nonzero":sum(c["off_root_white_cp_gap"] is not None and c["main_root_white_cp_gap"] is not None and c["off_root_white_cp_gap"]!=c["main_root_white_cp_gap"] for c in samples),
            "same_requested_depth_different_reported_rank1_nodes":sum(c["same_requested_depth_not_equal_nodes"] for c in samples),
            "median_MAIN_vs_OFF_rank1_node_ratio":statistics.median(c["MAIN_vs_OFF_rank1_node_ratio"] for c in samples if c["MAIN_vs_OFF_rank1_node_ratio"] is not None)
        }
    discovered={}
    for rnd in ("12.1","96.1","95.1"):
        cs=[c for c in cases if c["round"]==rnd and c["cold_repeat"]==1]
        assert len(cs)==3
        discovered[rnd]=[{
            "depth":c["requested_equal_depth"],
            "score_gap_OFF_cp":c["off_root_white_cp_gap"],
            "score_gap_MAIN_cp":c["main_root_white_cp_gap"],
            "strict":c["strict_nonzero_cp_sign_inversion"],
            "root_choice_relabel":c["bestmove_label_changed"],
            "cutoffs_blocked":c["observed_native_MAIN_cutoffs_blocked"],
            "nodes_OFF":c["rank1_reported_nodes_off"],
            "nodes_MAIN":c["rank1_reported_nodes_main"]
        } for c in cs]
    summary={
      "schema":"c3x-014-internal-p3-equal-requested-depth-budget-response-surface-v1",
      "one_formal_research_stage":"C3X 0.14",
      "P3_is_internal_not_formal_stage":True,
      "scientific_status":"POST_P2_DISCOVERY_DIAGNOSTIC__SAME_SOURCE_GROUPS__NO_MEDIATION_IDENTIFICATION",
      "p2_original_panel_sha256":PARENT_SHA,
      "engine_versions":{"clean_binary_sha256":h(a.clean),"instrumented_binary_sha256":h(a.ep9),
                        "upstream_commit":"68e1e9b3811e16cad014b590d7443b9063b3eb52"},
      "source_game_groups":16,"cold_repeats":2,"all_cells":len(cases),
      "sham_exact_every_cell":equal_all,
      "two_cold_runs_equal_group_depth_out_of_48":paired,
      "fixed_requested_depths":list(DEPTHS),
      "results_at_first_cold_by_depth":perdepth,
      "known_discovery_case_depth_responses":discovered,
      "samples":cases,
      "P1_holdout_opened":False,
      "stronger_claims_blocked":[
        "same requested depth does not identify equal achieved search work",
        "equal node cap does not identify same completed depth",
        "truncation of iterative deepening is not interchangeable with fresh fixed-depth search",
        "this run is not independent from P2 game selection or P2 discovery",
        "search-path effect is not chess semantic strategy mediation",
        "regression score cp within Stockfish16 does not establish true chess minimax",
        "no blind human usefulness experiment performed"]
    }
    out=Path(a.out);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(summary,indent=2,ensure_ascii=False)+"\n")
    print("P3_IN_STAGE_DEPTH_COURT",json.dumps({
        "sham":equal_all,"n":len(cases),"group_depth_repeat_equal":paired,
        "bydepth":perdepth,"known":discovered}),flush=True)
    if not equal_all or paired!=48:
        raise SystemExit("P3_FAIL_CLOSED_SHAM_OR_RESTART_INSTABILITY")
if __name__=="__main__":main()

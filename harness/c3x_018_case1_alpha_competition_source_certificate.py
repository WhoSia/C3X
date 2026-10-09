#!/usr/bin/env python3
"""Audited alpha-screening certificate for original C3X018 case1.

Combines SOURCE-NATIVE root trial event stream with the cold same-node
game-cycle counterfactual. Does NOT extrapolate to all later search calls.
"""
import argparse,hashlib,json
from pathlib import Path

EXPECTED_ROOT_TRACE_SHA="7967c17bd6abb4e52ba65316906c31e5a0182f68d19c3fb0144beb193fded4d8"
EXPECTED_GATED_SHA="c5b5d2d4f4a4d776673b4084cc768eab6a6b0a14e04a9354dcd1ee82b3a8f585"

def need(condition,marker):
    if not condition:raise RuntimeError("C3X018_ROOT_ALPHA_"+marker)
def digest(data):return hashlib.sha256(data).hexdigest()

def main():
 p=argparse.ArgumentParser()
 for field in ("root-native","gate-native","out"):p.add_argument("--"+field,required=True)
 a=p.parse_args()
 raw1=Path(a.root_native).read_bytes();raw2=Path(a.gate_native).read_bytes()
 need(digest(raw1)==EXPECTED_ROOT_TRACE_SHA,"ROOT_GENEALOGY_SHA")
 need(digest(raw2)==EXPECTED_GATED_SHA,"COUNTERFACTUAL_SHA")
 root=json.loads(raw1);gate=json.loads(raw2)
 need(root["case_id"]==gate["case_id"]==1,"CASE_ID")
 report={"schema":"c3x018-case1-alpha-competition-source-certificate-v1",
    "source_root_genealogy_sha256":digest(raw1),
    "native_draw_gate_sha256":digest(raw2),
    "scope":"First root call, first iterative-deepening depth, 22nd candidate only",
    "modes":{}}
 for mode in ("O","F"):
  vals={}
  for form in ("FEN6","ORIGINAL_PGN"):
   events=root["arms"][mode][form]["root_events"]
   call=[x for x in events if x.get("root_call")==1]
   enter=next(x for x in call if x["kind"]=="window_enter")
   prior=next(x for x in call if x["kind"]=="candidate" and x["index"]==14)
   loser=next(x for x in call if x["kind"]=="candidate" and x["index"]==22)
   sort=next(x for x in call if x["kind"]=="after_sort")
   must={"first_depth":1,"root_call":1,"candidate_index":22,"winning_prior_index":14}
   need(enter["depth"]==prior["depth"]==loser["depth"]==sort["depth"]==1,
        "ROOT_DEPTH")
   need(prior["move"]==1371 and prior["after"]==prior["child_return"]==137,
        "PRIOR_ROOT_COMPETITOR")
   need(loser["move"]==2313 and loser["alpha"]==137 and loser["beta"]==32001,
        "TARGET_ROOT_SEARCH_WINDOW")
   need(loser["after"]==-32001,"TARGET_FAIL_LOW_STORED_SCORE")
   need(sort["first_move"]==1371 and sort["first_score"]==137,"DEPTH1_WINNER")
   need(prior["seq"]<loser["seq"]<sort["seq"],"CAUSAL_TIME_ORDER")
   row=gate["arms"][mode][("HISTORY_BASE" if form=="ORIGINAL_PGN" else "FEN6_BASE")]
   need(row["first_root_event"]==loser,"SOURCE_EXACT_EVENT_EQUALITY")
   vals[form]={"window_enter":enter,"prior_competitor":prior,
               "target_candidate":loser,"after_sort":sort}
  base=gate["arms"][mode]["HISTORY_BASE"]
  treated=gate["arms"][mode]["HISTORY_G"]
  noop=gate["arms"][mode]["HISTORY_D"]
  fen=gate["arms"][mode]["FEN6_BASE"]
  need(base["first_root_candidate_return"] in (-1,1) and
       treated["first_root_candidate_return"]==fen["first_root_candidate_return"]==68,
       "LOCAL_ROOT_CHILD_RESTORATION")
  need(noop["first_root_candidate_return"]==base["first_root_candidate_return"],
       "IRRELEVANT_DRAW_CONTROL")
  need(treated["gate_contact_count"]==1 and noop["gate_contact_count"]==0,
       "POSITIVE_SINGLE_DRAW_BRANCH_SOURCE")
  need(base["UCI"]==treated["UCI"],"FULL_OUTPUT_SAME_AFTER_EXACT_LOCAL_RESTORATION")
  need(base["first_root_event"]["alpha"]==treated["first_root_event"]["alpha"]==137,
       "UNCHANGED_ROOT_ALPHA_G")
  need(base["first_root_event"]["after"]==treated["first_root_event"]["after"]==-32001,
       "UNCHANGED_CANDIDATE_RM_STORED_SCORE")
  need(treated["first_root_candidate_return"] < treated["first_root_event"]["alpha"],
       "RESTORED_CHILD_STILL_BELOW_ALPHA")
  report["modes"][mode]={
    "first_root_call_event_certificates":vals,
    "prior_competitor_native_move":1371,
    "prior_competitor_score":137,
    "target_native_move":2313,
    "source_child_before":base["first_root_candidate_return"],
    "source_child_after_exact_branch_suppression":treated["first_root_candidate_return"],
    "alpha_at_candidate":137,
    "margin_below_alpha_after_restoration":137-68,
    "stored_root_candidate_score_remains":-32001,
    "sorted_depth1_winner_move_native":1371,
    "source_exact_G_hits":1,
    "D_no_contact":True,
    "G_changed_final_six_field_UCI":False}
 report["certified"]="LOCAL_REPETITION_RETURN_CAUSALLY_RESTORED_BUT_ALPHA_SCREENED_FROM_ROOT_COMPETITION_AT_DEPTH1"
 report["limits"]=[
   "Only the first depth1 root-call loser #22 is certified alpha-screened; no claim about later aspiration calls",
   "A PVS fail-low candidate stored -VALUE_INFINITE is a source-level score-label semantics, not a real -32001 positional evaluation",
   "First candidate threshold change alone does not prove no downstream history effects; case1 full final UCI history/FEN difference remains unresolved",
   "Root call ID is within search arm and cannot identify counterfactual causal equivalence after path divergence",
   "No unique TT score writer-to-final bestmove mediation claim"]
 o=Path(a.out);o.parent.mkdir(parents=True,exist_ok=True)
 o.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
 print("C3X018_CASE1_NATIVE_ALPHA_SCREEN_CERTIFICATE_PASS")
if __name__=="__main__":main()

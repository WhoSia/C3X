#!/usr/bin/env python3
"""C3X018 fixed five-source W2/V/WV joint response, no outcome-based exclusions.

Preselected cases and target key/slot/epoch from historical source data.
Extends earlier 2/5 interaction court to all 5 previously writer-sensitive
source roots. Does not infer unique natural TT causal mediation.
"""
import argparse,hashlib,json
from pathlib import Path
from c3x_018_native_TT_lineage_factorial_6_8 import play,need
from c3x_018_depth_transport_five_source_worlds import TARGETS,WORLDS

def main():
    p=argparse.ArgumentParser()
    for k in ("cohort","prior","engine","out"):p.add_argument("--"+k,required=True)
    a=p.parse_args()
    cohort=json.loads(Path(a.cohort).read_text())
    prior=json.loads(Path(a.prior).read_text())
    result={"schema":"c3x018-five-frozen-source-world-W2-V-WV-competing-mechanism-v1",
      "selected_cases":list(WORLDS),
      "selection":"Historical W2 writer-responsive targets, fixed before joint five-world expansion",
      "prior_sha256":hashlib.sha256(Path(a.prior).read_bytes()).hexdigest(),
      "cases":[]}
    for case_id in WORLDS:
        world=cohort["selected"][case_id-1]
        need(world["id"]==case_id,f"SOURCE_CASE_{case_id}")
        original=prior["worlds"][case_id-1]["cells"]
        arms={}
        for arm in ("O","F","Z"):
            a1=play(a.engine,world,arm,"OBS")
            a2=play(a.engine,world,arm,"OBS")
            need(a1==a2,f"SHAM_REPLAY_{case_id}_{arm}")
            need(a1["UCI"]==original[arm]["UCI"],f"P4_DRIFT_{case_id}_{arm}")
            arms[arm]={"UCI":a1["UCI"],"writer_blocks":0,"V_reader_blocks":0}
        need(arms["O"]["UCI"]==arms["Z"]["UCI"],f"ZERO_CONTACT_OZ_{case_id}")
        for mode,budget in (("W",2),("V",None),("WV",2)):
            a1=play(a.engine,world,"F",mode,TARGETS[case_id],writer_budget=budget)
            a2=play(a.engine,world,"F",mode,TARGETS[case_id],writer_budget=budget)
            need(a1==a2,f"TREATMENT_REPLAY_{case_id}_{mode}")
            writes=a1["lineage_summary"]["writer_block"]
            reads=a1["lineage_summary"]["reader_block"]
            need(writes== (2 if mode in ("W","WV") else 0),
                 f"WRITE_DOSE_{case_id}_{mode}")
            need(all(z["site"]=="tt_value_eval_override" for z in a1["blocks"] if z["kind"]=="reader_block"),
                 f"TT_V_CONSUMER_SITE_{case_id}_{mode}")
            arms[mode]={"UCI":a1["UCI"],"writer_blocks":writes,
                         "V_reader_blocks":reads,
                         "operator_contacts":a1["blocks"]}
            print("C3X018_WV_FIVE_SOURCE",case_id,mode,writes,reads,
                  a1["UCI"]["bestmove"],a1["UCI"]["score_value"],flush=True)
        decoy=play(a.engine,world,"F","WV",
              {"key64":18446744073709551615,"slot":0,"epoch":1},writer_budget=2)
        need(decoy["UCI"]==arms["F"]["UCI"] and
             decoy["lineage_summary"]["writer_block"]==0 and
             decoy["lineage_summary"]["reader_block"]==0,
             f"JOINT_DECOY_CONTACT_{case_id}")
        F=arms["F"]["UCI"]["bestmove"]
        tab={mode:arms[mode]["UCI"]["bestmove"]!=F for mode in ("W","V","WV")}
        result["cases"].append({
          "id":case_id,"fixed_target":TARGETS[case_id],
          "arms":arms,"outcome_change_truth_table":tab,
          "joint_reader_contact":arms["WV"]["V_reader_blocks"],
          "joint_sham_exact":True,
          "W_and_V_full_core_equal":arms["W"]["UCI"]==arms["V"]["UCI"],
          "WV_matches_F_full_core":arms["WV"]["UCI"]==arms["F"]["UCI"]
        })
    result["summary"]={
      "n":len(WORLDS),
      "W_choice_changes":sum(c["outcome_change_truth_table"]["W"] for c in result["cases"]),
      "V_choice_changes":sum(c["outcome_change_truth_table"]["V"] for c in result["cases"]),
      "WV_choice_changes":sum(c["outcome_change_truth_table"]["WV"] for c in result["cases"]),
      "WV_actual_V_reader_contacts":sum(c["joint_reader_contact"] for c in result["cases"])}
    result["limits"]=[
      "Five earlier writer-sensitive cases, not a representative random sample",
      "Both W/V use a fixed full64 physical TT writer-shadow witness; after W path, identical numeric epochs may not identify natural equivalent actors",
      "A W2/V/WV truth table is a property of named source interventions at fixed depth, not logical circuitry in Stockfish",
      "R/M/E and other TT interactions remain potential causal pathways",
      "One exact external cohort still absent; no uniquely natural mediator identified",
      "Original Stockfish16 depth12, 1 thread, hash16MB, NNUE off, standalone FEN"]
    Path(a.out).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("C3X018_FIVE_SOURCE_WV_INTERACTION_NATIVE_PASS",
          json.dumps(result["summary"],sort_keys=True),flush=True)
if __name__=="__main__":main()

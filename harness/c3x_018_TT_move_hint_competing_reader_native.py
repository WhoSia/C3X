#!/usr/bin/env python3
"""C3X 0.18 targeted TT move hint versus early cutoff competing mechanism.

Frozen five source roots and full64 key/slot/write epoch targets. M mutes TT
move hint before move ordering and related TT-move heuristics, leaving TT
score/bound untouched. R mutes only early cutoff, W1/W2 block source writes.
"""
import argparse,hashlib,json
from pathlib import Path
from c3x_018_native_TT_lineage_factorial_6_8 import play,need
from c3x_018_depth_transport_five_source_worlds import WORLDS,TARGETS
def main():
    p=argparse.ArgumentParser()
    for k in ("cohort","prior","engine","out"):p.add_argument("--"+k,required=True)
    a=p.parse_args()
    cohort=json.loads(Path(a.cohort).read_text())
    prior=json.loads(Path(a.prior).read_text())
    output={"schema":"c3x018-TT-move-hint-versus-early-cutoff-competing-route-v1",
       "target_source":"PREVIOUSLY SEALED 5 WORLD SOURCE TARGETS",
       "world_ids":list(WORLDS),
       "prior_sha256":hashlib.sha256(Path(a.prior).read_bytes()).hexdigest(),
       "cases":[]}
    for case_id in WORLDS:
        world=cohort["selected"][case_id-1]
        need(world["id"]==case_id,"FROZEN_ID")
        controls={}
        for root_mode in ("O","F","Z"):
            run=play(a.engine,world,root_mode,"OBS")
            need(run["UCI"]==prior["worlds"][case_id-1]["cells"][root_mode]["UCI"],
                 f"PASSIVE_NONINTERFERENCE_{case_id}_{root_mode}")
            controls[root_mode]=run["UCI"]
        need(controls["O"]==controls["Z"],f"NO_CONTACT_{case_id}")
        row={"id":case_id,"source_target":TARGETS[case_id],
             "controls":controls,"treatments":{}}
        decoy={"key64":18446744073709551615,"slot":0,"epoch":1}
        sham=play(a.engine,world,"F","M",decoy)
        need(sham["lineage_summary"]["reader_block"]==0 and
             sham["UCI"]==controls["F"],f"M_DECOY_FAILED_{case_id}")
        row["M_decoy_noncontact_exact"]=True
        for mode,budget in (("R",None),("M",None),("W1",1),("W2",2)):
            real_mode="W" if mode.startswith("W") else mode
            a1=play(a.engine,world,"F",real_mode,TARGETS[case_id],writer_budget=budget)
            a2=play(a.engine,world,"F",real_mode,TARGETS[case_id],writer_budget=budget)
            need(a1==a2,f"NONDETERMINISTIC_{case_id}_{mode}")
            hist=a1["lineage_summary"]
            blocks=a1["blocks"]
            if mode=="M":
                need(all(e["site"]=="tt_move" for e in blocks),
                     f"OTHER_TT_CONSUMER_MUTED_{case_id}")
            row["treatments"][mode]={
               "UCI":a1["UCI"],
               "writer_block":hist["writer_block"],
               "reader_block":hist["reader_block"],
               "block_sites":[e["site"] for e in blocks],
               "changes_bestmove_vs_F":a1["UCI"]["bestmove"]!=controls["F"]["bestmove"],
               "changes_full_core_vs_F":a1["UCI"]!=controls["F"]}
            print("C3X018_TT_COMPETING_READER",case_id,mode,
                  hist["writer_block"],hist["reader_block"],
                  a1["UCI"]["bestmove"],a1["UCI"]["score_value"],flush=True)
        output["cases"].append(row)
    output["summary"]={
      "total_source_roots":len(WORLDS),
      "M_choice_changes":sum(c["treatments"]["M"]["changes_bestmove_vs_F"] for c in output["cases"]),
      "R_choice_changes":sum(c["treatments"]["R"]["changes_bestmove_vs_F"] for c in output["cases"]),
      "W1_choice_changes":sum(c["treatments"]["W1"]["changes_bestmove_vs_F"] for c in output["cases"]),
      "W2_choice_changes":sum(c["treatments"]["W2"]["changes_bestmove_vs_F"] for c in output["cases"])}
    output["limits"]=[
      "M suppresses ttMove at main/qsearch after probe; it influences multiple TT-move-dependent heuristics and ordering, not solely MovePicker",
      "M keeps TT score and early-cutoff logic untouched; R only mutes selected early-cutoff use",
      "Even M that changes root outcome is not proof of sole natural TT mediator",
      "TT targets previously chosen from treated F; no independent new sample",
      "Single-thread SF16 depth12 Hash16 NNUE off FEN standalone; root order unchanged in reader arms",
      "All five worlds retained and impossible-key move-reader decoy checks enforced"]
    Path(a.out).write_text(json.dumps(output,indent=2,sort_keys=True)+"\n")
    print("C3X018_TT_COMPETING_READER_ROUTE_NATIVE_PASS",flush=True)
if __name__=="__main__":main()

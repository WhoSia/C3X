#!/usr/bin/env python3
"""Two-event TT writer reinstallation court, #6/#8, frozen source.

S2 permits the second targeted source-eligible TTEntry::save() after W-blocking
the first; no external payload or artificial TT slot written. S3 is an
unreachable rescue negative control under budget2.
"""
import argparse,hashlib,json
from pathlib import Path
from c3x_018_native_TT_lineage_factorial_6_8 import play,need
from c3x_018_TT_writer_dose_6_8 import TARGETS

def main():
    p=argparse.ArgumentParser()
    for key in ("cohort","prior","engine","out"):p.add_argument("--"+key,required=True)
    a=p.parse_args()
    cohort=json.loads(Path(a.cohort).read_text())
    prior=json.loads(Path(a.prior).read_text())
    out={"schema":"c3x018-selective-second-writer-native-reinstatement-v1",
      "prior_sha256":hashlib.sha256(Path(a.prior).read_bytes()).hexdigest(),
      "cases":[]}
    for case_id in (6,8):
        w=cohort["selected"][case_id-1]
        prior_F=prior["worlds"][case_id-1]["cells"]["F"]["UCI"]
        baseline=play(a.engine,w,"F","OBS")
        need(baseline["UCI"]==prior_F,"HISTORICAL_F_DRIFT")
        row={"id":case_id,"target":TARGETS[case_id],"F":baseline["UCI"],"arms":{}}
        for name,mode,budget,rescue in (
            ("W1","W",1,None),("W2","W",2,None),
            ("S1","S",2,1),("S2","S",2,2),("S3_decoy","S",2,3)):
            aa=play(a.engine,w,"F",mode,TARGETS[case_id],writer_budget=budget,rescue_attempt=rescue)
            bb=play(a.engine,w,"F",mode,TARGETS[case_id],writer_budget=budget,rescue_attempt=rescue)
            need(aa==bb,f"COLD_REPEAT_{case_id}_{name}")
            s=aa["lineage_summary"]
            row["arms"][name]={
                "UCI":aa["UCI"],"writer_blocks":s["writer_block"],
                "writer_rescues":s["writer_rescue"],
                "rescued_events":aa["rescues"],
                "matches_F_core":aa["UCI"]==baseline["UCI"]
            }
            print("C3X018_SOURCE_REINSTATEMENT",case_id,name,
                  "W",s["writer_block"],"rescue",s["writer_rescue"],
                  "move",aa["UCI"]["bestmove"],flush=True)
        need(row["arms"]["W1"]["writer_blocks"]==1,"W1_DOSE")
        need(row["arms"]["W2"]["writer_blocks"]==2,"W2_DOSE")
        need(row["arms"]["S2"]["writer_blocks"]==1 and
             row["arms"]["S2"]["writer_rescues"]==1,"S2_NOT_REALIZED")
        need(row["arms"]["S3_decoy"]["writer_rescues"]==0 and
             row["arms"]["S3_decoy"]["UCI"]==row["arms"]["W2"]["UCI"],
             "OUT_OF_REACH_RESCUE_CHANGED_OUTPUT")
        row["second_writer_reinstatement_changes_W2"]={
            "bestmove":row["arms"]["S2"]["UCI"]["bestmove"]!=row["arms"]["W2"]["UCI"]["bestmove"],
            "full_core":row["arms"]["S2"]["UCI"]!=row["arms"]["W2"]["UCI"]}
        row["S2_matches_W1_exact_core"]=row["arms"]["S2"]["UCI"]==row["arms"]["W1"]["UCI"]
        out["cases"].append(row)
    out["limitations"]=[
      "Local source-opportunity restoration after first blocked writer, not a borrowed or synthetic TT value",
      "S2 may make future attempt identities different; record contact count and release event",
      "S2/W1 identical output does not prove unique natural mediation",
      "No other TT uses suppressed; source original finite depth and frozen FEN only",
      "Two prior outcome-selected root-flip worlds, TT targets discovered from treated F observation",
      "Physical writer and root-call source fingerprint equality must be independently checked"]
    Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("C3X018_SECOND_WRITER_REINSTATEMENT_NATIVE_PASS",flush=True)
if __name__=="__main__":main()

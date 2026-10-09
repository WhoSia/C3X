#!/usr/bin/env python3
"""C3X018 surgical comparison of TT cached eval (E) and value override (V).

Five frozen source worlds #1,#2,#5,#6,#8, full64 writer shadow targets
fixed from prior runs. Includes TT cutoff-only R, whole writer W2, impossible
key decoys, native cold repeats and original P4 O/F/Z exact core.
"""
import argparse,json,hashlib
from pathlib import Path
from c3x_018_native_TT_lineage_factorial_6_8 import play,need
from c3x_018_depth_transport_five_source_worlds import WORLDS,TARGETS

def main():
    p=argparse.ArgumentParser()
    for k in ("cohort","prior","engine","out"):p.add_argument("--"+k,required=True)
    a=p.parse_args()
    cohort=json.loads(Path(a.cohort).read_text())
    prior=json.loads(Path(a.prior).read_text())
    result={"schema":"c3x018-five-source-TT-cache-eval-vs-bound-eval-override-v1",
            "prior_sha256":hashlib.sha256(Path(a.prior).read_bytes()).hexdigest(),
            "world_ids":list(WORLDS),"cases":[]}
    for case_id in WORLDS:
        world=cohort["selected"][case_id-1]
        need(world["id"]==case_id,"COHORT_ID")
        controls={}
        for arm in ("O","F","Z"):
            q=play(a.engine,world,arm,"OBS")
            need(q["UCI"]==prior["worlds"][case_id-1]["cells"][arm]["UCI"],
                 f"HISTORICAL_CORE_{case_id}_{arm}")
            controls[arm]=q["UCI"]
        need(controls["O"]==controls["Z"],f"OZ_CORE_{case_id}")
        row={"id":case_id,"target":TARGETS[case_id],
             "controls":controls,"treatments":{}}
        for op,budget in (("E",None),("V",None),("R",None),("W",2)):
            q=play(a.engine,world,"F",op,TARGETS[case_id],writer_budget=budget)
            qq=play(a.engine,world,"F",op,TARGETS[case_id],writer_budget=budget)
            need(q==qq,f"COLD_REPLAY_{case_id}_{op}")
            hits=q["lineage_summary"]
            if op in ("E","V"):
                expected={"E":"tt_cached_eval","V":"tt_value_eval_override"}[op]
                need(all(b["site"]==expected for b in q["blocks"]),
                     f"UNEXPECTED_BRANCH_{case_id}_{op}")
            row["treatments"][op]={
               "UCI":q["UCI"],"writer_blocks":hits["writer_block"],
               "reader_blocks":hits["reader_block"],
               "sites":[b["site"] for b in q["blocks"]],
               "choice_changed":q["UCI"]["bestmove"]!=controls["F"]["bestmove"],
               "full_core_changed":q["UCI"]!=controls["F"]}
            print("C3X018_TT_EVAL_CONSUMER",case_id,op,
                  "R",hits["reader_block"],"W",hits["writer_block"],
                  q["UCI"]["bestmove"],q["UCI"]["score_value"],flush=True)
        decoy={"key64":18446744073709551615,"slot":0,"epoch":1}
        for op in ("E","V"):
            sham=play(a.engine,world,"F",op,decoy)
            need(sham["UCI"]==controls["F"] and
                 sham["lineage_summary"]["reader_block"]==0,
                 f"OPERATOR_DECOY_{case_id}_{op}")
        row["E_V_decoy_no_contact_exact"]=True
        result["cases"].append(row)
    result["summary"]={
       "total_worlds":len(WORLDS),
       "E_bestmove_changed":sum(c["treatments"]["E"]["choice_changed"] for c in result["cases"]),
       "V_bestmove_changed":sum(c["treatments"]["V"]["choice_changed"] for c in result["cases"]),
       "R_bestmove_changed":sum(c["treatments"]["R"]["choice_changed"] for c in result["cases"]),
       "W2_bestmove_changed":sum(c["treatments"]["W"]["choice_changed"] for c in result["cases"])}
    result["limitations"]=[
       "E accesses source-native evaluate() instead of matching TT eval; may generate identical score",
       "V skips TT value as evaluation improvement but leaves TT direct cutoff intact",
       "Only main and qsearch branches instrumented, not exhaustive all possible TT uses",
       "TT shadow physical writer key/slot/epoch target from prior treated F observations",
       "Five source roots selected because prior TT writer effects; no independent statistical sample",
       "Stockfish16 depth12 Hash16 single-thread NNUE off standalone FEN",
       "Neither E nor V alone is an exhaustive intervention on a natural writer-consumer path"]
    Path(a.out).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("C3X018_EVAL_CONSUMER_COMPETING_NATIVE_PASS",flush=True)
if __name__=="__main__":main()

#!/usr/bin/env python3
"""C3X018 nested physical writer/TT value-eval gate test, cases 2 and 5.

Compare W2, V and WV to observe contact-realizability and epistasis.
The same final tuple does not establish natural mediation. Retain null gates.
"""
import argparse,hashlib,json
from pathlib import Path
from c3x_018_native_TT_lineage_factorial_6_8 import play,need
from c3x_018_depth_transport_five_source_worlds import TARGETS

def main():
    p=argparse.ArgumentParser()
    for k in ("cohort","prior","engine","out"):p.add_argument("--"+k,required=True)
    a=p.parse_args()
    cohort=json.loads(Path(a.cohort).read_text())
    prior=json.loads(Path(a.prior).read_text())
    results={"schema":"c3x018-source-W2-V-nested-physical-writer-eval-reader-court-v1",
      "prior_sha256":hashlib.sha256(Path(a.prior).read_bytes()).hexdigest(),
      "cases":[]}
    for case_id in (2,5):
        world=cohort["selected"][case_id-1]
        c={"id":case_id,"target":TARGETS[case_id],"arms":{}}
        for arm in ("O","F","Z"):
            out=play(a.engine,world,arm,"OBS")
            need(out["UCI"]==prior["worlds"][case_id-1]["cells"][arm]["UCI"],
                 f"SOURCE_ORIGINAL_DRIFT_{case_id}_{arm}")
            c["arms"][arm]={"UCI":out["UCI"],"writer_blocks":0,"V_reader_blocks":0}
        need(c["arms"]["O"]["UCI"]==c["arms"]["Z"]["UCI"],"ZERO_CONTACT")
        for mode,limit in (("W",2),("V",None),("WV",2)):
            x=play(a.engine,world,"F",mode,TARGETS[case_id],writer_budget=limit)
            y=play(a.engine,world,"F",mode,TARGETS[case_id],writer_budget=limit)
            need(x==y,f"NOT_COLD_REPEATED_{case_id}_{mode}")
            write=x["lineage_summary"]["writer_block"]
            read=x["lineage_summary"]["reader_block"]
            relevant=[e for e in x["blocks"] if e["site"]=="tt_value_eval_override"]
            need(read==len(relevant),f"NON_VALUE_GATE_{case_id}_{mode}")
            c["arms"][mode]={"UCI":x["UCI"],
               "writer_blocks":write,"V_reader_blocks":read,
               "contact_events":x["blocks"],
               "relative_to_F_bestmove_changed":x["UCI"]["bestmove"]!=c["arms"]["F"]["UCI"]["bestmove"]}
            print("C3X018_WRITER_VALUE_INTERACTION",case_id,mode,
                  "writer",write,"reader",read,"bestmove",x["UCI"]["bestmove"],flush=True)
        need(c["arms"]["W"]["writer_blocks"]==2 and
             c["arms"]["V"]["V_reader_blocks"]==1,
             f"FIRST_ORDER_CONTACT_{case_id}")
        need(c["arms"]["W"]["UCI"]==c["arms"]["V"]["UCI"],
             f"PRIOR_W2_V_OUTPUT_EQUIVALENCE_{case_id}")
        decoy=play(a.engine,world,"F","WV",
             {"key64":18446744073709551615,"slot":0,"epoch":1},writer_budget=2)
        need(decoy["UCI"]==c["arms"]["F"]["UCI"] and
             decoy["lineage_summary"]["writer_block"]==0 and
             decoy["lineage_summary"]["reader_block"]==0,
             f"JOINT_DECOY_CONTACT_{case_id}")
        c["WV_vs_W2_core_equal"]=c["arms"]["WV"]["UCI"]==c["arms"]["W"]["UCI"]
        c["joint_decoy_no_contact_exact"]=True
        results["cases"].append(c)
    results["limits"]=[
      "W2 and V independently reproduce one final tuple but their precise root and TT call graphs may differ",
      "WV shows whether a V operator can fire in a modified W2 search world; not proof of natural mediation",
      "W suppresses entire save including move16; V only bound-value-as-eval correction",
      "Fixed key/slot/epoch can refer to different downstream events after W blockade",
      "Only two selected source worlds, SF16 depth12 threads1 Hash16 NNUE off"]
    Path(a.out).write_text(json.dumps(results,indent=2,sort_keys=True)+"\n")
    print("C3X018_W2_V_JOINT_SOURCE_NATIVE_PASS",flush=True)
if __name__=="__main__":main()

#!/usr/bin/env python3
"""C3X018 source-native TT save-payload to V-reader exact witness court.

Cases 2 and 5 previously showed V result equals W2; now require that the
V-consumed raw TTEntry payload is byte-field-identical to its last accepted
source writer's shadow snapshot, with real full64 key and writer ID.
"""
import argparse,hashlib,json
from pathlib import Path
from c3x_018_native_TT_lineage_factorial_6_8 import play,need
from c3x_018_depth_transport_five_source_worlds import TARGETS
FIELDS=("raw_value","raw_depth","raw_bound","raw_eval","raw_move")

def verify(x):
    stream=x["payload_witnesses"]
    writers={}
    matched=[]
    for position,e in enumerate(stream):
        key=(e["key64"],e["slot"],e["epoch"],e["writer_serial"])
        if e["kind"]=="writer":
            need(e["writer_serial"]>0,"BAD_WRITER_SERIAL")
            need(key not in writers,"REPEATED_WRITER_TICKET")
            writers[key]=(position,e)
        elif e["kind"]=="reader":
            need(e["known"]==1 and e["matched"]==1,"UNMATCHED_PHYSICAL_PAYLOAD")
            need(e["writer_serial"]>0 and key in writers,"NO_SOURCE_WRITER_FOR_READER")
            i,w=writers[key]
            need(i<position,"NON_CHRONOLOGICAL_WRITER")
            need(all(e[f]==w[f] for f in FIELDS),"PAYLOAD_FIELDS_CHANGED_AFTER_SAVE")
            need(e["key64"]==e["writer_key64"],"WRITER_KEY64_ALIAS")
            matched.append({"writer":w,"reader":e,"writer_stream_pos":i,"reader_stream_pos":position})
        else: raise RuntimeError("UNKNOWN_WITNESS_KIND_"+str(e["kind"]))
    return {"writer_count":len(writers),"matched_consumptions":matched,
            "all_reader_payloads_verified":True}

def main():
    p=argparse.ArgumentParser()
    for key in ("cohort","prior","engine","out"):p.add_argument("--"+key,required=True)
    a=p.parse_args()
    cohort=json.loads(Path(a.cohort).read_text())
    prior=json.loads(Path(a.prior).read_text())
    result={"schema":"c3x018-actual-TT-payload-writer-to-value-reader-witness-cases2-5-v1",
       "prior_sha256":hashlib.sha256(Path(a.prior).read_bytes()).hexdigest(),
       "cases":[]}
    for case_id in (2,5):
        world=cohort["selected"][case_id-1]
        need(world["id"]==case_id,"HISTORICAL_ID")
        row={"id":case_id,"target":TARGETS[case_id],"arms":{}}
        for name,root,mode,target,dose in (
              ("O","O","OBS",None,None),("F","F","OBS",TARGETS[case_id],None),
              ("Z","Z","OBS",None,None),("V","F","V",TARGETS[case_id],None),
              ("W2","F","W",TARGETS[case_id],2)):
            x=play(a.engine,world,root,mode,target,writer_budget=dose)
            y=play(a.engine,world,root,mode,target,writer_budget=dose)
            need(x==y,f"COLD_REPEAT_{case_id}_{name}")
            if name in ("O","F","Z"):
                need(x["UCI"]==prior["worlds"][case_id-1]["cells"][name]["UCI"],
                     f"ORIGINAL_P4_DRIFT_{case_id}_{name}")
            checked=verify(x)
            row["arms"][name]={"UCI":x["UCI"],"value_witness":checked,
                "reader_blocks":x["lineage_summary"]["reader_block"],
                "writer_blocks":x["lineage_summary"]["writer_block"]}
            print("C3X018_ACTUAL_VALUE_WITNESS",case_id,name,
                  checked["writer_count"],len(checked["matched_consumptions"]),
                  x["UCI"]["bestmove"],flush=True)
        need(row["arms"]["O"]["UCI"]==row["arms"]["Z"]["UCI"],"O_Z_SHAM")
        need(row["arms"]["V"]["reader_blocks"]==1,"V_BLOCK_NOT_FIRED")
        need(len(row["arms"]["V"]["value_witness"]["matched_consumptions"])>=1,
             "V_BOUND_EVAL_VALUE_NOT_FROM_VERIFIED_WRITER")
        need(row["arms"]["V"]["UCI"]==row["arms"]["W2"]["UCI"],
             "V_W2_ORIGINAL_OUTPUT_EQUIVALENCE_LOST")
        row["verified_source_value_in_V"]=True
        result["cases"].append(row)
    result["limits"]=[
      "Source last-payload-writer snapshot equal to physical entry read at V consumption, not sole causal mediator",
      "TT raw value and evaluated ttValue can differ due to mate/ply/rule50 normalization",
      "Shadow full64 key counteracts SF16 key16 aliases only for observed writer; races ruled out by Threads1",
      "Writer_serial valid within a cold process only; not cross-arm event identity",
      "V changes one existing evaluation-override consumption, not all TT uses",
      "Same original two selected source roots; independent new population remains separate court"]
    Path(a.out).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("C3X018_VALUE_WITNESS_NATIVE_COURT_PASS",flush=True)
if __name__=="__main__":main()

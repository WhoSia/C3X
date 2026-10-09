#!/usr/bin/env python3
"""Case11 adaptive exact source-root-call late physical TT reader singleton court.

All five root calls 9-13 predeclared after grouped age64 result inspection;
no target re-selection, source and prior raw JSON immutable SHA checked.
"""
import argparse,hashlib,json
from pathlib import Path
from c3x_018_native_TT_lineage_factorial_6_8 import play,need
from c3x_018_independent16_TT_value_transport_native import canonical_engine_world,verified_reader_lineage
from c3x_018_chess_clock_factorial_original_history_native import game_clocks

SOURCE_SHA="51366a480fe2631005dbded7992e870443ef6dd2dfd785fd10952d6eeff5e7cd"
PREVIOUS_EXACT_SHA="b035c8d184d4c3c474d8592793af442f00fb135276426db1e78d447999609952"
PHYSICAL={"key64":16448589199907615799,"slot":0,"epoch":2}
CALLS=(9,10,11,12,13)

def repeated(engine,world,clock,call):
    opts={"C3X018_FILTER_MIN_WRITE_AGE":64,
          "C3X018_FILTER_ROOT_CALL":call}
    args={"fen_clocks":clock,"tt_reader_filters":opts}
    x=play(engine,world,"F","V",PHYSICAL,**args)
    y=play(engine,world,"F","V",PHYSICAL,**args)
    need(x==y,"COLD_SINGLETON_CALL_"+str(call))
    proof=verified_reader_lineage(x)
    blocks=[b for b in x["blocks"] if b["kind"]=="reader_block"]
    need(len(blocks)==x["lineage_summary"]["reader_block"],"READ_BLOCK_EVENT_MISMATCH")
    need(all(b["root_call"]==call for b in blocks),"WRONG_ROOT_CALL_ACTUAL_BLOCK")
    need(not blocks or proof["all_valid"] is True,"UNVERIFIED_PHYSICAL_TT_WRITER")
    return {"call":call,"UCI":x["UCI"],"reader_blocks":len(blocks),
      "blocked_events":blocks,
      "read_value_witnesses":[r for r in x["payload_witnesses"] if r["kind"]=="reader"],
      "all_source_physical_payloads_valid":proof["all_valid"]}

def main():
    p=argparse.ArgumentParser()
    for name in ("source","prior-exact","engine","out"):p.add_argument("--"+name,required=True)
    a=p.parse_args()
    raw=Path(a.source).read_bytes();before=Path(a.prior_exact).read_bytes()
    need(hashlib.sha256(raw).hexdigest()==SOURCE_SHA,"DECEMBER_SOURCE_NOT_FROZEN")
    need(hashlib.sha256(before).hexdigest()==PREVIOUS_EXACT_SHA,"GROUPED_GATE_PRIOR_SHA_NOT_FROZEN")
    prev=json.loads(before)
    need(prev["source_target"]==PHYSICAL if "source_target" in prev else prev["frozen_target"]==PHYSICAL,
         "CASE11_PHYSICAL_TARGET_MISMATCH")
    w,norm=canonical_engine_world(json.loads(raw)["selected"][10])
    half,full=game_clocks(json.loads(raw)["selected"][10])
    clock=(half,full)
    original=play(a.engine,w,"F","OBS",fen_clocks=clock)
    again=play(a.engine,w,"F","OBS",fen_clocks=clock)
    need(original==again,"NATIVE_F_COLD_NONREPRODUCIBLE")
    need(original["UCI"]==prev["arms"]["F"]["UCI"],"F_BASELINE_DRIFT")
    out={"schema":"c3x018-case11-adaptive-late-TT-source-root-call-singletons-v1",
       "source_sha256":SOURCE_SHA,"prior_grouped_native_sha256":PREVIOUS_EXACT_SHA,
       "physical_target":PHYSICAL,"planned_calls":list(CALLS),
       "study_type":"ADAPTIVE_AFTER_DECEMBER_GROUP_OUTCOME",
       "F_UCI":original["UCI"],"arms":{}}
    for call in (*CALLS,8):
        row=repeated(a.engine,w,clock,call)
        row["bestmove_changed"]=row["UCI"]["bestmove"]!=original["UCI"]["bestmove"]
        row["full_UCI_changed"]=row["UCI"]!=original["UCI"]
        out["arms"][str(call)]=row
        print("C3X018_CASE11_OLDER_ROOT_CALL_SINGLETON",call,
              "block",row["reader_blocks"],"bestmove",row["UCI"]["bestmove"],
              "changed",row["bestmove_changed"],flush=True)
    decoy=out["arms"]["8"]
    need(decoy["reader_blocks"]==0 and decoy["UCI"]==original["UCI"],
         "WRONG_ROOT8_SHAM_FAIL")
    singles=[out["arms"][str(c)] for c in CALLS]
    flips=[q["call"] for q in singles if q["reader_blocks"]>0 and q["bestmove_changed"]]
    contacts={str(q["call"]):q["reader_blocks"] for q in singles}
    out["summary"]={
       "all_five_source_root_calls_recorded":len(singles)==5,
       "positive_source_contact_by_call":contacts,
       "singletons_changing_bestmove":flips,
       "S1_SINGLE_LATE_EFFECT":"PASS" if flips else "FAIL",
       "S2_SINGLES_COMPLETE":"PASS",
       "S3_NO_CONTACT":"PASS",
       "S4_SOURCE_WRITER":"PASS" if all(q["all_source_physical_payloads_valid"] is not False for q in singles) else "FAIL"}
    out["limits"]=[
       "All tests adaptive post-outcome on one December original game; no independent replication",
       "Root call numbers only within a cold source search, do not identify causal states after earlier divergence",
       "A failed singleton to change bestmove is not enough to prove it has zero computational effect",
       "Age64 is accepted successful TT writes since last physical writer, not elapsed clock time",
       "If group flips but none of these five singletons does, synergy is a hypothesis, not proven"] 
    path=Path(a.out);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("C3X018_CASE11_OLD_TT_SINGLETON_FINAL",
          json.dumps(out["summary"],sort_keys=True),flush=True)
if __name__=="__main__":main()

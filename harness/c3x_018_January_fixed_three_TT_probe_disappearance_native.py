#!/usr/bin/env python3
"""Adaptive three-case January disappearance microscope at true TT.probe.

Frozen external source and original sixteen root-pair results are hash pinned.
This observer is read-only and selects cases after initial failure.
"""
import argparse,hashlib,json
from pathlib import Path
from c3x_018_native_TT_lineage_factorial_6_8 import play,need
from c3x_018_independent16_TT_value_transport_native import canonical_engine_world
from c3x_018_chess_clock_factorial_original_history_native import game_clocks
from c3x_018_jan16_TT_cross_window_pair_native import mask_filters,RULES

SOURCE_SHA="5b49818e4678c12d0e5e73eba39eff2d50742b070a0ed870cba1d3e94afe0533"
EARLIER_SHA="9d7ff1d8c5e019a5ab5b95441468da0ad49951adc756b8669db7853b82649470"
SITES=((2,"STRICT"),(6,"BROAD"),(16,"STRICT"))

def main():
    p=argparse.ArgumentParser()
    for k in ("source","earlier","engine","out"):p.add_argument("--"+k,required=True)
    a=p.parse_args()
    source=Path(a.source).read_bytes();prior=Path(a.earlier).read_bytes()
    need(hashlib.sha256(source).hexdigest()==SOURCE_SHA,"JANUARY_SOURCE_SHA")
    need(hashlib.sha256(prior).hexdigest()==EARLIER_SHA,"JANUARY_COMPLETE_NATIVE_SHA")
    games=json.loads(source)["selected"]
    original=json.loads(prior)["cases"]
    result={"schema":"c3x018-Jan2026-three-fixed-source-TT-probe-disappearance-v1",
       "study":"ADAPTIVE_AFTER_J2_J3_J4_FAIL",
       "source_sha256":SOURCE_SHA,"prior_native_sha256":EARLIER_SHA,
       "fixed_sites":[{"id":id,"role":r} for id,r in SITES],"cases":[]}
    for cid,role in SITES:
        world,norm=canonical_engine_world(games[cid-1])
        clock=game_clocks(games[cid-1])
        old=original[cid-1]
        need(old["id"]==cid and old["status"]=="VALID","PRIOR_SOURCE_CASE")
        base=old["selectors"][role]
        pair=base["selected_passive_pair"]
        watch={"key64":pair["physical"]["key64"],"root_call":pair["root_calls"][1]}
        record={"id":cid,"selector":role,"watch":watch,
                "source_pair":pair,"original_pair_status":base["status"],
                "arms":{}}
        for label in ("BASE","FIRST","SECOND","BOTH"):
            kwargs={"fen_clocks":clock,"probe_watch":watch}
            mode="OBS" if label=="BASE" else "V"
            target=None if label=="BASE" else pair["physical"]
            if label!="BASE":
                kwargs["tt_reader_filters"]=mask_filters(RULES[role],pair,label)
            x=play(a.engine,world,"F",mode,target,**kwargs)
            y=play(a.engine,world,"F",mode,target,**kwargs)
            need(x==y,"WATCH_COLD_REPEAT_"+str(cid)+"_"+label)
            old_uci=(old["controls"]["F"] if label=="BASE"
                     else base["arms"][label]["UCI"])
            need(x["UCI"]==old_uci,"WATCH_CHANGED_NATIVE_FINAL_CORE")
            hits=[e for e in x["watched_tt_probes"] if e["kind"]=="probe"]
            censor=[e for e in x["watched_tt_probes"] if e["kind"]=="censored"]
            need(not censor,"WATCH_CENSORED_"+str(cid))
            need(all(e["key64"]==watch["key64"] and
                     e["root_call"]==watch["root_call"]
                     for e in hits),"PROBE_LOG_UNEXPECTED_SOURCE")
            blocks=[e for e in x["blocks"] if e["kind"]=="reader_block"]
            expected=(0 if label=="BASE" else base["arms"][label]["blocked"])
            need(len(blocks)==expected,"TT_V_BLOCK_COUNT_SOURCE_DRIFT")
            record["arms"][label]={
               "UCI":x["UCI"],
               "tt_probe_observed":len(hits)>0,
               "tt_probe_count":len(hits),
               "tt_probe_hits":sum(e["tt_hit"]==1 for e in hits),
               "tt_probe_misses":sum(e["tt_hit"]==0 for e in hits),
               "tt_probe_details":hits,
               "actual_source_TT_value_reader_blocks":blocks,
               "pre_gate_selected_physical_TT_value_reads":[e for e in x["payload_witnesses"]
                    if e["kind"]=="reader" and e.get("reader_root_call")==watch["root_call"]],
               "second_root_window_entered":any(e["kind"]=="window_enter"
                    and e.get("root_call")==watch["root_call"]
                    for e in x["root_events"])}
            print("C3X018_JANUARY_NATIVE_TT_PROBE_MICROSCOPE",
                  cid,role,label,"probes",len(hits),"hits",sum(e["tt_hit"]==1 for e in hits),
                  "reader_blocks",len(blocks),flush=True)
        result["cases"].append(record)
    c={x["id"]:x for x in result["cases"]}
    d1=c[2]["arms"]["BOTH"]["tt_probe_count"]==0
    d2=all(c[i]["arms"]["BOTH"]["tt_probe_hits"]>0 for i in (6,16))
    result["summary"]={
      "cases":3,
      "prior_original_J2_to_J4":"FAIL_NOT_RESURRECTED",
      "DQ1_GAME2_SECOND_CALL_HAS_NO_SOURCE_TT_PROBE":"PASS" if d1 else "FAIL",
      "DQ2_GAMES6_16_SECOND_CALL_HAS_SOURCE_TT_PROBE_HIT":"PASS" if d2 else "FAIL",
      "DQ3_COLD_AND_PRIOR_UCI_SOURCE_REPLAY":"PASS",
      "DQ4_PASSIVE_EXACT_NO_CENSOR":"PASS",
      "result_source_classification":[{"game":x["id"],"selector":x["selector"],
         "paired_second_call_probe_count":x["arms"]["BOTH"]["tt_probe_count"],
         "paired_second_call_probe_hits":x["arms"]["BOTH"]["tt_probe_hits"],
         "paired_second_call_value_evaluation_reads":len(x["arms"]["BOTH"]["pre_gate_selected_physical_TT_value_reads"])}
         for x in result["cases"]]}
    result["limits"]=[
      "Three source cases selected adaptively after outcomes; no independent replication",
      "Watching exact key at TT.probe does not tell whether the chess node returned early before probing",
      "Native ttHit is Stockfish key16 table key signal, not independent full64 last-writer causality",
      "A probe hit without V evaluation read may reflect cutoff/condition or search evaluation gating",
      "Same within-arm root call count is not an invariant cross-arm recursive node identity",
      "January original J2 J3 J4 FAIL is unchanged"]
    out=Path(a.out);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("C3X018_JANUARY_PRE_REGISTERED_ADAPTIVE_TT_PROBE_MICROSCOPE",
          json.dumps(result["summary"],sort_keys=True),flush=True)
if __name__=="__main__":main()

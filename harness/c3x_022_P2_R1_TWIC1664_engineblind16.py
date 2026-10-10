#!/usr/bin/env python3
"""Precommitted new TWIC1664 16 Standard Chess boards, exclude 8 earlier sources
and prior TWIC1656 and puzzle16. Zero chess engine or SEE-based selection.
TWIC original game ZIP and full PGN never go to public artifact.
"""
import argparse
import hashlib
import json
from pathlib import Path
from c3x_022_P2_external_TWIC_puzzle_engineblind_selector import prior_fens,twic,HISTORY

PRIOR_EXTERNAL_SHA="ebe6648f43f64c6f31e0d547845bec3d87c663093fd68298acf2ebe4c0287554"
ISSUE=1664
URL="https://theweekinchess.com/zips/twic1664g.zip"
PRECOMMIT="c3x/ontology/c3x-022-P2-R1-path-dependent-root-survival-TT-value-SEE-newTWIC-precommit.md"

def seal(twic_zip,prior_inputs,p2prior):
    eight,hist=prior_fens(prior_inputs)
    external_raw=Path(p2prior).read_bytes()
    if hashlib.sha256(external_raw).hexdigest()!=PRIOR_EXTERNAL_SHA:
        raise ValueError("EXTERNAL32_HISTORICAL_SHA_CHANGED")
    old=json.loads(external_raw)
    if old["selected_count"]!=32:raise ValueError("PRIOR_SOURCE_32_DRIFT")
    external=old["ecologies"]["twic"]["selected"]+old["ecologies"]["lichess_puzzles"]["selected"]
    if len(external)!=32:raise ValueError("PREVIOUS_TWIC_PUZZLE_COUNT")
    seen=eight | {x["fen4"] for x in external}
    rows,meta=twic(twic_zip,seen,issue=ISSUE)
    if len(rows)!=16 or len({r["fen4"] for r in rows})!=16:raise ValueError("HOLD_16_SOURCE")
    if set(x["fen4"] for x in rows)&seen:raise ValueError("HISTORICAL_FEN4_REUSED")
    return {"schema":"c3x022-P2-R1-newTWIC1664-16-engineblind-v1",
      "phase":"NEW_TWIC1664_SOURCE_ONLY_BEFORE_ANY_NEW_NATIVE_OUTCOME",
      "precommit":PRECOMMIT,"new_official_source_URL":URL,
      "original_twic_archive_SHA256":meta["zip_sha256"],
      "historical_preP2_unique_fen4":len(eight),
      "exclusions_including_P2_32_unique_fen4":len(seen),
      "historical_source_input_SHA256":hist,
      "excluded_external_P2_cohort_SHA256":PRIOR_EXTERNAL_SHA,
      "source":meta,"selected":rows,
      "license":"TWIC personal use only, original PGN NEVER distributed",
      "engine_calls_for_source_selection":0,
      "eligibility":"first512 eligible in first20000 scanned, SHA order first16",
      "newly_selected_source_labels_chess_is_Standard_not_Atomic_variant":True}

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--twic",required=True)
    a.add_argument("--p2prior",required=True)
    for k in HISTORY:a.add_argument("--"+k,required=True)
    a.add_argument("--out",required=True)
    q=a.parse_args()
    d=seal(q.twic,{k:getattr(q,k) for k in HISTORY},q.p2prior)
    out=Path(q.out);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(d,sort_keys=True,indent=2,ensure_ascii=False)+"\n")
    print("C3X022_P2_R1_NEW_TWIC1664_BLIND16",d["source"]["scanned"],len(d["selected"]),d["original_twic_archive_SHA256"],hashlib.sha256(out.read_bytes()).hexdigest(),flush=True)
if __name__=="__main__":main()

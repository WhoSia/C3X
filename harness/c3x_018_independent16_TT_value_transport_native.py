#!/usr/bin/env python3
"""C3X018 truly new source-game blind TT reader-value mediation court.

Cohort was selected in distinct engine-free GitHub Actions workflow, locked
by its exact SHA before outcomes. No target is selected by looking at V/W2.
All 16 positions retained, including nonfiring/held cases.
"""
import argparse,hashlib,json
from pathlib import Path
from c3x_018_native_TT_lineage_factorial_6_8 import play,need

FROZEN_SOURCE_SHA="6520672aabab7f525872169085f19bdd81e27a4473f0c58ba9c9aa428937104c"
FROZEN_BROADCAST_ZST_SHA="77be4c998ca8d3b303928e1619f0f9dc2a03a71d5ab6a59d02d42291ae0524e3"
FROZEN_FIRST_SOURCE_RUN=37981820261
RAW_FIELDS=("raw_value","raw_depth","raw_bound","raw_eval","raw_move")

def first_passive_target(row):
    candidates=[e for e in row["payload_witnesses"]
        if e["kind"]=="discovery" and e["known"]==1 and e["matched"]==1
           and e["writer_serial"]>0 and e["epoch"]>0 and 0<=e["slot"]<3
           and e["key64"]==e["writer_key64"]]
    if not candidates:return None,0
    e=candidates[0]
    return {k:e[k] for k in ("key64","slot","epoch")},len(candidates)

def verified_reader_lineage(row):
    if not row["payload_witnesses"]:return {"count":0,"all_valid":None}
    writes={}
    count=0
    for seq,e in enumerate(row["payload_witnesses"]):
        key=(e["key64"],e["slot"],e["epoch"],e["writer_serial"])
        if e["kind"]=="writer":
            need(e["writer_serial"]>0 and key not in writes,"WRITER_SERIAL_REUSED")
            writes[key]=(seq,e)
        if e["kind"]=="reader":
            need(key in writes and writes[key][0]<seq,"READER_WITHOUT_PRIOR_WRITE")
            old=writes[key][1]
            need(e["known"]==1 and e["matched"]==1
                 and e["key64"]==e["writer_key64"],"WRITER_KEY_OR_SNAPSHOT_INVALID")
            need(all(old[f]==e[f] for f in RAW_FIELDS),"RAW_PAYLOAD_CHANGED")
            count+=1
    return {"count":count,"all_valid":True if count else None}

def classify(r,F):
    s=r["lineage_summary"]
    return {"UCI":r["UCI"],"writer_blocks":s["writer_block"],
            "reader_blocks":s["reader_block"],
            "bestmove_differs_F":r["UCI"]["bestmove"]!=F["bestmove"],
            "full_core_differs_F":r["UCI"]!=F,
            "witness":verified_reader_lineage(r)}

def main():
    p=argparse.ArgumentParser()
    for k in ("cohort","engine","out"):p.add_argument("--"+k,required=True)
    a=p.parse_args()
    b=Path(a.cohort).read_bytes()
    need(hashlib.sha256(b).hexdigest()==FROZEN_SOURCE_SHA,"SOURCE_SHA_NOT_FROZEN")
    data=json.loads(b)
    need(data["compressed_source_sha256"]==FROZEN_BROADCAST_ZST_SHA,"BROADCAST_ARCHIVE_SHA")
    need(len(data["selected"])==16,"EXACT_PRESELECTED_16_DENOMINATOR")
    result={"schema":"c3x018-2025oct-independent-16-game-original-history-value-mediation-v1",
       "source_run":FROZEN_FIRST_SOURCE_RUN,"source_cohort_sha256":FROZEN_SOURCE_SHA,
       "source_archive_sha256":FROZEN_BROADCAST_ZST_SHA,
       "source_original_full_game_histories":True,
       "source_sample_excluded_from_engine_selection":True,
       "predictions_preregistered":True,"cases":[]}
    for world in data["selected"]:
        cid=world["id"]
        row={"id":cid,"source_game_sha256":world["source_game_sha256"],
             "source_url":world["game_url"],"fen4":world["fen4"],
             "played_original_move":world["played_legal_move_uci"],
             "status":"NOT_RUN","arms":{}}
        try:
            controls={}
            for arm in ("O","F","Z"):
                first=play(a.engine,world,arm,"OBS")
                again=play(a.engine,world,arm,"OBS")
                need(first==again,f"COLD_CONTROL_{cid}_{arm}")
                controls[arm]=first["UCI"]
            need(controls["O"]==controls["Z"],f"ZERO_CONTACT_SHAM_{cid}")
            discovery=play(a.engine,world,"F","OBS",discovery=True)
            replay=play(a.engine,world,"F","OBS",discovery=True)
            need(discovery==replay,f"COLD_DISCOVERY_{cid}")
            need(discovery["UCI"]==controls["F"],f"DISCOVERY_CHANGED_SOURCE_CORE_{cid}")
            selected,eligible=first_passive_target(discovery)
            row["arms"]["O"]=controls["O"]
            row["arms"]["F"]=controls["F"]
            row["arms"]["Z"]=controls["Z"]
            row["passive_discovery"]={"candidates_recorded":eligible,
                "first_eligible_target":selected}
            if selected is None:
                row["status"]="NO_ELIGIBLE_PASSIVE_TT_VALUE_READER"
            else:
                row["target"]=selected
                decoy=play(a.engine,world,"F","V",
                     {"key64":18446744073709551615,"slot":0,"epoch":1})
                need(decoy["UCI"]==controls["F"] and
                     decoy["lineage_summary"]["reader_block"]==0,
                     f"IMPOSSIBLE_KEY_DECOY_{cid}")
                for arm,mode,dose in (("V","V",None),("W2","W",2)):
                    first=play(a.engine,world,"F",mode,selected,writer_budget=dose)
                    again=play(a.engine,world,"F",mode,selected,writer_budget=dose)
                    need(first==again,f"COLD_TREATMENT_{cid}_{arm}")
                    row["arms"][arm]=classify(first,controls["F"])
                row["decoy_no_contact_exact"]=True
                row["status"]="EXPERIMENTED"
            print("C3X018_FROZEN_INDEPENDENT_GAME",cid,row["status"],
                  "F",controls["F"]["bestmove"],
                  "V",row["arms"].get("V",{}).get("UCI",{}).get("bestmove"),
                  "W2",row["arms"].get("W2",{}).get("UCI",{}).get("bestmove"),flush=True)
        except (RuntimeError,ValueError,KeyError) as exc:
            row["status"]="HOLD_FAIL_CLOSED"
            row["failure"]=type(exc).__name__+":"+str(exc)[:240]
            print("C3X018_COURT_HOLD",cid,row["failure"],flush=True)
        result["cases"].append(row)
    need([c["id"] for c in result["cases"]]==list(range(1,17)),"INCOMPLETE_DENOMINATOR")
    done=[x for x in result["cases"] if x["status"]=="EXPERIMENTED"]
    vchanges=[x for x in done if x["arms"]["V"]["reader_blocks"]>0
              and x["arms"]["V"]["bestmove_differs_F"]]
    vonly=[x for x in vchanges if not x["arms"]["W2"]["bestmove_differs_F"]]
    holds=[x["id"] for x in result["cases"] if x["status"]=="HOLD_FAIL_CLOSED"]
    nonfiring=[x["id"] for x in done if x["arms"]["V"]["reader_blocks"]==0]
    invalid_payload=[x["id"] for x in done if x["arms"]["V"]["witness"]["all_valid"] is False]
    result["summary"]={
        "full_denominator":16,
        "experimented":len(done),
        "no_passive_target":sum(x["status"]=="NO_ELIGIBLE_PASSIVE_TT_VALUE_READER" for x in result["cases"]),
        "hold":len(holds),"hold_ids":holds,
        "V_nofire_ids":nonfiring,
        "V_realized_root_flips":len(vchanges),
        "W2_root_flips":sum(x["arms"]["W2"]["bestmove_differs_F"] for x in done),
        "V_only_root_flips":len(vonly),
        "P1_at_least_one_contacted_V_root_flip":"PASS" if vchanges else "FAIL",
        "P2_all_V_root_flips_are_W2_root_flips":("NOT_TESTED" if not vchanges else "FAIL" if vonly else "PASS"),
        "P3_100pct_claimed_writer_payload_verified":"FAIL" if invalid_payload else "NOT_TESTED" if not done else "PASS",
        "P3_value_claims":sum(x["arms"]["V"]["witness"]["count"] for x in done),
        "valid_complete":not holds
    }
    result["limits"]=[
      "No new source record chosen after any SF16 output: game source SHA pinned in separate source-only workflow",
      "Cohort includes all 16 original PGN histories, but native stockfish tests use standalone FEN rather than history-sensitive replay",
      "First eligible V reader chosen from treated F passive observation; not an external intervention-independent position-specific TT marker",
      "Reader eligibility after V intervention may differ or not fire; nonfiring remains denominator",
      "P2 vacuous if no V flip and must not be reported as PASS",
      "TT physical last writer payload matches consumed bytes but does not prove unique natural causal source mediation",
      "W2 suppresses whole save, including move16, and is a different intervention than V",
      "Broadcast games may have shared tournament ecology; different game history does not mean statistical independence of players",
      "Single SF16 depth12 Threads1 Hash16 NNUE off; one 2025 month external cohort, no separate engine replication"
    ]
    out=Path(a.out);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("C3X018_INDEPENDENT_16_TT_VALUE_FALSIFICATION_RESULT",
          json.dumps(result["summary"],sort_keys=True),flush=True)
    if holds:raise RuntimeError("C3X018_TT16_SOURCE_COURT_HOLD_FAIL_CLOSED_"+str(holds))
if __name__=="__main__":main()

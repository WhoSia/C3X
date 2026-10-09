#!/usr/bin/env python3
"""C3X018 fixed 16-game halfmove/fullmove vs original-history factor court.

C00 and HIST outcomes pinned from earlier native ZIPs. C10/C01/C11 are
prospectively evaluated here. Not sole natural TT mediation.
"""
import argparse,hashlib,json
from pathlib import Path
import chess
from c3x_018_native_TT_lineage_factorial_6_8 import play,need
from c3x_018_independent16_TT_value_transport_native import canonical_engine_world,FROZEN_SOURCE_SHA

FEN_BASELINE_SHA="519796b24302736da13929076453cfc5278c2402a19c9903270057eee59832eb"
HIST_BASELINE_SHA="d29753ddf6cc292ec7d9e5aeb99464bc75776e2bfbd9bceaf425f03c2bfb82bd"

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def game_clocks(world):
    b=chess.Board()
    for uci in world["full_original_mainline_uci"][:world["source_ply_before_original_move"]]:
        move=chess.Move.from_uci(uci)
        need(move in b.legal_moves,"ORIGINAL_GAME_CLOCK_HISTORY_ILLEGAL")
        b.push(move)
    return b.halfmove_clock,b.fullmove_number

def main():
    p=argparse.ArgumentParser()
    for k in ("cohort","standalone","history","engine","out"):p.add_argument("--"+k,required=True)
    a=p.parse_args()
    need(sha(a.cohort)==FROZEN_SOURCE_SHA,"COHORT_SHA")
    need(sha(a.standalone)==FEN_BASELINE_SHA,"C00_SHA")
    need(sha(a.history)==HIST_BASELINE_SHA,"ORIGINAL_HISTORY_SHA")
    cohort=json.loads(Path(a.cohort).read_text())
    old=json.loads(Path(a.standalone).read_text())
    historical=json.loads(Path(a.history).read_text())
    result={
       "schema":"c3x018-original-chess-game-clock-rule50-fullmove-vs-history-factor-v1",
       "design":"ADAPTIVE_SECONDARY_PRECOMMITTED_FIXED_SOURCE_FACTORIAL",
       "source_manifest_sha256":FROZEN_SOURCE_SHA,
       "C00_native_sha256":FEN_BASELINE_SHA,
       "HIST_native_sha256":HIST_BASELINE_SHA,
       "cases":[]}
    for world,prev,hist in zip(cohort["selected"],old["cases"],historical["cases"]):
        cid=world["id"]
        need(cid==prev["id"]==hist["id"],"SOURCE_ID_ALIGNMENT")
        w,normal=canonical_engine_world(world)
        half,full=game_clocks(world)
        row={"id":cid,"game_url":world["game_url"],
             "original_halfmove_clock":half,"original_fullmove_number":full,
             "position_FEN4":w["fen4"],"status":"NOT_RUN","arms":{}}
        try:
            for arm in ("O","F"):
                reference=prev["arms"][arm]
                history=hist["arms"][arm]["historical_UCI"]
                result_arm={"C00":reference,"HIST":history}
                for code,clocks in (("C10",(half,1)),("C01",(0,full)),
                                    ("C11",(half,full))):
                    x=play(a.engine,w,arm,"OBS",fen_clocks=clocks)
                    y=play(a.engine,w,arm,"OBS",fen_clocks=clocks)
                    need(x==y,f"COLD_CLOCK_REPLAY_{cid}_{arm}_{code}")
                    need(x["root_contact"]["target_contact"]=="1",
                         f"ROOT_SOURCE_CONTACT_{cid}_{arm}_{code}")
                    result_arm[code]=x["UCI"]
                row["arms"][arm]=result_arm
            sham=play(a.engine,w,"Z","OBS",fen_clocks=(half,full))
            sham2=play(a.engine,w,"Z","OBS",fen_clocks=(half,full))
            need(sham==sham2,f"C11_Z_REPLAY_{cid}")
            need(sham["root_contact"]["target_contact"]=="0",
                 f"C11_Z_NO_CONTACT_{cid}")
            need(sham["UCI"]==row["arms"]["O"]["C11"],f"C11_OZ_SHAM_{cid}")
            row["C11_Z_no_contact_exact"]=True
            row["status"]="EXPERIMENTED"
            row["contrasts"]={}
            for arm in ("O","F"):
                x=row["arms"][arm]
                row["contrasts"][arm]={
                    "C10_C00_bestmove_diff":x["C10"]["bestmove"]!=x["C00"]["bestmove"],
                    "C01_C00_bestmove_diff":x["C01"]["bestmove"]!=x["C00"]["bestmove"],
                    "C11_C00_bestmove_diff":x["C11"]["bestmove"]!=x["C00"]["bestmove"],
                    "HIST_C11_bestmove_diff":x["HIST"]["bestmove"]!=x["C11"]["bestmove"],
                    "C10_C00_core_diff":x["C10"]!=x["C00"],
                    "C01_C00_core_diff":x["C01"]!=x["C00"],
                    "C11_C00_core_diff":x["C11"]!=x["C00"],
                    "HIST_C11_core_diff":x["HIST"]!=x["C11"]
                }
            print("C3X018_RULE50_FULLMOVE_HISTORY",cid,half,full,
                  "F",[(k,row["arms"]["F"][k]["bestmove"]) for k in ("C00","C10","C01","C11","HIST")],
                  flush=True)
        except (RuntimeError,ValueError,KeyError) as exc:
            row["status"]="HOLD_FAIL_CLOSED"
            row["failure"]=type(exc).__name__+":"+str(exc)[:260]
            print("C3X018_CLOCK_COURT_HOLD",cid,row["failure"],flush=True)
        result["cases"].append(row)
    need([c["id"] for c in result["cases"]]==list(range(1,17)),"FULL_DENOMINATOR")
    valid=[c for c in result["cases"] if c["status"]=="EXPERIMENTED"]
    summary={"total":16,"completed":len(valid),"holds":16-len(valid)}
    for arm in ("O","F"):
        for key in ("C10_C00_bestmove_diff","C01_C00_bestmove_diff",
                    "C11_C00_bestmove_diff","HIST_C11_bestmove_diff",
                    "C10_C00_core_diff","C01_C00_core_diff",
                    "C11_C00_core_diff","HIST_C11_core_diff"):
            summary[arm+"_"+key]=sum(c["contrasts"][arm][key] for c in valid)
    result["summary"]=summary
    result["limitations"]=[
        "Secondary analysis after original 16-game FEN/history outputs; not an independently preregistered discovery",
        "C10 isolates halfmove count with fullmove=1, C01 isolates fullmove label with halfmove=0, C11 combines both",
        "Six-field FEN cannot encode all repetition history; C11/HIST differences indicate missing state but do not isolate which source state",
        "All full original game prefixes retained; no source root identities selected after observing outcome",
        "Stockfish16 single-thread 16MB hash depth12 NNUE off, no uniqueness of TT writer-reader causal mechanism"]
    out=Path(a.out);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("C3X018_RULE50_FULLMOVE_HISTORY_SOURCE_NATIVE",
          json.dumps(summary,sort_keys=True),flush=True)
    if summary["holds"]:raise RuntimeError("C3X018_CLOCK_FACTORIAL_HOLD_FAIL_CLOSED")
if __name__=="__main__":main()

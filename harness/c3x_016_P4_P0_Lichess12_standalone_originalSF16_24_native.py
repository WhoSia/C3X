#!/usr/bin/env python3
"""C3X 0.16 P4-P0: original untouched SF16 source baseline on 12 FEN-only,
source-frozen Lichess game roots. NO concept source intervention in this phase.
Exactly cold replay; outcome cannot select/revise FEN cohort.
"""
import argparse,hashlib,json,os,re,subprocess
from pathlib import Path
import chess
FIXED_REF="68e1e9b3811e16cad014b590d7443b9063b3eb52"
def must(cond,message):
 if not cond:raise RuntimeError("C3X016_P4_P0_FAIL_CLOSED_"+message)
def go(engine,fen):
 result=[]
 with subprocess.Popen([engine],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,env=os.environ.copy(),text=True,bufsize=1) as proc:
  def send(*commands):proc.stdin.write("\n".join(commands)+"\n");proc.stdin.flush()
  def collect(needle):
   for _ in range(150000):
    line=proc.stdout.readline()
    must(bool(line),"UCI_EOF_"+needle)
    result.append(line.rstrip())
    if line.startswith(needle):return
   raise RuntimeError("C3X016_P4_UNBOUNDED_UCI_STREAM")
  send("uci");collect("uciok")
  send("setoption name Threads value 1","setoption name Hash value 16","setoption name MultiPV value 1","setoption name Use NNUE value false","ucinewgame","isready")
  collect("readyok")
  send("position fen "+fen,"go depth 12");collect("bestmove ")
  send("quit")
  must(proc.wait(timeout=45)==0,"ENGINE_EXIT")
 parsed=[]
 for row in result:
  if not row.startswith("info depth ") or " pv " not in row:continue
  depth=re.search(r"\bdepth (\d+)",row)
  score=re.search(r"\bscore (cp|mate) (-?\d+)(?: (lowerbound|upperbound))?(?:\s|$)",row)
  nodes=re.search(r"\bnodes (\d+)",row)
  if depth and int(depth.group(1))==12 and score and nodes:
   parsed.append({"score_kind":score.group(1),"score_value":int(score.group(2)),
     "score_bound":score.group(3) or "exact_reported","nodes":int(nodes.group(1)),
     "PV":row.split(" pv ",1)[1].split()[:16]})
 must(bool(parsed),"FINAL_DEPTH12_SCORE_MISSING")
 final=parsed[-1]
 best=[row.split()[1] for row in result if row.startswith("bestmove ")]
 must(len(best)==1 and final["PV"] and best[0]==final["PV"][0],"BESTMOVE_PV_MISMATCH")
 board=chess.Board(fen)
 must(board.is_legal(chess.Move.from_uci(best[0])),"BESTMOVE_ILLEGAL")
 final["bestmove"]=best[0]
 return final
def main():
 p=argparse.ArgumentParser()
 for n in ("cohort","engine","out"):p.add_argument("--"+n,required=True)
 a=p.parse_args()
 raw=Path(a.cohort).read_bytes()
 j=json.loads(raw)
 must(j["schema"]=="c3x016-P4-source-only-Lichess12-standalone-FEN-3x4-external-opportunity-cohort-v1","WRONG_COHORT_SCHEMA")
 roots=j["cases"]
 must(len(roots)==12 and len(set(z["fen"] for z in roots))==12,"ROOTS_NOT_12_UNIQUE_FEN")
 labels={}
 for item in roots:labels[item["motif"]]=labels.get(item["motif"],0)+1
 must(labels=={"SKEWER_RAY":3,"INTERFERENCE_RAY":3,"DEFENDER_REMOVAL_RAY":3,"NO_MOTIF_RAY_OPPORTUNITY":3},"STRATA_DRIFT")
 records=[]
 for item in roots:
  fen=item["fen"]+" 0 1"
  board=chess.Board(fen)
  must(board.is_valid() and len(item["fen"].split())==4,"ILLEGAL_FEN_"+item["id"])
  must(board.is_legal(chess.Move.from_uci(item["played_uci"])),"SOURCE_PLAYED_MOVE_NOT_LEGAL_"+item["id"])
  original=go(a.engine,fen)
  replay=go(a.engine,fen)
  must(original==replay,"COLD_REPLAY_"+item["id"])
  records.append({"id":item["id"],"source_opportunity":item["motif"],
       "standalone_FEN_sha256":hashlib.sha256(fen.encode()).hexdigest(),
       "actual_played_legal_move":item["played_uci"],
       "original_native":original,"cold_exact":True})
  print("C3X016_P4_NATIVE_STANDALONE",item["id"],item["motif"],original["bestmove"],
        original["score_value"],original["nodes"],flush=True)
 output={"schema":"c3x016-P4-P0-external-Lichess12-standalone-FEN-unpatched-SF16-24cold-native-v1",
  "pinned_upstream_SF16_commit":FIXED_REF,
  "source_FEN_cohort_sha256":hashlib.sha256(raw).hexdigest(),
  "original_source_Lichess_SHA256":j["original_source_sha256"],
  "original_game_count":12,"standalone_root_positions":12,
  "native_processes":24,"all_cold_replays_exact":True,
  "Lichess_game_history_mode":"FEN_STANDALONE, not complete original PGN history or repetition/rule50 counts",
  "replay_root_moves_legality":"python-chess original source legal vs Go source selection original game moves",
  "records":records,
  "claims":["Native original Stockfish search on 12 source-blind frozen FENs only",
    "Labels describe actual legally played move geometry opportunities, NOT verified tactics or engine cause",
    "No source-level TT/SEE/qsearch intervention in this P4-P0 and no new named concept causal effect identified",
    "Source-only frozen before native outcomes; no outcome-based sample replacement; historical 0.15 C1 prediction accuracy FAIL remains"]}
 Path(a.out).write_text(json.dumps(output,indent=2,sort_keys=True)+"\n")
 print("C3X016_P4_P0_INDEPENDENT_SOURCE_12_FEN_24_NATIVE_BASELINE_PASS",flush=True)
if __name__=="__main__":main()

#!/usr/bin/env python3
"""C3X 0.15 P2 source-native 64 pin and 64 no-pin court. No resampling."""
import argparse,collections,hashlib,json,os,re,subprocess
from pathlib import Path
import chess
from c3x_014_ROOT_PIN_object_guarded_SEE_40world_native_court import main_engine

SRC="1e932aa881eaef549c770211c078d930cd8d675e5688644e1bc36ab31bae4534"
PRED="1e4c2e1b6cf777df86da8b630afc1459cc4a60265645bbd13c8c78fead3894a6"
FULL_PRED="a4ebc45f8ab844e502aa507c64eb78f72371952c0512df676e4b33b0ccc4d172"
CORE=("score_kind","value_root_stm","score_flag","nodes","pv","bestmove")
def sha(x):return hashlib.sha256(x).hexdigest()
def check(x,why):
    if not x:raise RuntimeError(why)
def load(path,expected):
    b=Path(path).read_bytes()
    check(sha(b)==expected,"SEALED_BYTES_DIFFER_"+str(path))
    return json.loads(b)
def original(engine,moves,arm,sq,pn):
    env={**os.environ,"C3X014_PIN_ROOT_OBJECT_ARM":arm,
         "C3X014_PIN_ROOT_SQUARE_ID":str(sq),"C3X014_PIN_ROOT_PINNER_ID":str(pn)}
    lines=[]
    with subprocess.Popen([engine],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,
                          text=True,bufsize=1,env=env) as p:
        def send(*z):p.stdin.write("\n".join(z)+"\n");p.stdin.flush()
        def until(pre):
            for j in range(160000):
                s=p.stdout.readline()
                check(bool(s),"PREMATURE_ENGINE_EOF_"+pre)
                lines.append(s.rstrip())
                if s.startswith(pre):return
            raise RuntimeError("ENGINE_OUTPUT_LIMIT")
        send("uci");until("uciok")
        send("setoption name Threads value 1","setoption name Hash value 16",
             "setoption name MultiPV value 1","setoption name Use NNUE value false","ucinewgame","isready")
        until("readyok")
        send("position startpos moves "+" ".join(moves),"go depth 12")
        until("bestmove ")
        send("quit");check(p.wait(timeout=25)==0,"ENGINE_BAD_EXIT")
    info=[]
    for line in lines:
        if not line.startswith("info depth ") or " pv " not in line:continue
        de=re.search(r"\\bdepth (\\d+)",line)
        if not de or int(de.group(1))!=12:continue
        sc=re.search(r"\\bscore (cp|mate) (-?\\d+)(?: (lowerbound|upperbound))?(?:\\s|$)",line)
        nd=re.search(r"\\bnodes (\\d+)",line)
        if sc and nd:info.append(dict(score_kind=sc.group(1),value_root_stm=int(sc.group(2)),
            score_flag=sc.group(3) or "exact_reported",nodes=int(nd.group(1)),
            pv=line.split(" pv ",1)[1].split()[:16]))
    check(bool(info),"DEPTH12_NOT_COMPLETED")
    d=info[-1];best=[s.split()[1] for s in lines if s.startswith("bestmove ")]
    check(len(best)==1 and best[0]==d["pv"][0],"BESTMOVE_PV_MISMATCH")
    d["bestmove"]=best[0]
    stamps=[s for s in lines if s.startswith("info string c3x014_root_object_see ")]
    if stamps:
        check(len(stamps)==1,"GUARD_TRACE_DUPLICATED")
        d["guard"]={k:int(v) for k,v in (s.split("=") for s in stamps[0].split()[3:])}
    return d
def core(d):return {k:d[k] for k in CORE}
def main():
    ap=argparse.ArgumentParser()
    for k in ("source","pred","pristine","patched","out"):ap.add_argument("--"+k,required=True)
    a=ap.parse_args()
    source=load(a.source,SRC);pr=load(a.pred,PRED)
    check(pr["source_manifest_sha256"]==SRC and pr["original_full_prediction_sha256"]==FULL_PRED,
          "MODEL_PREOUTCOME_IDENTITY_NOT_FROZEN")
    pins=source["pin_roots"];controls=source["nonpin_controls"]
    check(len(pins)==len(controls)==64 and len({r["game_key_sha256"] for r in pins+controls})==128,
          "ORIGINAL_GAME_COHORT_CHANGED")
    fenhash=[sha(x["root_sixfield_fen"].encode()) for x in pins]
    check(sha("\n".join(fenhash).encode())==pr["ordered_fenhash_join_sha256"],"PREDICTION_ORDER_MISMATCH")
    check(all(len(pr[k])==64 and set(pr[k])<={"0","1"} for k in ("B0","B1","C1")),"PREDICTION_BITS_BAD")
    def replay(row):
        bd=chess.Board(row["initial_fen"]); hist=row["full_history_uci"][:row["root_ply"]]
        for move in hist:
            m=chess.Move.from_uci(move);check(m in bd.legal_moves,"ILLEGAL_SOURCE_GAME")
            bd.push(m)
        check(bd.fen(en_passant="fen")==row["root_sixfield_fen"],"SOURCE_BOARD_MISMATCH")
        return bd,hist
    rows=[]
    for i,row in enumerate(pins):
        board,hist=replay(row);p=row["objects"][0]
        sq=chess.parse_square(p["pinned_square"]);pn=chess.parse_square(p["pinner_square"])
        check(board.is_pinned(board.turn,sq),"SOURCE_PIN_NOT_LEGAL")
        native=original(a.pristine,hist,"OFF",sq,pn)
        world={"source_game_history_uci":hist,"pinned_square":p["pinned_square"],"pinning_square":p["pinner_square"]}
        arm={}
        for mode in ("OFF","ROOT_OBJECT_SEE_UNMASK"):
            pair=[main_engine(a.patched,world,mode) for _ in range(2)]
            check(pair[0]==pair[1],"SOURCE_NATIVE_COLD_REPEAT_MISMATCH")
            arm[mode]=pair[0]
        off=arm["OFF"];on=arm["ROOT_OBJECT_SEE_UNMASK"]
        check(core(native)==core(off),"INSTRUMENTED_OFF_CHANGED_PRISTINE_NATIVE")
        check(off["object_guard"]["target_fired"]==0 and on["object_guard"]["arm"]==1,
              "ROOT_PIN_OBJECT_GUARD_BROKEN")
        fire=on["object_guard"]["target_fired"]
        if not fire:check(core(off)==core(on),"NO_SITE_FIRING_YET_ENGINE_OUTPUT_CHANGED")
        moved=int(off["bestmove"]!=on["bestmove"])
        rows.append({"ordinal":i+1,"fen_sha256":fenhash[i],"game_sha256":row["game_key_sha256"],
                     "event":row["headers"].get("Event",""),"law":p["law"],
                     "pred":{k:int(pr[k][i]) for k in ("B0","B1","C1")},
                     "source_site_fires":fire,"y_changed_bestmove":moved,
                     "native_pristine_OFF":core(native),"native_ROOT_SEE_UNMASK":core(on),
                     "source_guard":on["object_guard"]})
        print("C3X015_P2_PIN",i+1,"SITE_FIRES",fire,"ROOT_MOVE_CHANGE",moved,flush=True)
    ctrl=[]
    for i,row in enumerate(controls):
        board,hist=replay(row)
        check(not any(board.is_pinned(board.turn,sq) for sq,pc in board.piece_map().items()
                  if pc.color==board.turn and pc.piece_type!=chess.KING),"NONPIN_HAS_ABSOLUTE_PIN")
        n=original(a.pristine,hist,"OFF",0,0)
        off=original(a.patched,hist,"OFF",0,0)
        on=original(a.patched,hist,"ROOT_OBJECT_SEE_UNMASK",0,0)
        check(core(n)==core(off)==core(on),"NONPIN_SHAM_VS_PRISTINE_FAILED")
        check(off.get("guard",{}).get("arm")==-1 and on.get("guard",{}).get("arm")==-1,
              "NONPIN_SOURCE_GUARD_NOT_DISABLED")
        ctrl.append({"ordinal":i+1,"root_FEN_sha256":sha(row["root_sixfield_fen"].encode()),
                     "sham_equal":True})
        print("C3X015_P2_NONPIN",i+1,"NATIVE_SHAM_PASS",flush=True)
    y=[z["y_changed_bestmove"] for z in rows];summ={}
    for k in ("B0","B1","C1"):
        p=[z["pred"][k] for z in rows]
        tp=sum(a and b for a,b in zip(p,y));tn=sum(not a and not b for a,b in zip(p,y))
        fp=sum(a and not b for a,b in zip(p,y));fn=sum(not a and b for a,b in zip(p,y))
        summ[k]={"correct":tp+tn,"accuracy":(tp+tn)/64,
                 "TP":tp,"TN":tn,"FP":fp,"FN":fn,
                 "balanced_accuracy":((tp/(tp+fn))+(tn/(tn+fp)))/2 if (tp+fn)*(tn+fp)>0 else None}
    result={"schema":"c3x-015-TWIC1665-P2-prescored-root-object-SEE-native-v1",
      "source_SHA256":SRC,"pred_compact_SHA256":PRED,"pred_full_prior_SHA256":FULL_PRED,
      "upstream_commit":"68e1e9b3811e16cad014b590d7443b9063b3eb52",
      "actual_native_engine_processes":64*5+64*3,
      "pin_count":64,"nonpin_count":64,"pin_cold_pairs_equal":128,
      "pin_OFF_original_equal":64,"nonpin_negative_shams_equal":64,
      "firing_worlds":sum(x["source_site_fires"]>0 for x in rows),
      "firing_events":sum(x["source_site_fires"] for x in rows),
      "root_move_changes":sum(y),"event_sample_sizes":dict(collections.Counter(x["event"] for x in rows)),
      "frozen_predictions_vs_actual":summ,
      "pin_worlds":rows,"nonpin_shams":ctrl,
      "limits":["The intervention changes Stockfish SEE software, not board chess law.",
       "No TT/alpha-beta first-divergence correspondence established by this P2 endpoint.",
       "Historic 0.13 global duplicate corpus only partially audited.",
       "No direct NNUE latent feature claim."]}
    Path(a.out).write_text(json.dumps(result,sort_keys=True,indent=2,ensure_ascii=False)+"\n")
    print("C3X015_P2_ACTUAL_NATIVE_CONCLUSION",json.dumps({k:result[k] for k in
      ("firing_worlds","firing_events","root_move_changes","frozen_predictions_vs_actual")},
      sort_keys=True),flush=True)
if __name__=="__main__":main()

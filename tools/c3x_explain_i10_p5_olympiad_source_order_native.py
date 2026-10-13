"""C3X I10-P5 original Stockfish 16 ROOT order source intervention on NEW 2026 Olympiad games.

Cold original O, patched O/F/Z repeated; source patch from existing independent
C3X0.16 P4 (NOT new surgical mechanism). Full PGN historic UCI replay prevents
P4's standalone-FEN repetition-history truncation. Source claims remain
constrained to root candidate order sensitivity, not human chess concept.
"""
from __future__ import annotations
import argparse, hashlib, json, os, re, subprocess
from pathlib import Path
from tools.c3x_explain_i10_p5_olympiad_source_targets import native_uci,SOURCE_SHA,GAME_SHA

CORE=("bestmove","score_kind","score_value","score_flag","nodes","pv")

def engine_one(engine:str,row:dict,mode:str,patched:bool,depth:int=11)->dict:
    if row["native_move"]!=native_uci(row["uci"]):
        raise ValueError("SOURCE_NATIVE_MOVE_ENCODING_CHANGED")
    fen4=" ".join(row["full_fen"].split()[:4])
    if fen4!=row["fen4"]:
        raise ValueError("SOURCE_ORIGINAL_FEN4_MISMATCH")
    env=os.environ.copy()
    if patched:
        env.update({"C3X016_P4_MODE":mode,"C3X016_P4_FEN4":fen4,
                    "C3X016_P4_PLAYED_NATIVE":str(row["native_move"])})
    cmds=["uci","setoption name Threads value 1","setoption name Hash value 16",
          "setoption name MultiPV value 1","setoption name Use NNUE value false",
          "ucinewgame","isready","position startpos moves "+" ".join(row["context_pre_moves"]),
          "go depth "+str(depth)]
    p=subprocess.Popen([engine],stdin=subprocess.PIPE,stdout=subprocess.PIPE,
                       stderr=subprocess.STDOUT,env=env,text=True,bufsize=1)
    output=[]
    try:
        def readuntil(marker):
            for _ in range(40000):
                line=p.stdout.readline()
                if not line:raise ValueError("SOURCE_ENGINE_EARLY_EOF_"+marker)
                output.append(line.rstrip("\n"))
                if line.startswith(marker):return
            raise ValueError("SOURCE_ENGINE_EXCESSIVE_TEXT")
        p.stdin.write("uci\n");p.stdin.flush();readuntil("uciok")
        p.stdin.write("\n".join(cmds[1:7])+"\n");p.stdin.flush();readuntil("readyok")
        p.stdin.write("\n".join(cmds[7:])+"\n");p.stdin.flush()
        readuntil("bestmove ")
        p.stdin.write("quit\n");p.stdin.flush()
        if p.wait(timeout=30)!=0:raise ValueError("SOURCE_NATIVE_EXIT_NONZERO")
    finally:
        if p.poll() is None:p.kill()
    scores=[]
    for line in output:
        if not line.startswith("info depth ") or " pv " not in line:continue
        d=re.search(r"\bdepth (\d+)\b",line)
        sc=re.search(r"\bscore (cp|mate) (-?\d+)(?: (lowerbound|upperbound))?",line)
        nd=re.search(r"\bnodes (\d+)\b",line)
        if d and int(d.group(1))==depth and sc and nd:
            scores.append({"score_kind":sc.group(1),"score_value":int(sc.group(2)),
                           "score_flag":sc.group(3) or "exact_reported",
                           "nodes":int(nd.group(1)),
                           "pv":line.split(" pv ",1)[1].split()[:16]})
    if not scores:raise ValueError("NO_COMPLETED_DEPTH_NATIVE_PV")
    val=scores[-1]
    best=[s.split()[1] for s in output if s.startswith("bestmove ")]
    if len(best)!=1 or not val["pv"] or val["pv"][0]!=best[0]:
        raise ValueError("NATIVE_BESTMOVE_PV_INCONSISTENCY")
    val["bestmove"]=best[0]
    if patched:
        lines=[x for x in output if x.startswith("info string c3x016_p4_root_order ")]
        if len(lines)!=1:raise ValueError("ORIGINAL_SOURCE_PHYSICAL_ROOT_CONTACT_REPORT_NOT_UNIQUE")
        fields=[z.split("=",1) for z in lines[0].split()[3:]]
        info=dict(fields)
        need={"mode","guard","root_legal_count","selected_native","selected_pre_index",
              "target_contact","target_pre_index","source_reorder","new_front_native"}
        if set(info)!=need:raise ValueError("SOURCE_EVENT_SCHEMA_MISMATCH")
        val["physical_source"]={k:v if k=="mode" else int(v) for k,v in info.items()}
    return val

def core(x):
    return {k:x[k] for k in CORE}

def court(preseal:dict,engine_orig:str,engine_patched:str,depth:int=11)->dict:
    if preseal["original_source_sha256"]!=SOURCE_SHA or len(preseal["positions"])!=8:
        raise ValueError("C3X_P5_COHORT_NOT_PRESEALED")
    if [p["game_id"] for p in preseal["positions"]]!=GAME_SHA:
        raise ValueError("SOURCE_COHORT_ORDER_OR_IDENTITY_CHANGED")
    outcomes=[]
    for row in preseal["positions"]:
        u=engine_one(engine_orig,row,"ORIGINAL",False,depth)
        cells={}
        for mode in ("O","F","Z"):
            first=engine_one(engine_patched,row,mode,True,depth)
            second=engine_one(engine_patched,row,mode,True,depth)
            if first!=second:raise ValueError("SOURCE_NATIVE_COLD_REPLAY_CHANGED_"+mode)
            p=first["physical_source"]
            if p["mode"]!=mode or p["guard"]!=1 or p["selected_native"]!=row["native_move"]:
                raise ValueError("ACTUAL_NATIVE_CONTACT_GUARD_FAIL")
            if p["target_contact"]!=int(mode!="Z"):
                raise ValueError("SOURCE_INTERVENTION_CONTACT_MISMATCH")
            if p["source_reorder"]!=int(mode=="F" and p["selected_pre_index"]>0):
                raise ValueError("SOURCE_ROOT_REORDER_GATE_MISMATCH")
            if mode=="O" and core(u)!=core(first):
                raise ValueError("PATCHED_OBSERVATION_ALTERS_ORIGINAL_ENGINE_BASELINE")
            if mode=="Z" and core(first)!=cells["O"]["uci"]:
                raise ValueError("NO_CONTACT_NEGATIVE_CONTROL_DIFFERS")
            if mode=="F" and p["selected_pre_index"]==0 and core(first)!=cells["O"]["uci"]:
                raise ValueError("NO_REAL_ORDER_CHANGE_BUT_ENGINE_RESULT_CHANGED")
            cells[mode]={"uci":core(first),"physical_source":p}
        o=cells["O"]["uci"];f=cells["F"]["uci"]
        d={
            "source_reorder_activated":bool(cells["F"]["physical_source"]["source_reorder"]),
            "root_bestmove_changed":o["bestmove"]!=f["bestmove"],
            "reported_cp_or_bound_changed":tuple(o[k] for k in ("score_kind","score_value","score_flag"))!=
                                           tuple(f[k] for k in ("score_kind","score_value","score_flag")),
            "nodes_changed":o["nodes"]!=f["nodes"],
            "PV_changed":o["pv"]!=f["pv"]
        }
        outcomes.append({
            "game_id":row["game_id"],"group":row["split"],
            "played_uci":row["uci"],"played_san":row["san"],"ply":row["ply"],
            "fen":row["full_fen"],"historical_move_count":len(row["context_pre_moves"]),
            "original_unmodified":core(u),
            "source_world_cells":cells,
            "source_intervention_observation":d,
            "causal_scope":"NATIVE_SEARCH_ROOT_ORDER_ONLY_IF_REORDER_CONTACT_CONFIRMED",
            "human_chess_semantic_concept_label":None,
            "chess_semantic_causal_certificate":None,
        })
        print("C3X_P5_ORIGINAL_NATIVE_ROOT_SOURCE_EVENT",row["game_id"],row["split"],row["san"],
             d,"root_O",o["bestmove"],"root_F",f["bestmove"],flush=True)
    summary={k:sum(x["source_intervention_observation"][k] for x in outcomes)
             for k in outcomes[0]["source_intervention_observation"]}
    return {
        "schema":"c3x-i10-p5-new-Olympiad-original-SF16-eight-game-source-order-O-F-Z-native-v1",
        "source_original_sha":"68e1e9b3811e16cad014b590d7443b9063b3eb52",
        "source_pgn_sha256":SOURCE_SHA,
        "source_selection":"ENGINE_BLIND_PREDECLARED_8_DISTINCT_GAME_GROUPS",
        "original_full_game_histories_replayed":True,
        "native_engine_new_source_operations":8*(1+3*2),
        "native_engine_unmodified_original_references":8,
        "actual_patch_modes":["O","F","Z"],
        "research_evaluation_groups":["TRAIN","EVAL"],
        "source_order_intervention_scope":"ONLY_FIRST_ITERATIVE_ROOT_MOVES_ORDER_WITH_SAME_ROOT_LEGAL_MOVE_SET",
        "depth":depth,"worlds":outcomes,"summary":summary,
        "independent_game_source_new_to_I10_P4":True,
        "human_chess_strategic_semantic_causes_proven":False,
        "opponent_reply_transfer_achieved":None,
        "original_Ethereal_P16_authority_promoted":False,
        "C3X_science_0_26_upgrade":False,
    }

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--cohort",required=True)
    a.add_argument("--original",required=True)
    a.add_argument("--patched",required=True)
    a.add_argument("--out",required=True)
    args=a.parse_args()
    p=json.loads(Path(args.cohort).read_text())
    r=court(p,args.original,args.patched)
    Path(args.out).write_text(json.dumps(r,ensure_ascii=False,indent=2)+"\n")
    print("C3X_P5_NEW_SOURCE_INTERVENTION_FROZEN_NATIVE_PASS",json.dumps(r["summary"],sort_keys=True))

if __name__=="__main__":main()

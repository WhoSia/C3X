#!/usr/bin/env python3
"""C3X016 P4: 12 source-frozen, nonpin-origin, multi-motif root-order native court.
Original Stockfish binary checked; O/F/Z two cold trials; run depth12 single thread.
No raw third-party PGN in this program or output.
"""
import argparse,hashlib,json,os,re,subprocess
from pathlib import Path
from collections import Counter
SOURCE_SHA="65905d611c0d78d90ab57cd9edd3821f4119b46c22b5489fd7e265a74c6767b3"
FROZEN_SELECTION="08bf2179e141ba6a862314660298fa90fa61c3d377e46accc07bd4c5d9cacae2"
GROUPS=("SKEWER_RAY","INTERFERENCE_RAY","DEFENDER_REMOVAL_RAY","NO_MOTIF_RAY_OPPORTUNITY")
CORE=("bestmove","score_kind","score_value","score_flag","nodes","pv")

def need(ok,msg):
    if not ok:raise RuntimeError("C3X016_P4_FAIL_CLOSED_"+str(msg))
def native_uci(move):
    need(len(move)==4 and all(move[i] in "abcdefgh" for i in (0,2)) and
         all(move[i] in "12345678" for i in (1,3)),"ROOT_MOVE_SHAPE")
    frm=(ord(move[0])-97)+8*(int(move[1])-1)
    to=(ord(move[2])-97)+8*(int(move[3])-1)
    return frm*64+to
def play(engine,world,mode,patched):
    env={**os.environ}
    if patched:
        env.update({"C3X016_P4_MODE":mode,"C3X016_P4_FEN4":world["fen4"],
                    "C3X016_P4_PLAYED_NATIVE":str(world["native_move"])})
    output=[]
    with subprocess.Popen([engine],stdin=subprocess.PIPE,stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT,env=env,text=True,bufsize=1) as p:
        def send(*items):
            p.stdin.write("\n".join(items)+"\n");p.stdin.flush()
        def read(marker):
            for _ in range(100000):
                z=p.stdout.readline()
                need(z,"PREMATURE_UCI_EOF_"+marker)
                output.append(z.rstrip("\n"))
                if z.startswith(marker):return
            raise RuntimeError("UCI_OUTPUT_LINE_CAP")
        send("uci");read("uciok")
        send("setoption name Threads value 1","setoption name Hash value 16",
             "setoption name MultiPV value 1","setoption name Use NNUE value false",
             "ucinewgame","isready");read("readyok")
        send("position fen "+world["fen4"]+" 0 1","go depth 12")
        read("bestmove ")
        send("quit")
        need(p.wait(timeout=45)==0,"ENGINE_EXIT_NONZERO")
    scores=[]
    for s in output:
        if not s.startswith("info depth ") or " pv " not in s:continue
        md=re.search(r"\bdepth (\d+)\b",s)
        sc=re.search(r"\bscore (cp|mate) (-?\d+)(?: (lowerbound|upperbound))?",s)
        nc=re.search(r"\bnodes (\d+)\b",s)
        if md and md.group(1)=="12" and sc and nc:
            scores.append({"score_kind":sc.group(1),"score_value":int(sc.group(2)),
                           "score_flag":sc.group(3) or "exact_reported",
                           "nodes":int(nc.group(1)),
                           "pv":s.split(" pv ",1)[1].split()[:16]})
    need(scores,"DEPTH12_SCORE_MISSING")
    val=scores[-1]
    b=[s.split()[1] for s in output if s.startswith("bestmove ")]
    need(len(b)==1 and val["pv"] and b[0]==val["pv"][0],"BESTMOVE_INVALID")
    val["bestmove"]=b[0]
    if patched:
        lines=[s for s in output if s.startswith("info string c3x016_p4_root_order ")]
        need(len(lines)==1,"ROOT_SOURCE_EVENT_REPORT_MISSING_OR_MULTIPLE")
        fields=[z.split("=",1) for z in lines[0].split()[3:]]
        audit=dict(fields)
        need(set(audit)=={"mode","guard","root_legal_count","selected_native",
              "selected_pre_index","target_contact","target_pre_index","source_reorder",
              "new_front_native"},"SOURCE_EVENT_REPORT_FIELDS")
        val["root_source"]={k:(v if k=="mode" else int(v)) for k,v in audit.items()}
    if patched:
        raw_events=[z for z in output if z.startswith("info string c3x017_root_event ")]
        events=[]
        for text in raw_events:
            entries=dict(part.split("=",1) for part in text.split()[3:])
            need("seq" in entries and "kind" in entries,"ROOT_EVENT_MALFORMED")
            events.append({k:(v if k=="kind" else int(v)) for k,v in entries.items()})
        need(len(events)>0,"ROOT_TRACE_EMPTY")
        need(len(events)<=2048,"ROOT_TRACE_CAP_EXCEEDED")
        need([x["seq"] for x in events]==list(range(1,len(events)+1)),
             "ROOT_EVENT_SEQUENCE_GAPPED")
        val["passive_root_events"]=events
        val["trace_censored"]=len(events)==2048
    return val

def core(z):return {k:z[k] for k in CORE}

def main():
    a=argparse.ArgumentParser()
    for opt in ("source","original","patched","out"):
        a.add_argument("--"+opt,required=True)
    a.add_argument("--prior-p4",required=True)
    args=a.parse_args()
    inp=Path(args.source).read_bytes();data=json.loads(inp)
    need(data["original_private_12_source_only_selection_sha256"]==FROZEN_SELECTION,"SELECTION_SHA")
    need(data["source_original_broadcast_sha256"]==SOURCE_SHA,"PROVIDER_SHA")
    roots=data["selected"]
    need(len(roots)==12 and [r["id"] for r in roots]==list(range(1,13)),"ROOT_IDS")
    need(Counter(r["geometry_candidate"] for r in roots)==dict.fromkeys(GROUPS,3),"GROUPS")
    need(len({r["fen4"] for r in roots})==12,"FEN_DUPLICATE")
    for r in roots:
        need(native_uci(r["played_legal_move_uci"])==r["native_move"],"MOVE_ENCODING")
        need(len(r["fen4"].split())==4,"FOUR_FIELD_FEN")
    out={"schema":"c3x017-root-order-window-candidate-source-native-12by3by2-passive-v1",
         "original_source_sha256":SOURCE_SHA,
         "preselected_private_cohort_sha256":FROZEN_SELECTION,
         "source_only_strata":dict(Counter(r["geometry_candidate"] for r in roots)),
         "new_native_processes":0,
         "unmodified_original_sham_processes":0,
         "unique_original_game_roots":12,"independent_original_source_games_claim":"inherited_P2_by_GameURL_SHA_12_distinct",
         "all_source_native_no_contact_controls":True,
         "scoped_fen_only_not_true_repetition_history":True,
         "worlds":[]}
    if args.prior_p4:
        prior=json.loads(Path(args.prior_p4).read_text())
        need(prior["new_native_processes"]==72 and len(prior["worlds"])==12,
             "PRIOR_P4_COURT_SIZE")
    else: prior=None
    for r in roots:
        original=play(args.original,r,"O",False);out["unmodified_original_sham_processes"]+=1
        world={"id":r["id"],"candidate_stratum":r["geometry_candidate"],
               "input_game_FEN4_sha256":hashlib.sha256(r["fen4"].encode()).hexdigest(),
               "candidate_move":r["played_legal_move_uci"],"cells":{}}
        for mode in ("O","F","Z"):
            once=play(args.patched,r,mode,True)
            twice=play(args.patched,r,mode,True)
            out["new_native_processes"]+=2
            need(once==twice,f"COLD_REPLAY_ID{r['id']}_{mode}")
            src=once["root_source"]
            need(src["mode"]==mode and src["guard"]==1 and
                 src["selected_native"]==r["native_move"] and
                 src["selected_pre_index"]>=0,"SOURCE_ROOT_GUARD")
            need(src["target_contact"]==int(mode!="Z"),"EXACT_CONTACT")
            need(src["source_reorder"]==int(mode=="F" and src["selected_pre_index"]>0),
                 "REORDER_EXPOSURE")
            if mode=="Z":
                need(src["target_pre_index"]==-1,"SENTINEL_PHYSICALLY_PRESENT")
            if mode=="O":
                need(core(once)==core(original),"PATCHED_SHAM_VS_UNPATCHED_ORIGINAL")
            if mode=="Z":
                need(core(once)==core(world["cells"]["O"]["UCI"]),"ZERO_CONTACT_SHAM_NOT_EQUAL")
            if mode=="F" and src["selected_pre_index"]==0:
                need(core(once)==core(world["cells"]["O"]["UCI"]),"ALREADY_FIRST_EFFECT")
            if prior is not None:
                previous=prior["worlds"][r["id"]-1]["cells"][mode]
                need(core(once)==previous["UCI"],"OBSERVER_CHANGED_ORIGINAL_P4_NATIVE_CORE")
                need(src==previous["root_source"],"OBSERVER_CHANGED_ROOT_ORDER_CONTACT")
            world["cells"][mode]={"UCI":core(once),"root_source":src,
                                  "passive_root_events":once["passive_root_events"],
                                  "trace_censored":once["trace_censored"]}
            print("C3X016_P4_NATIVE",r["id"],r["geometry_candidate"],mode,
                  once["bestmove"],once["score_kind"],once["score_value"],
                  once["nodes"],"reorder",src["source_reorder"],flush=True)
        before=world["cells"]["O"]["UCI"];after=world["cells"]["F"]["UCI"]
        world["contrasts"]={"root_reordered":bool(world["cells"]["F"]["root_source"]["source_reorder"]),
            "categorical_bestmove_changed":before["bestmove"]!=after["bestmove"],
            "score_or_bound_changed":tuple(before[k] for k in ("score_kind","score_value","score_flag"))!=
                                     tuple(after[k] for k in ("score_kind","score_value","score_flag")),
            "nodes_changed":before["nodes"]!=after["nodes"],
            "PV_changed":before["pv"]!=after["pv"]}
        out["worlds"].append(world)
    need(out["new_native_processes"]==72 and out["unmodified_original_sham_processes"]==12,
         "SEARCH_COUNT")
    out["summary"]={k:sum(w["contrasts"][k] for w in out["worlds"]) for k in
       ("root_reordered","categorical_bestmove_changed","score_or_bound_changed","nodes_changed","PV_changed")}
    out["observer_status"]="SOURCE_PASSIVE_WITH_EXACT_P4_O_F_Z_CORE_REGRESSION"
    out["limits"]=[
        "Source-native root move ORDER intervention only; not direct SEE, motif-specific, TT or NNUE causal contact.",
        "Selected geometry labels are possibilities, not tactical or strategic good moves.",
        "Only 12 source game histories, three per stratum, with standalone FEN not full historical repetition state.",
        "Original C3X0.15 C1 42/64 vs null 53/64 accuracy failure preserved.",
        "Source original selected 24 Lichess full SAN games legal but root test lacks full move sequence context.",
        "Outcomes must not select or replace worlds; zero observed effects are retained."]
    Path(args.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("C3X017_ROOT_WINDOW_TRACE_72_NATIVE_ORIGINAL_P4_EXACT_COURT_PASS",
          json.dumps(out["summary"],sort_keys=True),flush=True)
if __name__=="__main__":main()

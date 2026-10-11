#!/usr/bin/env python3
"""P7 original native Stockfish16 basic startpos parity + opt-in TT scalar probes.
Two independent binaries. Two cold engine processes each, depth7, NNUE false.
This is an observational native source microevent witness, not causal TT-FIRST.
"""
import argparse,hashlib,json,os,re,subprocess
from pathlib import Path
SCHEMA="c3x025-P7-original-SF16-native-probe-refresh-moveonly-cold-parity-v1"
TAG="info string c3x025_tt_micro "
INFO=re.compile(r"\b(?:depth|nodes)\s+(\d+)")
def run(engine:str,observer:bool)->dict:
    env=dict(os.environ)
    env["C3X025_P7_TT_MICRO_OBS"]="1" if observer else "0"
    p=subprocess.Popen([engine],stdin=subprocess.PIPE,stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE,env=env,bufsize=1,text=True)
    if p.stdin is None or p.stdout is None:raise RuntimeError("P7_ENGINE_PIPE_MISSING")
    def send(*lines):
        p.stdin.write("\n".join(lines)+"\n");p.stdin.flush()
    def until(marker,maxlines=30000):
        raw=[]
        for _ in range(maxlines):
            line=p.stdout.readline()
            if line=="":raise RuntimeError("P7_ENGINE_EOF_WHILE_WAITING_"+marker)
            line=line.strip()
            raw.append(line)
            if line.startswith(marker) or line==marker:return raw
        raise RuntimeError("P7_NATIVE_UCI_LINE_CENSOR_CAP_"+marker)
    try:
        send("uci")
        until("uciok")
        send("setoption name Threads value 1",
             "setoption name Hash value 16",
             "setoption name MultiPV value 1",
             "setoption name Use NNUE value false",
             "ucinewgame",
             "isready")
        until("readyok")
        send("position startpos","go depth 7")
        raw=until("bestmove ")
        send("quit")
        try:p.wait(timeout=8)
        except subprocess.TimeoutExpired:
            p.kill();p.wait();raise RuntimeError("P7_ENGINE_DID_NOT_CLOSE")
    finally:
        if p.poll() is None:p.kill();p.wait()
    best=[x for x in raw if x.startswith("bestmove ")]
    if len(best)!=1:raise ValueError("P7_NOT_ONE_NATIVE_TERMINAL_BESTMOVE")
    bestmove=best[0].split()[1]
    if not re.fullmatch(r"[a-h][1-8][a-h][1-8][qrbn]?",bestmove):
        raise ValueError("P7_TERMINAL_NATIVE_UCI_ILLEGAL_SHAPE")
    # Exact depth7 root information only, not arbitrary partial depth7 string.
    scores=[]
    for line in raw:
        if not line.startswith("info depth 7 ") or " nodes " not in line:continue
        mt=re.search(r"\bnodes\s+(\d+)\b",line)
        if mt:scores.append(int(mt.group(1)))
    if not scores:raise ValueError("P7_NO_FIXED_DEPTH7_ORIGINAL_SEARCH_NODES")
    trace=[]
    for line in raw:
        if line.startswith(TAG):
            if not observer:raise ValueError("P7_OPTOUT_PRODUCED_NATIVE_MICRO_TAG")
            fields={}
            for pair in line[len(TAG):].split():
                if "=" not in pair:raise ValueError("P7_INVALID_NATIVE_INFO_FIELD")
                a,b=pair.split("=",1)
                fields[a]=b
            kind=fields.get("kind")
            if kind=="probe_refresh":
                if set(fields)!={"kind","found","prev_gen","new_gen","current_gen","seq"}:
                    raise ValueError("P7_MISSING_OR_EXCESS_PROBE_SOURCE_FIELDS")
                fields={k:(int(v) if k!="kind" else v) for k,v in fields.items()}
                if fields["new_gen"]!=(fields["current_gen"]|(fields["prev_gen"]&7)):
                    raise ValueError("P7_NATIVE_PROBE_REFRESH_FORMULA_INCONSISTENT")
                if fields["found"] not in (0,1):raise ValueError("P7_BAD_NATIVE_TT_FOUND")
            elif kind=="move_only_save":
                if set(fields)!={"kind","move_changed","score_fields_changed","seq"}:
                    raise ValueError("P7_INVALID_NATIVE_SAVE_SOURCE_FIELDS")
                fields={k:(int(v) if k!="kind" else v) for k,v in fields.items()}
                if (fields["move_changed"],fields["score_fields_changed"])!=(1,0):
                    raise ValueError("P7_ORIGINAL_NATIVE_MOVE_ONLY_FIELD_GUARD_WRONG")
            else:raise ValueError("P7_UNRECOGNIZED_SOURCE_OBSERVER_TAG")
            trace.append(fields)
    probes=[x for x in trace if x["kind"]=="probe_refresh"]
    moves=[x for x in trace if x["kind"]=="move_only_save"]
    if len(probes)>8 or len(moves)>8:
        raise ValueError("P7_BOUNDED_NATIVE_SOURCE_EVENT_BUDGET_OVERFLOW")
    for xs in (probes,moves):
        if [x["seq"] for x in xs]!=list(range(1,len(xs)+1)):
            raise ValueError("P7_NATIVE_SOURCE_EVENT_SEQUENCE_WRONG")
    return {"bestmove":bestmove,"depth":7,"nodes":scores[-1],
            "probe_refresh_events_bounded":len(probes),
            "move_only_save_events_bounded":len(moves),
            "probe_refresh_native_observer":probes,
            "move_only_native_observer":moves,
            "native_events_are_bounded_prefix_not_whole_search":True}
def court(original:str,patched:str,manifest:dict)->dict:
    if manifest["schema"]!="c3x025-P7-read-only-optin-native-TT-source-probe-and-move-provenance-overlay-v1" or not manifest["source_patch_reversible_original_byte_equal"]:
        raise ValueError("P7_OBSERVER_NOT_REVERSED_FROM_ORIGINAL_PINNED_SOURCE")
    ref=[run(original,False) for _ in range(2)]
    active=[run(patched,True) for _ in range(2)]
    inactive=run(patched,False)
    def controls(x):return (x["bestmove"],x["depth"],x["nodes"])
    if len({controls(x) for x in ref+active+[inactive]})!=1:
        raise ValueError("P7_OBSERVER_CHANGED_PINNED_NATIVE_COLD_BESTMOVE_OR_NODES")
    if any(x["probe_refresh_events_bounded"]!=0 or x["move_only_save_events_bounded"]!=0
           for x in ref+[inactive]):
        raise ValueError("P7_ORIGINAL_OR_DISABLED_CXX_HAS_OBSERVER_TAG")
    if active[0]!=active[1]:
        raise ValueError("P7_ACTIVE_NATIVE_MICROEVENT_COLD_REPEAT_DRIFT")
    if active[0]["probe_refresh_events_bounded"]==0:
        raise ValueError("P7_NATIVE_PINNED_PROBE_REFRESH_NOT_ACTUALLY_OBSERVED")
    return {"schema":SCHEMA,
        "pin_SF16_original_git_commit":"68e1e9b3811e16cad014b590d7443b9063b3eb52",
        "original_upstream_tt_cpp_sha256":manifest["official_Stockfish16_tt_cpp_original_SHA256"],
        "reversible_observer_source_sha256":manifest["modified_compilation_source_SHA256"],
        "source_patch_exact_byte_restoration_verified":True,
        "starting_chess_position":"PUBLIC_STANDARD_STARTPOS_ONLY",
        "original_unmodified_engine_cold_runs":2,
        "native_observer_on_cold_runs":2,
        "native_observer_off_negative_controls":1,
        "native_source_original_and_observer_bestmove_nodes_depth_parity":True,
        "identical_original_terminal_bestmove":ref[0]["bestmove"],
        "identical_original_terminal_depth":ref[0]["depth"],
        "identical_original_terminal_nodes":ref[0]["nodes"],
        "native_observer_probe_refresh_bounded_source_count":active[0]["probe_refresh_events_bounded"],
        "native_observer_probe_empty_vs_found":{
            "found":sum(x["found"]==1 for x in active[0]["probe_refresh_native_observer"]),
            "empty":sum(x["found"]==0 for x in active[0]["probe_refresh_native_observer"])},
        "native_move_only_save_bounded_source_count":active[0]["move_only_save_events_bounded"],
        "native_move_only_observer_status":"ACTUAL_SOURCE_BRANCH_EXECUTED" if active[0]["move_only_save_events_bounded"] else
            "NOT_SEEN_WITHIN_BOUNDED_OBSERVER_NOT_PROVEN_ABSENT",
        "native_observed_scalar_trace":active[0]["probe_refresh_native_observer"]+
                                         active[0]["move_only_native_observer"],
        "original_native_TT_semantic_score_consumption_identified":False,
        "natural_TT_SEE_mediation_proven":False,
        "original_July256_chess_model_M5_predictive_gain_measured":False,
        "native_performance_speed_or_Elo_gain_claimed":False,
        "source_licenses":"Original official Stockfish16 GPLv3, separate Lichess July original PGNs not downloaded or used, no C++ patch/binary redistributed"}
def main():
    p=argparse.ArgumentParser()
    for k in ("original","observer","manifest","out"):p.add_argument("--"+k,required=True)
    a=p.parse_args()
    m=json.loads(Path(a.manifest).read_text())
    r=court(a.original,a.observer,m)
    out=Path(a.out);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(r,indent=2,sort_keys=True)+"\n")
    print("C3X025_P7_NATIVE_SOURCE_COLD_TT_MICROEVENT_PARITY",
          {k:v for k,v in r.items() if k in (
              "native_source_original_and_observer_bestmove_nodes_depth_parity",
              "identical_original_terminal_bestmove","identical_original_terminal_nodes",
              "native_observer_probe_refresh_bounded_source_count",
              "native_move_only_save_bounded_source_count",
              "native_move_only_observer_status")},flush=True)
    print("C3X025_P7_NATIVE_SOURCE_PARITY_JSON_SHA256",
          hashlib.sha256(out.read_bytes()).hexdigest(),flush=True)
if __name__=="__main__":main()

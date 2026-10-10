#!/usr/bin/env python3
"""C3X018 #6/#8 exploratory native physical TT lineage and selective factorial court.

Pre-existing case selection (#6/#8) and root-order treatments are frozen.
TT event selection from this tranche is exploratory, NOT a pre-registered mediator.
"""
import argparse
import hashlib
import json
import os
import re
import subprocess
from pathlib import Path

FIELDS = ("bestmove", "score_kind", "score_value", "score_flag", "nodes", "pv")
FOCAL = (6, 8)
SOURCE_SELECTION = "08bf2179e141ba6a862314660298fa90fa61c3d377e46accc07bd4c5d9cacae2"

def need(test, label):
    if not test:
        raise RuntimeError("C3X018_PHYSICAL_COURT_" + label)

def parse_fields(line):
    return dict(p.split("=", 1) for p in line.split()[3:] if "=" in p)

def core(raw, search_depth=12):
    rows = []
    for line in raw:
        if line.startswith("info depth "+str(search_depth)+" ") and " pv " in line:
            value = re.search(r"\bscore (cp|mate) (-?\d+)(?: (lowerbound|upperbound))?", line)
            nodes = re.search(r"\bnodes (\d+)", line)
            if value and nodes:
                rows.append(dict(score_kind=value.group(1),
                    score_value=int(value.group(2)), score_flag=value.group(3) or "exact_reported",
                    nodes=int(nodes.group(1)), pv=line.split(" pv ",1)[1].split()[:16]))
    need(rows, "MISSING_DEPTH_SCORE_"+str(search_depth))
    best = [x.split()[1] for x in raw if x.startswith("bestmove ")]
    need(len(best)==1 and best[0]==rows[-1]["pv"][0], "MISSING_BESTMOVE")
    return {"bestmove":best[0],**rows[-1]}

def play(engine, world, p4_mode, lineage_mode=None, target=None, writer_budget=None, rescue_attempt=None, discovery=False, history=False, fen_clocks=None, search_depth=12, draw_mode=None, tt_reader_filters=None, probe_watch=None, p1_writer=None, native_use_watch=None, passive_second_call=None, root_return=None, multi_state=None, root_searchmoves=None):
    need(isinstance(search_depth,int) and 1<=search_depth<=32,"INVALID_SEARCH_DEPTH")
    if root_searchmoves is not None:
        need(isinstance(root_searchmoves,(list,tuple)) and
             1<=len(root_searchmoves)<=16 and
             all(isinstance(m,str) and
                 re.fullmatch(r"[a-h][1-8][a-h][1-8][qrbn]?",m)
                 for m in root_searchmoves) and
             len(set(root_searchmoves))==len(root_searchmoves),
             "ROOT_SEARCHMOVES_STRICT_UNIQUE_UCI")
    go_cmd="go depth "+str(search_depth)
    if root_searchmoves is not None:
        go_cmd+=" searchmoves "+" ".join(root_searchmoves)
    env = dict(os.environ)
    return_env={
      "depth":"C3X019_RETURN_DEPTH",
      "root_call":"C3X019_RETURN_ROOT_CALL",
      "trial":"C3X019_RETURN_TRIAL",
      "move":"C3X019_RETURN_MOVE",
      "index":"C3X019_RETURN_INDEX",
      "alpha":"C3X019_RETURN_ALPHA",
      "beta":"C3X019_RETURN_BETA",
      "expected":"C3X019_RETURN_EXPECTED",
      "replacement":"C3X019_RETURN_REPLACEMENT",
      "mode":"C3X019_RETURN_REPAIR_MODE"}
    for key in return_env.values():
        env.pop(key,None)
    if root_return is not None:
        need(isinstance(root_return,dict) and set(root_return)==set(return_env),
             "ROOT_RETURN_STRICT_SCHEMA")
        need(root_return["mode"] in ("OBS","REPAIR"),
             "ROOT_RETURN_INVALID_MODE")
        for field in return_env:
            if field=="mode":
                continue
            need(isinstance(root_return[field],int),
                 "ROOT_RETURN_INVALID_"+field)
            env[return_env[field]]=str(root_return[field])
        need(1<=root_return["depth"]<=search_depth
             and 1<=root_return["root_call"]<=2000
             and 1<=root_return["trial"]<=100
             and 1<=root_return["index"]<=256
             and 1<=root_return["move"]<=65535
             and root_return["alpha"]<root_return["beta"]
             and -32000<root_return["replacement"]<32000
             and -32000<root_return["expected"]<32000,
             "ROOT_RETURN_BOUNDS")
        env[return_env["mode"]]=root_return["mode"]
    c3x020_second = {
        "depth":"C3X020_SECOND_DEPTH", "root_call":"C3X020_SECOND_ROOT_CALL",
        "trial":"C3X020_SECOND_TRIAL", "move":"C3X020_SECOND_MOVE",
        "index":"C3X020_SECOND_INDEX", "alpha":"C3X020_SECOND_ALPHA",
        "beta":"C3X020_SECOND_BETA", "expected":"C3X020_SECOND_EXPECTED",
        "target":"C3X020_SECOND_TARGET", "mode":"C3X020_SECOND_MODE"}
    c3x020_boundary = {
        "depth":"C3X020_BOUNDARY_DEPTH", "move":"C3X020_BOUNDARY_MOVE",
        "expect_score":"C3X020_BOUNDARY_EXPECT_SCORE",
        "expect_average":"C3X020_BOUNDARY_EXPECT_AVERAGE",
        "target_score":"C3X020_BOUNDARY_TARGET_SCORE",
        "target_average":"C3X020_BOUNDARY_TARGET_AVERAGE",
        "mode":"C3X020_BOUNDARY_MODE"}
    for key in (*c3x020_second.values(), *c3x020_boundary.values()):
        env.pop(key,None)
    if multi_state is not None:
        need(isinstance(multi_state,dict)
             and set(multi_state)=={"second","boundary"}, "C3X020_STRICT_TOP_LEVEL")
        for which,mapping,modes in (
            ("second",c3x020_second,("OBS","REPAIR")),
            ("boundary",c3x020_boundary,("O","A","S","B"))):
            values=multi_state[which]
            if values is None:
                continue
            need(isinstance(values,dict) and set(values)==set(mapping),
                 "C3X020_STRICT_"+which)
            need(values["mode"] in modes, "C3X020_INVALID_MODE_"+which)
            need(all(type(v) is int for k,v in values.items() if k!="mode"),
                 "C3X020_INVALID_TYPE_"+which)
            need(1 <= values["depth"] <= search_depth and
                 0 <= values["move"] <= 65535, "C3X020_BOUNDS_"+which)
            for k in values:
                if k=="mode":
                    continue
                if k in ("expected","target","expect_score","expect_average",
                         "target_score","target_average"):
                    need(-32001<=values[k]<=32001,"C3X020_VALUE_RANGE_"+k)
            if which=="second":
                need(values["root_call"]>0 and values["trial"]>0
                     and values["index"]>0 and values["alpha"]<values["beta"],
                     "C3X020_SECOND_COORDINATES")
            for k,v in values.items():
                env[mapping[k]]=str(v)
    for key in ("C3X019_NATIVE_USE_WATCH_KEY64","C3X019_NATIVE_USE_WATCH_ROOT_CALL","C3X019_PASSIVE_SECOND_ROOT_CALL"):
        env.pop(key,None)
    if native_use_watch is not None:
        need(isinstance(native_use_watch,dict) and set(native_use_watch)=={"key64","root_call"},
             "INVALID_C3X019_NATIVE_USE_WATCH")
        need(all(isinstance(v,int) and v>0 for v in native_use_watch.values()),
             "INVALID_NATIVE_USE_WATCH_PARAMETER")
        env["C3X019_NATIVE_USE_WATCH_KEY64"]=str(native_use_watch["key64"])
        env["C3X019_NATIVE_USE_WATCH_ROOT_CALL"]=str(native_use_watch["root_call"])
    if passive_second_call is not None:
        need(isinstance(passive_second_call,int) and passive_second_call>0,
             "INVALID_C3X019_PASSIVE_SECOND_CALL")
        env["C3X019_PASSIVE_SECOND_ROOT_CALL"]=str(passive_second_call)
    for key in ("C3X018_P1_WRITER_KEY64","C3X018_P1_WRITER_SLOT",
                "C3X018_P1_WRITER_EPOCH","C3X018_P1_FIRST_CALL",
                "C3X018_P1_LAST_CALL",
                "C3X018_P1_WRITE_POLICY"):
        env.pop(key,None)
    if p1_writer is not None:
        need(isinstance(p1_writer,dict) and
             set(p1_writer)=={"key64","slot","epoch","first_call","last_call","policy"},
             "INVALID_P1_WRITER_EXACT_SCHEMA")
        need(p1_writer["policy"] in ("NONE","SKIP","REINSTATE","BYTES_ONLY","SHADOW_ONLY"),
             "P1_INVALID_WRITE_POLICY")
        for name in ("key64","slot","epoch","first_call","last_call"):
            need(isinstance(p1_writer[name],int) and p1_writer[name]>=0,
                 "P1_WRITER_BAD_NUMBER")
        need(p1_writer["first_call"]>0 and p1_writer["first_call"]<p1_writer["last_call"]
             and p1_writer["epoch"]>0
             and 0<=p1_writer["slot"]<3,"P1_WRITER_SOURCE_CONSTRAINT")
        env.update(C3X018_P1_WRITER_KEY64=str(p1_writer["key64"]),
                   C3X018_P1_WRITER_SLOT=str(p1_writer["slot"]),
                   C3X018_P1_WRITER_EPOCH=str(p1_writer["epoch"]),
                   C3X018_P1_FIRST_CALL=str(p1_writer["first_call"]),
                   C3X018_P1_LAST_CALL=str(p1_writer["last_call"]),
                   C3X018_P1_WRITE_POLICY=p1_writer["policy"])
    env.pop("C3X018_PROBE_WATCH_KEY64",None)
    env.pop("C3X018_PROBE_WATCH_ROOT_CALL",None)
    if probe_watch is not None:
        need(isinstance(probe_watch,dict) and set(probe_watch)=={"key64","root_call"},"INVALID_PROBE_WATCH_FIELDS")
        need(all(isinstance(v,int) and v>0 for v in probe_watch.values()),"INVALID_PROBE_WATCH_VALUES")
        env["C3X018_PROBE_WATCH_KEY64"]=str(probe_watch["key64"])
        env["C3X018_PROBE_WATCH_ROOT_CALL"]=str(probe_watch["root_call"])
    for key in ("C3X018_FILTER_MIN_WRITE_AGE","C3X018_FILTER_ROOT_CALL","C3X018_FILTER_ROOT_MOVE","C3X018_FILTER_PLY","C3X018_FILTER_RAW_BOUND","C3X018_FILTER_CALL_MASK_9_13","C3X018_FILTER_PAIR_CALL_A","C3X018_FILTER_PAIR_CALL_B","C3X018_FILTER_MAX_PLY","C3X018_FILTER_WINDOW_WIDTH_MAX"):
        env.pop(key,None)
    if tt_reader_filters is not None:
        need(isinstance(tt_reader_filters,dict) and tt_reader_filters,"EMPTY_READER_EVENT_FILTER")
        for key,value in tt_reader_filters.items():
            need(key in ("C3X018_FILTER_MIN_WRITE_AGE","C3X018_FILTER_ROOT_CALL","C3X018_FILTER_ROOT_MOVE","C3X018_FILTER_PLY","C3X018_FILTER_RAW_BOUND","C3X018_FILTER_CALL_MASK_9_13","C3X018_FILTER_PAIR_CALL_A","C3X018_FILTER_PAIR_CALL_B","C3X018_FILTER_MAX_PLY","C3X018_FILTER_WINDOW_WIDTH_MAX"),"INVALID_READER_EVENT_FILTER")
            need(isinstance(value,int) and value>=0,"INVALID_READER_FILTER_VALUE")
            env[key]=str(value)
    env.pop("C3X018_EXACT_DRAW_SUPPRESS",None)
    if draw_mode is not None:
        need(draw_mode in ("G","D","GD"),"INVALID_DRAW_SUPPRESSION_MODE")
        env["C3X018_EXACT_DRAW_SUPPRESS"]=draw_mode
    for name in ("C3X018_TT_MODE", "C3X018_TT_TARGET_KEY64",
                 "C3X018_TT_TARGET_SLOT", "C3X018_TT_TARGET_EPOCH",
                 "C3X018_TT_LOG_WRITES", "C3X018_TT_WRITER_BLOCK_BUDGET",
                 "C3X018_TT_RESCUE_ATTEMPT", "C3X018_TT_DISCOVERY"):
        env.pop(name,None)
    if lineage_mode is not None:
        env.update(C3X016_P4_MODE=p4_mode,C3X016_P4_FEN4=world["fen4"],
                   C3X016_P4_PLAYED_NATIVE=str(world["native_move"]),
                   C3X018_TT_MODE=lineage_mode)
        if discovery:
            env["C3X018_TT_DISCOVERY"]="1"
        if writer_budget is not None:
            need(isinstance(writer_budget,int) and 0<=writer_budget<=256,"INVALID_WRITER_BUDGET")
            env["C3X018_TT_WRITER_BLOCK_BUDGET"]=str(writer_budget)
        if rescue_attempt is not None:
            need(isinstance(rescue_attempt,int) and 1<=rescue_attempt<=256,
                 "INVALID_RESCUE_ATTEMPT")
            env["C3X018_TT_RESCUE_ATTEMPT"]=str(rescue_attempt)
        if target:
            env.update(C3X018_TT_TARGET_KEY64=str(target["key64"]),
                       C3X018_TT_TARGET_SLOT=str(target["slot"]),
                       C3X018_TT_TARGET_EPOCH=str(target["epoch"]))
    lines=[]
    with subprocess.Popen([engine], stdin=subprocess.PIPE,
          stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
          env=env,text=True,bufsize=1) as proc:
        def send(*commands):
            proc.stdin.write("\n".join(commands)+"\n");proc.stdin.flush()
        def receive(marker,cap):
            for _ in range(cap):
                line=proc.stdout.readline()
                need(bool(line),"PREMATURE_EOF_"+marker)
                lines.append(line.rstrip("\n"))
                if line.startswith(marker):return
            raise RuntimeError("C3X018_UCI_LINE_CAP_"+marker)
        send("uci");receive("uciok",100)
        send("setoption name Threads value 1",
             "setoption name Hash value 16",
             "setoption name MultiPV value 1",
             "setoption name Use NNUE value false",
             "ucinewgame","isready")
        receive("readyok",100)
        if history:
            original_moves=world["full_original_mainline_uci"][:world["source_ply_before_original_move"]]
            need(original_moves and world["source_ply_before_original_move"]==len(original_moves),
                 "INCOMPLETE_ORIGINAL_GAME_HISTORY")
            send("position startpos moves "+" ".join(original_moves),go_cmd)
        elif fen_clocks is not None:
            half,full=fen_clocks
            need(isinstance(half,int) and half>=0 and isinstance(full,int) and full>=1,
                 "INVALID_SOURCE_FEN_CLOCKS")
            send("position fen "+world["fen4"]+" "+str(half)+" "+str(full),go_cmd)
        else:
            send("position fen "+world["fen4"]+" 0 1",go_cmd)
        receive("bestmove ",120000)
        send("quit")
        need(proc.wait(timeout=50)==0,"NATIVE_NONZERO_EXIT")
    result=core(lines,search_depth)
    if lineage_mode is None: return {"UCI":result}
    events=[]
    for line in lines:
        if line.startswith("info string c3x018_lineage "):
            evt=parse_fields(line)
            events.append({k:(v if k in ("kind","site") else int(v)) for k,v in evt.items()})
    need(events, "NO_LINEAGE_EVENTS")
    need(not any(x["kind"]=="trace_censored" for x in events), "TRACE_CENSORED")
    fingerprints=[]
    for line in lines:
        if line.startswith("info string c3x018_write_fingerprint "):
            fingerprints.append({k:int(v) for k,v in parse_fields(line).items()})
    witnesses=[]
    for line in lines:
        if line.startswith("info string c3x018_value_witness "):
            fields=parse_fields(line)
            witnesses.append({k:(v if k in ("kind","site") else int(v)) for k,v in fields.items()})
    p0_save_events=[]
    for line in lines:
        if line.startswith("info string c3x018_p1_save "):
            fields=parse_fields(line)
            p0_save_events.append({k:(v if k=="kind" else int(v)) for k,v in fields.items()})
    native_tt_value_uses=[]
    for line in lines:
        if line.startswith("info string c3x019_native_use "):
            fields=parse_fields(line)
            native_tt_value_uses.append({k:(v if k in ("kind","site") else int(v)) for k,v in fields.items()})
    watched_tt_probes=[]
    for line in lines:
        if line.startswith("info string c3x018_jan_probe_watch "):
            fields=parse_fields(line)
            watched_tt_probes.append({k:(v if k in ("kind","site") else int(v)) for k,v in fields.items()})
    draw_gate_contacts=[]
    for line in lines:
        if line.startswith("info string c3x018_exact_draw_intervention "):
            fields=parse_fields(line)
            draw_gate_contacts.append({k:(v if k=="site" else int(v)) for k,v in fields.items()})
    draw_probes=[]
    for line in lines:
        if line.startswith("info string c3x018_draw_probe "):
            fields=parse_fields(line)
            draw_probes.append({k:(v if k in ("type","site") else int(v)) for k,v in fields.items()})
    root_return_events=[]
    for line in lines:
        if line.startswith("info string c3x019_return_repair "):
            fields=parse_fields(line)
            root_return_events.append({k:(v if k=="kind" else int(v))
                                       for k,v in fields.items()})
    second_return_events=[]
    boundary_state_events=[]
    for line in lines:
        if line.startswith("info string c3x020_second "):
            fields=parse_fields(line)
            second_return_events.append({
                k:(v if k=="kind" else int(v)) for k,v in fields.items()})
        if line.startswith("info string c3x020_boundary "):
            fields=parse_fields(line)
            boundary_state_events.append({
                k:(v if k in ("kind","mode") else int(v)) for k,v in fields.items()})
    root_events=[]
    for line in lines:
        if line.startswith("info string c3x017_root_event "):
            raw=parse_fields(line)
            root_events.append({k:(v if k=="kind" else int(v)) for k,v in raw.items()})
    roots=[parse_fields(x) for x in lines if x.startswith("info string c3x016_p4_root_order ")]
    need(len(roots)==1 and roots[0]["mode"]==p4_mode,"P4_ROOT_CONTACT_MISSING")
    return {
       "UCI":result,
       "lineage_summary":{
           "records":len(events),
           "consumer_reached":sum(e["kind"]=="consumer_reached" for e in events),
           "writer_block":sum(e["kind"]=="writer_block" for e in events),
           "reader_block":sum(e["kind"]=="reader_block" for e in events),
           "writer_rescue":sum(e["kind"]=="writer_rescue" for e in events),
           "exact_key_consumers":sum(e["kind"]=="consumer_reached" and
                                      e.get("key_match")==1 for e in events),
           "key16_or_unknown_consumers":sum(e["kind"]=="consumer_reached" and
                                      e.get("key_match")==0 for e in events)
       },
       "consumer_records":[e for e in events if e["kind"]=="consumer_reached"],
       "blocks":[e for e in events if e["kind"] in ("writer_block","reader_block")],
       "rescues":[e for e in events if e["kind"]=="writer_rescue"],
       "write_fingerprints":fingerprints,
       "payload_witnesses":witnesses,
       "draw_probes":draw_probes,
       "draw_gate_contacts":draw_gate_contacts,
       "watched_tt_probes":watched_tt_probes,
       "native_tt_value_uses":native_tt_value_uses,
       "native_tt_source_allows":[e for e in events if e["kind"]=="reader_native_allow"],
       "p0_save_events":p0_save_events,
       "root_events":root_events,
       "root_return_events":root_return_events,
       "second_return_events":second_return_events,
       "boundary_state_events":boundary_state_events,
       "root_contact":roots[0]}

def stable(t):
    return json.dumps(t,sort_keys=True,separators=(",",":"))

def select_candidate(O,F):
    # Predeclared algorithm, determined without observing ANY treatment output.
    o={(e["key64"],e["slot"],e["epoch"]) for e in O
        if e["kind"]=="consumer_reached" and e["key_match"]==1 and e["epoch"]>0}
    good=[e for e in F if e["kind"]=="consumer_reached" and
          e["key_match"]==1 and e["epoch"]>0 and 0<=e["slot"]<3]
    novel=[e for e in good if (e["key64"],e["slot"],e["epoch"]) not in o]
    pool=novel if novel else good
    if not pool:return None, "NO_EXACT_KEY_WRITER_CONSUMER"
    first=pool[0]
    return {k:first[k] for k in ("key64","slot","epoch")}, \
           ("FIRST_F_UNIQUE_EXACT_KEY_CONSUMER" if novel
            else "FIRST_F_EXACT_KEY_CONSUMER_NO_UNIQUE_CONTRAST")

def main():
    p=argparse.ArgumentParser()
    for field in ("cohort","prior","original","patched","out"):
        p.add_argument("--"+field,required=True)
    args=p.parse_args()
    data=json.loads(Path(args.cohort).read_text())
    need(data["original_private_12_source_only_selection_sha256"]==SOURCE_SELECTION,
         "FROZEN_SELECTION_MISMATCH")
    old=json.loads(Path(args.prior).read_text())
    need(old["new_native_processes"]==72,"PRIOR_NATIVE_SIZE")
    result={"schema":"c3x018-natural-physical-TT-lineage-6-8-exploratory-factorial-v1",
            "prior_sha256":hashlib.sha256(Path(args.prior).read_bytes()).hexdigest(),
            "cohort_sha256":hashlib.sha256(Path(args.cohort).read_bytes()).hexdigest(),
            "source_only":True,"cases":[],
            "scope":"actual main/qsearch TT cutoff branch, not other TT uses",
            "status":"NATIVE_EXPLORATORY_NOT_UNIQUE_CAUSAL_MEDIATION"}
    for case_id in FOCAL:
        world=data["selected"][case_id-1]
        need(world["id"]==case_id,"FOCAL_CASE_INDEX")
        historical=old["worlds"][case_id-1]["cells"]
        original=play(args.original,world,"O")
        need(original["UCI"]==historical["O"]["UCI"],"UNMODIFIED_P4_SHAM")
        controls={}
        for arm in ("O","F","Z"):
            a=play(args.patched,world,arm,"OBS")
            b=play(args.patched,world,arm,"OBS")
            need(a==b,"COLD_OBSERVER_REPLAY_ID_"+str(case_id)+"_"+arm)
            need(a["UCI"]==historical[arm]["UCI"],"P4_NONINTERFERENCE_"+str(case_id)+"_"+arm)
            controls[arm]=a
        need(controls["O"]["UCI"]==controls["Z"]["UCI"],"NO_CONTACT_NOT_EQUAL")
        need(controls["O"]["UCI"]["bestmove"]!=controls["F"]["UCI"]["bestmove"],
             "HISTORICAL_FLIP_NOT_REPRODUCED")
        target,basis=select_candidate(controls["O"]["consumer_records"],
                                      controls["F"]["consumer_records"])
        decoy={"key64":18446744073709551615,"slot":0,"epoch":1}
        decoys={}
        for decoy_mode in ("W","R"):
            negative=play(args.patched,world,"F",decoy_mode,decoy)
            replay=play(args.patched,world,"F",decoy_mode,decoy)
            need(negative==replay,"DECOY_COLD_REPLAY_"+str(case_id)+"_"+decoy_mode)
            need(negative["UCI"]==controls["F"]["UCI"],
                 "DECOY_CHANGED_FINAL_OUTPUT_"+str(case_id)+"_"+decoy_mode)
            need(negative["lineage_summary"]["writer_block"]==0 and
                 negative["lineage_summary"]["reader_block"]==0,
                 "DECOY_OPERATOR_FIRED_"+str(case_id)+"_"+decoy_mode)
            decoys[decoy_mode]={
                "UCI":negative["UCI"],
                "writer_block":0,"reader_block":0,"contact":"NONE"}
        row={"id":case_id,
             "prior_output":{arm:controls[arm]["UCI"] for arm in controls},
             "observer":{arm:controls[arm]["lineage_summary"] for arm in controls},
             "target_selection":basis,"target":target,
             "decoy_no_contact":decoys,
             "target_design":"EXPLORATORY_F_ONLY_SELECTION_NOT_INDEPENDENT_PREREGISTRATION",
             "interventions":{}}
        if target:
            for treatment in ("W","R","WR"):
                a=play(args.patched,world,"F",treatment,target)
                b=play(args.patched,world,"F",treatment,target)
                need(a==b,"COLD_FACTORIAL_"+str(case_id)+"_"+treatment)
                expected_w=treatment in ("W","WR")
                expected_r=treatment in ("R","WR")
                w=a["lineage_summary"]["writer_block"]
                r=a["lineage_summary"]["reader_block"]
                row["interventions"][treatment]={
                    "UCI":a["UCI"],"observer":a["lineage_summary"],
                    "writer_contact":w,"reader_contact":r,
                    "relative_to_F":{
                      "bestmove_changed":a["UCI"]["bestmove"]!=controls["F"]["UCI"]["bestmove"],
                      "score_or_bound_changed":tuple(a["UCI"][k] for k in ("score_kind","score_value","score_flag"))!=tuple(
                          controls["F"]["UCI"][k] for k in ("score_kind","score_value","score_flag")),
                      "nodes_changed":a["UCI"]["nodes"]!=controls["F"]["UCI"]["nodes"]},
                    "arm_contact_status":("CONTACT" if ((not expected_w or w>0) and
                                        (not expected_r or r>0)) else "PARTIAL_OR_NOT_FIRED"),
                    "sample_block_events":a["blocks"][:5]}
                print("C3X018",case_id,treatment,"contact",w,r,
                      "bestmove",a["UCI"]["bestmove"],flush=True)
        result["cases"].append(row)
        print("C3X018_SOURCE_LINEAGE",case_id,"target",basis,
              "observed_consumers",row["observer"]["F"]["consumer_reached"],flush=True)
    result["limitations"]=[
        "Intervention key/slot/epoch selected on treated F observation, not on independent cohort",
        "Slot epoch is per-slot accepted payload-write ordinal after native TT clear",
        "Writer source ablation may also prevent move16 update; not an isolated score mediator",
        "W and R blocking do not test unique natural mediation; other TT uses remain active",
        "Exactly one writer suppression; subsequent writes may reuse the vacant slot epoch",
        "Writer suppression may alter future epoch numbering; missing contact is not an effect",
        "Only cases 6 and 8, standalone FEN, SF16 single-thread depth12",
        "Censor gate rejects missing full lineage event buffer",
        "No source-exact rescue; no human chess tactical proof"
    ]
    Path(args.out).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("C3X018_LINEAGE_FACTORIAL_NATIVE_EVIDENCE_MATERIALIZED",flush=True)

if __name__=="__main__":
    main()

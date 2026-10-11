#!/usr/bin/env python3
"""P11 independently capped native actual TT-return, SEE-guard, root-update events.
Same actual SF16 process, shared source serial; observed co-occurrence DOES NOT
establish one causal parent→child→root path; held out as explicit HOLD.
"""
import argparse,hashlib,json,os,re,subprocess
from collections import Counter
from pathlib import Path
SCHEMA="c3x025-P12-native-actual-caller-parent-and-TT-return-frame-unwind-with-source-SEE-root-status-v1"
P11="info string c3x025_p11 "
P9="info string c3x025_p9_root "
CLASSES={"TT_MAIN_RETURN":"CUTOFF","TT_Q_RETURN":"CUTOFF",
         "SEE_QUIET_GUARD":"SEE","SEE_QSEARCH_GUARD":"SEE",
         "ROOT_SCORE_UPDATE":"ROOT"}
def run(binary,enabled):
    env={**os.environ,"C3X025_P8_TT_FIELDS":"1" if enabled else "0"}
    p=subprocess.Popen([binary],stdin=subprocess.PIPE,stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE,text=True,bufsize=1,env=env)
    if p.stdin is None or p.stdout is None:raise ValueError("P11_UCI_PIPES_MISSING")
    def send(*commands):
        p.stdin.write("\n".join(commands)+"\n");p.stdin.flush()
    def consume(terminal,maxlines=40000):
        data=[]
        for _ in range(maxlines):
            x=p.stdout.readline()
            if not x:raise RuntimeError("P11_ENGINE_EOF_OR_CRASH_"+terminal)
            x=x.strip();data.append(x)
            if x==terminal or x.startswith(terminal):return data
        raise RuntimeError("P11_NATIVE_SOURCE_UCI_OUTPUT_NOT_FINITE")
    try:
        send("uci");consume("uciok")
        send("setoption name Threads value 1","setoption name Hash value 16",
             "setoption name MultiPV value 1","setoption name Use NNUE value false",
             "ucinewgame","isready")
        consume("readyok")
        send("position startpos","go depth 7")
        output=consume("bestmove ")
        send("quit")
        try:p.wait(timeout=8)
        except subprocess.TimeoutExpired:
            p.kill();p.wait();raise RuntimeError("P11_NATIVE_PROCESS_DID_NOT_TERMINATE")
    finally:
        if p.poll() is None:p.kill();p.wait()
    best=[l.split()[1] for l in output if l.startswith("bestmove ")]
    if len(best)!=1 or not re.fullmatch("[a-h][1-8][a-h][1-8][qrbn]?",best[0]):
        raise ValueError("P11_NO_SINGLE_LEGAL_SHAPED_NATIVE_BESTMOVE")
    depth=[l for l in output if l.startswith("info depth 7 ") and " nodes " in l]
    if not depth:raise ValueError("P11_SOURCE_DEPTH_SEVEN_NODES_MISSING")
    n=int(re.search(r"\bnodes\s+(\d+)\b",depth[-1]).group(1))
    source=[];by_class=Counter();caps=Counter();frames=[]
    root=[]
    for line in output:
        if line.startswith("info string c3x025_p12 "):
            if not enabled:raise ValueError("P12_NATIVE_OBSERVER_DISABLED_BUT_FRAME_LOGGED")
            fields={}
            for part in line[len("info string c3x025_p12 "):].split():
                if "=" not in part:raise ValueError("P12_MALFORMED_NATIVE_FRAME_TAG")
                k,v=part.split("=",1)
                if k in fields:raise ValueError("P12_DUPLICATED_NATIVE_FRAME_FIELD")
                fields[k]=v
            if fields.get("kind") not in ("SOURCE_EVENT","TT_RETURN_FRAME_EXIT","RETURN_CENSORED"):
                raise ValueError("P12_NATIVE_SOURCE_FRAME_KIND_UNKNOWN")
            frames.append(fields)
        if line.startswith(P9):root.append(line)
        if not line.startswith(P11):continue
        if not enabled:raise ValueError("P11_OPT_OUT_STILL_LOGGED")
        tokens=line[len(P11):].split()
        vals={}
        for token in tokens:
            if "=" not in token:raise ValueError("P11_MALFORMED_NATIVE_SOURCE_SCALAR")
            key,val=token.split("=",1)
            if key in vals:raise ValueError("P11_DUPLICATED_SCALAR")
            vals[key]=val
        kind=vals.get("kind")
        if kind=="CLASS_CENSORED":
            if set(vals)!={"kind","class","cap","serial"} or vals["class"] not in ("CUTOFF","SEE","ROOT") or vals["cap"]!="24":
                raise ValueError("P11_CLASS_CENSOR_MARKER_INVALID")
            caps[vals["class"]]+=1
            continue
        if kind not in CLASSES:raise ValueError("P11_EVENT_UNKNOWN_OR_UNSCOPED")
        if set(vals)!={"kind","serial","ply","depth","value","alpha","beta",
                     "result","move_code","score_writer","score_writer_exact"}:
            raise ValueError("P11_NATIVE_CLASS_FIELDS_NOT_COMPLETE")
        item={k:int(v) if k!="kind" else v for k,v in vals.items()}
        if source and item["serial"]<=source[-1]["serial"]:
            raise ValueError("P11_GLOBAL_CLOCK_NOT_MONOTONE")
        if item["score_writer_exact"] not in (0,1) or item["result"] not in (0,1):
            raise ValueError("P11_NATIVE_BOOLEAN_NOT_ACTUAL")
        if kind in ("TT_MAIN_RETURN","TT_Q_RETURN") and item["result"]!=1:
            raise ValueError("P11_NOT_AN_ACTUAL_RETURN")
        if kind=="ROOT_SCORE_UPDATE" and item["result"]!=1:
            raise ValueError("P11_NOT_AN_ACTUAL_RM_SCORE_UPDATE")
        source.append(item)
        by_class[CLASSES[kind]]+=1
    if len(root)!=int(enabled):
        raise ValueError("P11_NATIVE_FINAL_ROOT_OBSERVED_NOT_ONCE_IF_ENABLED")
    if any(v>24 for v in by_class.values()) or any(v>1 for v in caps.values()):
        raise ValueError("P11_CLASS_QUOTA_OR_CENSOR_INVALID")
    endpoint=None
    if root:
        vals={}
        for item in root[0][len(P9):].split():
            key,value=item.split("=",1);vals[key]=value
        if set(vals)!={"kind","UCI","root_score","completed_depth","root_candidate_count"} or vals["kind"]!="FINAL_CANDIDATE":
            raise ValueError("P11_ROOT_FINAL_NATIVE_ENDPOINT_INVALID")
        if vals["UCI"]!=best[0] or int(vals["completed_depth"])!=7:
            raise ValueError("P11_ROOT_CANDIDATE_AND_TERMINAL_UCI_MISMATCH")
        endpoint={"bestmove":vals["UCI"],"score":int(vals["root_score"]),
                  "candidate_count":int(vals["root_candidate_count"]),"depth":7}
    return {"bestmove":best[0],"depth":7,"nodes":n,
            "source":source,"counts":dict(by_class),
            "censored_class_names":sorted(caps.keys()),
            "native_frame_events":frames,
            "native_final_root_endpoint":endpoint}
def audit(original,observed,manifest):
    if not manifest.get("P8_then_P11_then_P12_reverse_exact_original_source_byte_equal"):
        raise ValueError("P11_ORIGINAL_SOURCE_REVERSE_NOT_VERIFIED")
    a=[run(original,False) for _ in range(2)]
    b=[run(observed,True) for _ in range(2)]
    off=run(observed,False)
    if len({(q["bestmove"],q["depth"],q["nodes"]) for q in a+b+[off]})!=1:
        raise ValueError("P11_OBSERVER_CHANGES_BASELINE_NATIVE_UCI_OR_NODES")
    if b[0]!=b[1]:
        raise ValueError("P11_TWO_NATIVE_COLD_SOURCE_EVIDENCE_CHANGED")
    if any(q["source"] or q["native_final_root_endpoint"] for q in a+[off]):
        raise ValueError("P11_NOT_DISABLED_ON_NEGATIVE_CONTROL")
    x=b[0]
    actual_returns=[v for v in x["source"] if v["kind"] in
            ("TT_MAIN_RETURN","TT_Q_RETURN")]
    guarded=[v for v in x["source"] if v["kind"] in
            ("SEE_QUIET_GUARD","SEE_QSEARCH_GUARD")]
    roots=[v for v in x["source"] if v["kind"]=="ROOT_SCORE_UPDATE"]
    tags=x["native_frame_events"]
    native_source=[v for v in tags if v["kind"]=="SOURCE_EVENT"]
    native_exit=[v for v in tags if v["kind"]=="TT_RETURN_FRAME_EXIT"]
    event_by_serial={}
    for e in native_source:
        i=int(e["serial"])
        if i in event_by_serial:raise ValueError("P12_DUPLICATED_NATIVE_SOURCE_FRAME_SERIAL")
        event_by_serial[i]=e
        if not (int(e["call_id"])>0 and int(e["root_id"])>0):
            raise ValueError("P12_NO_ACTUAL_ROOT_CALL_ID_FOR_NATIVE_SOURCE_EVENT")
    if len(native_source)!=len(x["source"]):
        raise ValueError("P12_NATIVE_SOURCE_EVENT_WITHOUT_EXACT_FRAME_TAG")
    for e in x["source"]:
        f=event_by_serial.get(e["serial"])
        if f is None or f["source_kind"]!=e["kind"]:
            raise ValueError("P12_NATIVE_TT_SEE_ROOT_SOURCE_FRAME_MISMATCH")
    seen={}
    for e in native_exit:
        frame=int(e["call_id"]);parent=int(e["parent_id"])
        if frame in seen or frame<=0 or parent<=0 or parent>=frame or int(e["root_id"])<=0:
            raise ValueError("P12_NATIVE_PARENT_CHILD_CALL_ID_NOT_WELLFORMED")
        seen[frame]=e
    original_returns={(int(event_by_serial[e["serial"]]["call_id"]),e["value"]) for e in actual_returns}
    exits={(int(e["call_id"]),int(e["value"])) for e in native_exit}
    if original_returns!=exits:
        raise ValueError("P12_SOURCE_TT_RETURN_DOES_NOT_MATCH_ACTUAL_NATIVE_FRAME_UNWIND")
    if len(original_returns)!=len(actual_returns):
        raise ValueError("P12_SOURCE_NATIVE_TT_RETURN_DID_NOT_HAPPEN_IN_UNIQUE_FRAME")
    if not actual_returns:
        tt_status="NO_ACTUAL_TT_RETURN_WITNESSED_IN_THIS_ORIGINAL_DEPTH7"
    else:
        tt_status="ACTUAL_NATIVE_TT_RETURN_SOURCE_WITNESSED"
    if not guarded:see_status="NO_ACTUAL_SEE_GUARD_WITNESSED_IN_THIS_ORIGINAL_DEPTH7"
    else:see_status="ACTUAL_NATIVE_SEE_GUARD_EXECUTION_WITNESSED"
    if not roots:root_status="NO_NATIVE_ROOT_SCORE_UPDATE_WITNESSED_WITHIN_QUOTA"
    else:root_status="ACTUAL_NATIVE_ROOT_CANDIDATE_SCORE_UPDATE_WITNESSED"
    return {
      "schema":SCHEMA,
      "original_pinned_SF16_git_commit":"68e1e9b3811e16cad014b590d7443b9063b3eb52",
      "original_tt_cpp_sha256":manifest["original_upstream_SHA256"]["tt.cpp"],
      "original_search_cpp_sha256":manifest["original_upstream_source_SHA256"]["search.cpp"],
      "native_observer_two_layers_reverse_original_bytes":True,
      "two_native_original_and_observer_cold_repeats_each_plus_optout_control":True,
      "source_original_and_observer_same_UCI_depth_nodes":True,
      "source_position":"STANDARD_PUBLIC_STARTPOS",
      "original_final_UCI":x["bestmove"],"original_depth":7,
      "original_search_nodes":x["nodes"],
      "actual_TT_return_source_status":tt_status,
      "actual_SEE_guard_source_status":see_status,
      "actual_root_score_update_source_status":root_status,
      "class_bounded_native_events":x["counts"],
      "classes_censored_beyond_24_native_events":x["censored_class_names"],
      "native_source_events_with_actual_search_call_id":len(native_source),
      "actual_TT_return_frame_exit_parent_edges":len(native_exit),
      "original_TT_return_native_parent_call_certificate":
          "TT_RETURN_TO_ACTUAL_DIRECT_PARENT_CALLER_FRAME_CERTIFIED" if native_exit
          else "HOLD_NO_TT_RETURN_FRAME_WITNESS",
      "native_parent_received_and_used_TT_return_score_proven":False,
      "source_only_parent_child_unwind_is_not_SEE_mediation":True,
      "actual_TT_return_events_total_logged":len(actual_returns),
      "actual_TT_return_with_full64_original_score_field_writer_present":sum(
           bool(v["score_writer"] and v["score_writer_exact"]) for v in actual_returns),
      "actual_SEE_guard_events_total_logged":len(guarded),
      "actual_SEE_source_guards_pruned_via_continue":sum(not v["result"] for v in guarded),
      "actual_root_candidate_score_updates_total_logged":len(roots),
      "actual_selected_final_root_endpoint":x["native_final_root_endpoint"],
      "TT_returns_first24_evidence":[{"kind":v["kind"],"native_serial":v["serial"],
              "ply":v["ply"],"value":v["value"],"score_writer_serial":v["score_writer"],
              "original_full64_writer_match":bool(v["score_writer_exact"])} for v in actual_returns],
      "SEE_first24_evidence":[{"kind":v["kind"],"native_serial":v["serial"],
          "ply":v["ply"],"guard_returned":bool(v["result"]),
          "executed_continue":not bool(v["result"])} for v in guarded],
      "root_update_first24_evidence":[{"native_serial":v["serial"],
           "source_score":v["value"],"depth":v["depth"]} for v in roots],
      "in_process_source_clock_shared_by_event_classes":True,
      "source_clock_equal_to_unique_search_parent_identifier":False,
      "P11_natural_TT_to_SEE_to_root_mediation_certificate":
          "HOLD_NO_VERIFIED_CHILD_VALUE_ASSIGNMENT_OR_SEE_MEDIATION_TO_ROOT",
      "reason_for_HOLD":["TT returned score is not uniquely identified as ancestor of any observed SEE guard",
           "SEE guard and root score update have no matching native child-return/parent score-update edge",
           "Source-level event serials enforce temporal order but not causal ancestry",
           "Observed classes may be censored after 24 events each"],
      "TT_policy_optimized_Elo_speed_benefit_measured":False,
      "new_M5_unseen_forecast_executed":False,
      "rights":"GPLv3 original SF16 sources pinned; only derived original public chess startpos event scalar; no modified native binary or code uploaded."
    }
def main():
    p=argparse.ArgumentParser()
    for k in ("original","observer","manifest","out"):p.add_argument("--"+k,required=True)
    a=p.parse_args()
    d=audit(a.original,a.observer,json.loads(Path(a.manifest).read_text()))
    f=Path(a.out);f.parent.mkdir(parents=True,exist_ok=True)
    f.write_text(json.dumps(d,indent=2,sort_keys=True)+"\n")
    print("C3X025_P12_ACTUAL_RECURSIVE_FRAME_SOURCE_EDGES",
          {k:d[k] for k in ("original_final_UCI","original_search_nodes",
           "actual_TT_return_events_total_logged",
           "actual_TT_return_frame_exit_parent_edges",
           "original_TT_return_native_parent_call_certificate",
           "actual_TT_return_with_full64_original_score_field_writer_present",
           "actual_SEE_guard_events_total_logged",
           "actual_SEE_source_guards_pruned_via_continue",
           "actual_root_candidate_score_updates_total_logged",
           "classes_censored_beyond_24_native_events",
           "P11_natural_TT_to_SEE_to_root_mediation_certificate")},flush=True)
    print("C3X025_P12_NATIVE_JSON_SHA256",
          hashlib.sha256(f.read_bytes()).hexdigest(),flush=True)
if __name__=="__main__":main()

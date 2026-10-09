#!/usr/bin/env python3
"""Preregistered January 2026 16-game cross-window TT writer/reader pair court.

Source passive selection is deterministic before V interventions, and no exact
historical root call IDs, keys, chess moves, or scores are hard-coded.
"""
import argparse,hashlib,json
from pathlib import Path
from c3x_018_native_TT_lineage_factorial_6_8 import play,need
from c3x_018_independent16_TT_value_transport_native import (
    canonical_engine_world,verified_reader_lineage)
from c3x_018_chess_clock_factorial_original_history_native import game_clocks

SOURCE_SHA="5b49818e4678c12d0e5e73eba39eff2d50742b070a0ed870cba1d3e94afe0533"
ARCHIVE_SHA="9abf10d106a8bf5ecd41359825b3bf55c2f124c8a790a380cb98844c2cca5dca"
MAX_DISCOVERY=2048
VERSIONS=("STRICT","BROAD")
RULES={"STRICT":{"min_age":64,"max_ply":1,"exact_ply":1,"max_window":2},
       "BROAD":{"min_age":32,"max_ply":2,"exact_ply":None,"max_window":16}}
DECOY={"key64":18446744073709551615,"slot":0,"epoch":1}

def signed_width(e):
    return e["beta"]-e["alpha"]

def valid_source_event(e,rule):
    if e["kind"]!="discovery":return False
    if not (e["known"]==e["matched"]==1 and e["writer_serial"]>0
            and e["key64"]==e["writer_key64"] and e["epoch"]>0
            and 0<=e["slot"]<3 and e["raw_bound"]==2):
        return False
    if e["current_write_serial"]<e["writer_serial"]:return False
    if e["writer_age_writes"]!=e["current_write_serial"]-e["writer_serial"]:return False
    if e["writer_age_writes"]<rule["min_age"]:return False
    if not (1<=e["ply"]<=rule["max_ply"]):return False
    if rule["exact_ply"] is not None and e["ply"]!=rule["exact_ply"]:return False
    if not (1<=signed_width(e)<=rule["max_window"]):return False
    if not (e["reader_root_call"]>0 and e["reader_root_move"]!=0):return False
    return True

def same_physical_writer(a,b):
    return all(a[k]==b[k] for k in (
        "key64","slot","epoch","writer_serial","reader_root_move",
        "raw_value","raw_depth","raw_bound","raw_eval","raw_move"))

def first_pair(events,rule):
    # Streaming minimum of (second index, first index), not outcome-based.
    prior={}
    for j,e in enumerate(events):
        if not valid_source_event(e,rule):continue
        carrier=tuple(e[k] for k in (
            "key64","slot","epoch","writer_serial","reader_root_move",
            "raw_value","raw_depth","raw_bound","raw_eval","raw_move"))
        ancestors=prior.get(carrier,[])
        earlier=next(((i,r) for i,r in ancestors
                      if r["reader_root_call"]!=e["reader_root_call"]
                      and same_physical_writer(e,r)),None)
        if earlier is not None:
            i,r=earlier
            return {"indices":[i,j],
                    "readers":[r,e],
                    "physical":{"key64":e["key64"],"slot":e["slot"],"epoch":e["epoch"]},
                    "root_calls":[r["reader_root_call"],e["reader_root_call"]],
                    "root_candidate_native":e["reader_root_move"],
                    "bound_raw":2,"oldest_first":True}
        ancestors.append((j,e));prior[carrier]=ancestors
    return None

def root_episode(events,reader):
    root_call=reader["reader_root_call"]
    move=reader["reader_root_move"]
    episode=[e for e in events if e.get("root_call")==root_call]
    enter=next((e for e in episode if e["kind"]=="window_enter"),None)
    after=next((e for e in episode if e["kind"]=="after_sort"),None)
    candidate=[e for e in episode if e["kind"]=="candidate" and e["move"]==move]
    return {"root_call":root_call,"native_candidate":move,
            "enter":enter,"after_sort":after,
            "candidate_events":candidate,
            "root_trace_censored":len(events)>=4096}

def mask_filters(rule,pair,kind):
    a,b=pair["root_calls"]
    active={"FIRST":(a,0),"SECOND":(b,0),"BOTH":(a,b),"ZERO":(0,0)}
    ra,rb=active[kind]
    filters={"C3X018_FILTER_MIN_WRITE_AGE":rule["min_age"],
             "C3X018_FILTER_ROOT_MOVE":pair["root_candidate_native"],
             "C3X018_FILTER_RAW_BOUND":2,
             "C3X018_FILTER_WINDOW_WIDTH_MAX":rule["max_window"],
             "C3X018_FILTER_PAIR_CALL_A":ra,
             "C3X018_FILTER_PAIR_CALL_B":rb}
    if rule["exact_ply"] is not None:filters["C3X018_FILTER_PLY"]=rule["exact_ply"]
    else:filters["C3X018_FILTER_MAX_PLY"]=rule["max_ply"]
    return filters

def verify_selected_blocks(x,pair,rule,kind):
    contacts=[e for e in x["blocks"] if e["kind"]=="reader_block"]
    witnesses=[e for e in x["payload_witnesses"] if e["kind"]=="reader"]
    need(len(contacts)==x["lineage_summary"]["reader_block"],
         "SOURCE_LINEAGE_BLOCK_COUNT")
    target=pair["physical"]
    allowed={"FIRST":{pair["root_calls"][0]},
             "SECOND":{pair["root_calls"][1]},
             "BOTH":set(pair["root_calls"]),"ZERO":set()}[kind]
    need(all(e["root_call"] in allowed
             and all(e[k]==target[k] for k in ("key64","slot","epoch"))
             for e in contacts),"SOURCE_PAIR_ROOT_CALL_OR_PHYSICAL_MISMATCH")
    # A physical TT triple may be read WITHOUT the event-specific V guard firing.
    # c3x018_value_witness kind=reader is a pre-gate value snapshot, while
    # c3x018_lineage kind=reader_block is an actual intervention.
    # Match source block events to snapshots one-to-one, never validate *all*
    # physical snapshot reads as if they had been suppressed.
    def block_identity(evt):
        return (evt["key64"],evt["slot"],evt["epoch"],
                evt["root_call"],evt["root_move"],evt["ply"],
                evt["depth"],evt["alpha"],evt["beta"],evt["value"])
    def witness_identity(evt):
        return (evt["key64"],evt["slot"],evt["epoch"],
                evt["reader_root_call"],evt["reader_root_move"],evt["ply"],
                evt["depth"],evt["alpha"],evt["beta"],evt["effective_value"])
    available={}
    for witness in witnesses:
        available.setdefault(witness_identity(witness),[]).append(witness)
    matched=[]
    for blocked in contacts:
        choices=available.get(block_identity(blocked),[])
        need(bool(choices),"ACTUAL_BLOCK_WITHOUT_CORRESPONDING_PRE_GATE_VALUE_SNAPSHOT")
        matched.append(choices.pop(0))
    for w in matched:
        need(w["reader_root_call"] in allowed
             and w["reader_root_move"]==pair["root_candidate_native"]
             and w["raw_bound"]==2
             and w["writer_age_writes"]>=rule["min_age"]
             and (rule["exact_ply"] is None or w["ply"]==rule["exact_ply"])
             and 1<=w["ply"]<=rule["max_ply"]
             and 1<=w["beta"]-w["alpha"]<=rule["max_window"]
             and w["known"]==w["matched"]==1
             and w["key64"]==w["writer_key64"]
             and all(w[k]==target[k] for k in ("key64","slot","epoch")),
             "ACTUALLY_BLOCKED_READER_PROPERTY_CONGRUENCE")
    proof=verified_reader_lineage(x)
    need(not contacts or (proof["all_valid"] is True and proof["count"]>=len(contacts)),
         "LAST_PHYSICAL_WRITER_RAW_PAYLOAD")
    return {"blocked":len(contacts),"source_block_events":contacts,
            "physical_reader_payloads":witnesses,
            "matched_actually_blocked_payloads":matched,
            "physically_targeted_but_not_blocked_reads":len(witnesses)-len(matched),
            "writer_integrity":proof}

def main():
    p=argparse.ArgumentParser()
    for k in ("source","engine","out"):p.add_argument("--"+k,required=True)
    a=p.parse_args()
    b=Path(a.source).read_bytes()
    need(hashlib.sha256(b).hexdigest()==SOURCE_SHA,"JANUARY_BLIND_SOURCE_SHA")
    cohort=json.loads(b)
    need(cohort["compressed_source_sha256"]==ARCHIVE_SHA,"JANUARY_ARCHIVE_SHA")
    need(len(cohort["selected"])==16,"JANUARY_PRECOMMITTED_DENOMINATOR")
    result={"schema":"c3x018-Jan2026-independent16-cross-window-TT-pair-transport-v1",
         "protocol":"c3x/ontology/c3x-018-january2026-blind16-cross-window-TT-pair-transfer-preregistration.md",
         "source_manifest_sha256":SOURCE_SHA,"source_archive_sha256":ARCHIVE_SHA,
         "census_cap":MAX_DISCOVERY,"rules":RULES,"cases":[]}
    for original in cohort["selected"]:
        w,normal=canonical_engine_world(original)
        clocks=game_clocks(original)
        case={"id":original["id"],"source_game_sha256":original["source_game_sha256"],
              "native_original_played":w["native_move"],
              "clock":list(clocks),"normalization":normal,
              "status":"NOT_STARTED",
              "selectors":{r:{"status":"NOT_RUN"} for r in VERSIONS}}
        try:
            controls={}
            for mode in ("O","F","Z"):
                x=play(a.engine,w,mode,"OBS",fen_clocks=clocks)
                y=play(a.engine,w,mode,"OBS",fen_clocks=clocks)
                need(x==y,"BASELINE_COLD_"+mode)
                need(x["root_contact"]["target_contact"]==
                     ("0" if mode=="Z" else "1"),"P4_NO_CONTACT_"+mode)
                controls[mode]=x["UCI"]
            need(controls["O"]==controls["Z"],"O_Z_ROOT_SHAM_DRIFT")
            source=play(a.engine,w,"F","OBS",discovery=True,fen_clocks=clocks)
            again=play(a.engine,w,"F","OBS",discovery=True,fen_clocks=clocks)
            need(source==again,"SOURCE_PASSIVE_COLD_NONDETERMINISTIC")
            need(source["UCI"]==controls["F"],"SOURCE_PASSIVE_NONINTERFERENCE")
            decoy=play(a.engine,w,"F","V",DECOY,fen_clocks=clocks)
            need(decoy["UCI"]==controls["F"] and decoy["lineage_summary"]["reader_block"]==0,
                 "NO_CONTACT_DECOY_DRIFT")
            events=[e for e in source["payload_witnesses"] if e["kind"]=="discovery"]
            need(len(events)<=MAX_DISCOVERY,"SOURCE_DISCOVERY_OVER_CAP")
            case.update(status="VALID",controls=controls,
                passive_reader_events=events,
                reader_census_count=len(events),
                reader_census_censored=len(events)==MAX_DISCOVERY,
                root_search_events=source["root_events"],
                root_trace_censored=len(source["root_events"])>=4096,
                no_contact_sham_pass=True)
            for label in VERSIONS:
                rule=RULES[label]
                selected=first_pair(events,rule)
                row={"selector":label,"status":"NO_ELIGIBLE_PAIR",
                     "first_2048_source_census_censored":len(events)==MAX_DISCOVERY}
                if selected is not None:
                    row={"selector":label,"status":"SOURCE_PAIR_ELIGIBLE",
                         "selected_passive_pair":selected,
                         "source_root_episodes":[root_episode(source["root_events"],e) for e in selected["readers"]],
                         "arms":{}}
                    for kind in ("FIRST","SECOND","BOTH","ZERO"):
                        flags=mask_filters(rule,selected,kind)
                        x=play(a.engine,w,"F","V",selected["physical"],
                               fen_clocks=clocks,tt_reader_filters=flags)
                        y=play(a.engine,w,"F","V",selected["physical"],
                               fen_clocks=clocks,tt_reader_filters=flags)
                        need(x==y,"SOURCE_COLD_V_"+label+"_"+kind)
                        v=verify_selected_blocks(x,selected,rule,kind)
                        if kind=="ZERO":
                            need(v["blocked"]==0 and x["UCI"]==controls["F"],
                                 "ZERO_PAIR_CALL_SHAM_DRIFT")
                        v.update(UCI=x["UCI"],
                            bestmove_changed=x["UCI"]["bestmove"]!=controls["F"]["bestmove"],
                            full_core_changed=x["UCI"]!=controls["F"],
                            source_root_events=x["root_events"])
                        row["arms"][kind]=v
                    first=row["arms"]["FIRST"]["blocked"]>0
                    second=row["arms"]["SECOND"]["blocked"]>0
                    bothblocks={e["root_call"] for e in row["arms"]["BOTH"]["source_block_events"]}
                    row["single_source_reached"]={"FIRST":first,"SECOND":second}
                    row["both_source_calls_realized"]=set(selected["root_calls"]).issubset(bothblocks)
                    row["status"]="PAIR_REALIZED" if row["both_source_calls_realized"] else "PAIR_NOT_REALIZED"
                    row["pair_root_flip"]=row["both_source_calls_realized"] and row["arms"]["BOTH"]["bestmove_changed"]
                    row["minimal_pair_like"]=row["pair_root_flip"] and first and second and (
                        not row["arms"]["FIRST"]["bestmove_changed"] and
                        not row["arms"]["SECOND"]["bestmove_changed"])
                case["selectors"][label]=row
        except (RuntimeError,ValueError,KeyError) as exc:
            case["status"]="HOLD_FAIL_CLOSED"
            case["failure"]=type(exc).__name__+":"+str(exc)[:350]
        result["cases"].append(case)
        print("C3X018_JANUARY_CROSS_WINDOW_PAIR",case["id"],case["status"],
              {k:(v["status"],v.get("pair_root_flip"),
                  v.get("minimal_pair_like")) for k,v in case["selectors"].items()},flush=True)
    need([x["id"] for x in result["cases"]]==list(range(1,17)),
         "SAMPLE_DENOMINATOR_16")
    good=[c for c in result["cases"] if c["status"]=="VALID"]
    def rows(role):
        return [c["selectors"][role] for c in good]
    strict=rows("STRICT");broad=rows("BROAD")
    realized=[r for c in good for r in c["selectors"].values()
              if r["status"]=="PAIR_REALIZED"]
    failed_congruence=0  # fail-closed in event source verifier
    summary={"games_total":16,"games_valid":len(good),"games_held":16-len(good),
         "source_reader_censored_cases":sum(c["reader_census_censored"] for c in good),
         "strict_eligible":sum(r["status"]!="NO_ELIGIBLE_PAIR" for r in strict),
         "strict_physically_realized":sum(r["status"]=="PAIR_REALIZED" for r in strict),
         "strict_pair_root_flips":sum(r.get("pair_root_flip",False) for r in strict),
         "strict_minimal_pair_like":sum(r.get("minimal_pair_like",False) for r in strict),
         "broad_eligible":sum(r["status"]!="NO_ELIGIBLE_PAIR" for r in broad),
         "broad_physically_realized":sum(r["status"]=="PAIR_REALIZED" for r in broad),
         "broad_pair_root_flips":sum(r.get("pair_root_flip",False) for r in broad),
         "claimed_unverified_payloads":failed_congruence,
         "J1_STRICT_ELIGIBILITY":"PASS" if any(r["status"]!="NO_ELIGIBLE_PAIR" for r in strict) else "FAIL",
         "J2_STRICT_GROUP_ROOT":"PASS" if any(r.get("pair_root_flip",False) for r in strict) else "FAIL",
         "J3_STRICT_MINIMAL_INTERACTION":"PASS" if any(r.get("minimal_pair_like",False) for r in strict) else "FAIL",
         "J4_BROAD_TRANSFER":"PASS" if any(r.get("pair_root_flip",False) for r in broad) else "FAIL",
         "J5_SOURCE_WRITER_EVENT_CONGRUENCE":"PASS",
         "J6_NEGATIVE_CONTROL":"PASS" if len(good)==16 else "HOLD",
         "J7_DENOMINATOR":"PASS" if len(result["cases"])==16 and all(len(c["selectors"])==2 for c in result["cases"]) else "FAIL",
         "J8_TEST_NONINTERFERENCE":"PASS" if len(good)==16 else "HOLD"}
    if len(good)!=16:
        for k in ("J1_STRICT_ELIGIBILITY","J2_STRICT_GROUP_ROOT",
                  "J3_STRICT_MINIMAL_INTERACTION","J4_BROAD_TRANSFER",
                  "J5_SOURCE_WRITER_EVENT_CONGRUENCE"):
            summary[k]="HOLD_INCOMPLETE_NATIVE_COURT"
    result["summary"]=summary
    result["limits"]=[
      "Census first 2048 passive TT V bound-qualified readers only, not complete search tree",
      "Two source selectors chosen before any counterfactual V results, broad and strict overlap possible",
      "Within-process root call IDs selected from features, but search trajectory changes can invalidate identity claims",
      "A pair intervention uses two source root-call guards not a simultaneous immutable two-edge intervention",
      "Search and bound score are internal evaluation units and do not directly prove chess motif explanations",
      "January source ecology independent of October-December; chess engine Stockfish16 not independent algorithm",
      "All J1-J4 failures retained, and no retargeting to success allowed"]
    out=Path(a.out);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("C3X018_JANUARY_PRECOMMITTED_TT_CROSS_WINDOW_FINAL",
          json.dumps(summary,sort_keys=True),flush=True)
    if len(good)!=16:raise RuntimeError("C3X018_JANUARY_NATIVE_FAIL_CLOSED")
if __name__=="__main__":main()

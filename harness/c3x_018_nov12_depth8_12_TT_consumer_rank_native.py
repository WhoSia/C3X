#!/usr/bin/env python3
"""Preregistered C3X018 November chess TT value-reader index 0,7,23 x depth8,12.

Does not select based on any intervention outcome. FULL 12 x 2 x 3 grid
including ineligible rank and no-fired sites. Source and old cohorts separate.
"""
import argparse,hashlib,json
from pathlib import Path
import chess
from c3x_018_native_TT_lineage_factorial_6_8 import play,need
from c3x_018_independent16_TT_value_transport_native import canonical_engine_world,verified_reader_lineage
from c3x_018_chess_clock_factorial_original_history_native import game_clocks
SOURCE_SHA="2971fe617f39fbba6d40fb0b09d8a18ce247d5865dc807fcdab9a594e3473402"
ARCHIVE_SHA="39deb43faf6e2f4569a76f369ca0a3b87aa7787330c9e2ff87705c6f3bf32ff1"
DEPTHS=(8,12)
RANKS=(0,7,23)
DECOY={"key64":18446744073709551615,"slot":0,"epoch":1}

def eligible(r):
    return [e for e in r["payload_witnesses"] if
        e["kind"]=="discovery" and e["known"]==1 and e["matched"]==1 and
        e["writer_serial"]>0 and e["epoch"]>0 and
        0<=e["slot"]<3 and e["key64"]==e["writer_key64"]]

def main():
    p=argparse.ArgumentParser()
    for k in ("source","engine","out"):p.add_argument("--"+k,required=True)
    a=p.parse_args()
    content=Path(a.source).read_bytes()
    need(hashlib.sha256(content).hexdigest()==SOURCE_SHA,"NEW_NOVEMBER_SOURCE_NOT_PINNED")
    data=json.loads(content)
    need(data["compressed_source_sha256"]==ARCHIVE_SHA,"NOVEMBER_ARCHIVE_SHA")
    need(len(data["selected"])==12,"TWELVE_FROZEN_SOURCES")
    output={"schema":"c3x018-nov2025-blind-12-two-depth-three-TT-consumer-ranks-v1",
      "preregistration":"c3x/ontology/c3x-018-independent-nov2025-depth8-12-TT-reader-rank-preregistration.md",
      "source_manifest_sha256":SOURCE_SHA,"source_archive_sha256":ARCHIVE_SHA,
      "depths":list(DEPTHS),"consumer_ranks_zero_index":list(RANKS),
      "cases":[]}
    for original in data["selected"]:
        world,normal=canonical_engine_world(original)
        half,full=game_clocks(original)
        row={"id":original["id"],"game_sha256":original["source_game_sha256"],
             "source":original["game_url"],
             "original_halfmove":half,"original_fullmove":full,
             "normalization":normal,"depths":[]}
        for depth in DEPTHS:
            cell={"depth":depth,"status":"NOT_STARTED",
                  "target_ranks":{}}
            try:
                controls={}
                for arm in ("O","F","Z"):
                    x=play(a.engine,world,arm,"OBS",fen_clocks=(half,full),search_depth=depth)
                    y=play(a.engine,world,arm,"OBS",fen_clocks=(half,full),search_depth=depth)
                    need(x==y,f"BASELINE_COLD_{row['id']}_{depth}_{arm}")
                    need(x["root_contact"]["target_contact"]==("0" if arm=="Z" else "1"),
                         f"ROOT_CONTACT_NEGATIVE_CONTROL_{row['id']}_{depth}_{arm}")
                    controls[arm]=x["UCI"]
                need(controls["O"]==controls["Z"],"OZ_NO_CONTACT_CORE_MISMATCH")
                discover=play(a.engine,world,"F","OBS",discovery=True,fen_clocks=(half,full),
                              search_depth=depth)
                verify=play(a.engine,world,"F","OBS",discovery=True,fen_clocks=(half,full),
                            search_depth=depth)
                need(discover==verify,"SOURCE_DISCOVERY_NONDETERMINISTIC")
                need(discover["UCI"]==controls["F"],"PASSIVE_DISCOVERY_CHANGED_CORE")
                candidates=eligible(discover)
                cell["controls"]=controls
                cell["candidates_found"]=len(candidates)
                for rank in RANKS:
                    name=str(rank)
                    rec={"rank_zero_index":rank,"status":"NOT_ELIGIBLE"}
                    if rank<len(candidates):
                        ev=candidates[rank]
                        target={k:ev[k] for k in ("key64","slot","epoch")}
                        rec.update(status="ELIGIBLE",target=target,
                                   passive_info={k:ev[k] for k in (
                                     "writer_serial","ply","depth","alpha","beta",
                                     "effective_value","raw_value","raw_bound","raw_depth",
                                     "site")})
                        a1=play(a.engine,world,"F","V",target,fen_clocks=(half,full),search_depth=depth)
                        a2=play(a.engine,world,"F","V",target,fen_clocks=(half,full),search_depth=depth)
                        need(a1==a2,f"COLD_V_{row['id']}_{depth}_{rank}")
                        witnessed=verified_reader_lineage(a1)
                        blocked=a1["lineage_summary"]["reader_block"]
                        rec.update(status="FIRED" if blocked>0 else "NOT_FIRED",
                          blocked_reads=blocked,writer_witness=witnessed,
                          final_UCI=a1["UCI"],
                          bestmove_changed=a1["UCI"]["bestmove"]!=controls["F"]["bestmove"],
                          full_core_changed=a1["UCI"]!=controls["F"])
                        if blocked:
                            need(witnessed["count"]>=blocked and witnessed["all_valid"] is True,
                                 "UNVERIFIED_WRITER_READER_PAYLOAD")
                    cell["target_ranks"][name]=rec
                # impossible target verifies physically no blocked read in current depth
                sham=play(a.engine,world,"F","V",DECOY,fen_clocks=(half,full),
                          search_depth=depth)
                need(sham["UCI"]==controls["F"] and sham["lineage_summary"]["reader_block"]==0,
                     "IMPOSSIBLE_KEY_NEGATIVE_CONTROL")
                cell["status"]="VALID"
            except (RuntimeError,ValueError,KeyError) as err:
                cell["status"]="HOLD_FAIL_CLOSED"
                cell["reason"]=type(err).__name__+":"+str(err)[:230]
            row["depths"].append(cell)
            print("C3X018_NOVEMBER_V_RANK",row["id"],depth,cell["status"],
                  {k:(v["status"],v.get("bestmove_changed")) for k,v in cell["target_ranks"].items()},
                  flush=True)
        output["cases"].append(row)
    need([x["id"] for x in output["cases"]]==list(range(1,13)),"DENOMINATOR")
    valid=[cell for c in output["cases"] for cell in c["depths"] if cell["status"]=="VALID"]
    cells=[cell for c in output["cases"] for cell in c["depths"]]
    def flips(rank,depth):
        return sum(cell["target_ranks"].get(str(rank),{}).get("bestmove_changed",False)
                   and cell["target_ranks"][str(rank)]["status"]=="FIRED"
                   for cell in valid if cell["depth"]==depth)
    late_any=any(flips(rank,12)>0 for rank in (7,23))
    depth_difference=False
    for row in output["cases"]:
        d8,d12=row["depths"]
        if d8["status"]==d12["status"]=="VALID":
            for rank in RANKS:
                a1=d8["target_ranks"][str(rank)]
                a2=d12["target_ranks"][str(rank)]
                if a1["status"]=="FIRED" and a2["status"]=="FIRED" and (
                    a1["bestmove_changed"]!=a2["bestmove_changed"]):
                    depth_difference=True
    all_realized=[r for cell in valid for r in cell["target_ranks"].values() if r["status"]=="FIRED"]
    failed=[r for r in all_realized if r["writer_witness"]["all_valid"] is not True]
    summary={"prespecified_worlds":12,"prespecified_depth_cells":24,
      "valid_cells":len(valid),"held_cells":24-len(valid),
      "rank0_depth12_root_flips":flips(0,12),
      "rank7_depth12_root_flips":flips(7,12),
      "rank23_depth12_root_flips":flips(23,12),
      "rank0_depth8_root_flips":flips(0,8),
      "rank7_depth8_root_flips":flips(7,8),
      "rank23_depth8_root_flips":flips(23,8),
      "realized_reader_interventions":len(all_realized),
      "unverified_physical_writer_payloads":len(failed),
      "T1_FIRST_ZERO":"PASS" if flips(0,12)<=2 else "FAIL",
      "T2_LATE_HAS_ROOT_EFFECT":"PASS" if late_any else "FAIL",
      "T3_DEPTH_MODULATION":"PASS" if depth_difference else "FAIL",
      "T4_PHYSICAL_WRITER_READ_INTEGRITY":("FAIL" if failed else "NOT_TESTED" if not all_realized else "PASS"),
      "T5_ROOT_SHAM":"PASS" if len(valid)==24 else "HOLD",
      "T6_FULL_DENOMINATOR":"PASS" if len(cells)==24 and all(len(q["target_ranks"])==3 for q in cells) else "FAIL"}
    if summary["held_cells"]:
        for k in ("T1_FIRST_ZERO","T2_LATE_HAS_ROOT_EFFECT","T3_DEPTH_MODULATION"):
            summary[k]="HOLD_NOT_ALL_CELLS_VALID"
    output["summary"]=summary
    output["limits"]=[
      "Actual future-game source cohort selected independent of engine results from a different PGN month",
      "Passive evaluation reader ranks are event order, not recursive tree depth or causal distance",
      "Using same rank across depths need not select same full key or same physical writer",
      "Per-source history retained but search uses canonical standalone FEN with ORIGINAL rule50/fullmove clocks",
      "A V reader that fires but does not change bestmove still changes one branch computation, not necessarily root",
      "No unique TT natural mediator; cross-engine validation separate"]
    dst=Path(a.out);dst.parent.mkdir(parents=True,exist_ok=True)
    dst.write_text(json.dumps(output,indent=2,sort_keys=True)+"\n")
    print("C3X018_NOVEMBER_TT_VALUE_RANK_NATIVE_FINAL",json.dumps(summary,sort_keys=True),flush=True)
    if summary["held_cells"]:raise RuntimeError("NATIVE_FROZEN_COURT_FAIL_CLOSED")
if __name__=="__main__":main()

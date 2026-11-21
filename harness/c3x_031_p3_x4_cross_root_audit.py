"""0.31/P3-X4: independent original-source 128+12-root counterexample audit.

Derived analysis ONLY. No new Stockfish search or model training.
Physical event-target/arm signatures, repeated sham/treated original UCI
and original JSON SHA-256 are independently checked and retained.
"""
import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from zipfile import ZipFile

P2_SHA="be66a985016b4ceaae1379c64ee0f6347c3a2e8c4fd3660ceb394227ac237df1"
X2_SHA="3c90be5bd0803937a6c9aaf8e55e6b15443c0a5c4f9a71605e13af28cc4da085"
P2_MEMBER="C3X_031_P2_B2_1669_NATIVE_PHYSICAL_RESULT.json"
X2_MEMBER="C3X_031_P3_X2_12_DEPTH_HORIZONS.json"


def require(value, detail):
    if not value:
        raise ValueError(detail)


def source_zip(path,member,expected_sha):
    with ZipFile(path) as archive:
        require(archive.testzip() is None,"original archive ZIP CRC invalid")
        require(archive.namelist().count(member)==1,"missing or duplicated source member")
        raw=archive.read(member)
    require(hashlib.sha256(raw).hexdigest()==expected_sha,
            "original research input JSON SHA mismatched")
    return json.loads(raw)


def classify(old,target,new):
    require(all(isinstance(x,str) and x for x in (old,target,new)),
            "missing signed source root name")
    if old==new:return "NO_FINAL_CHANGE"
    if old==target:return "TARGET_DISPLACED"
    if new==target:return "TARGET_PROMOTED"
    return "OFF_TARGET_SWITCH"


def original_p2(row):
    require(row["valid_primary"] and row["invalid_reason"] is None,
            "original physical source result invalid")
    a=row["arms"];t=row["original_target"]
    old=row["original_untreated_bestmove"]
    require(a["sham0"]==a["sham1"] and a["both_off0"]==a["both_off1"],
            "original source cold replay changed")
    require(a["sham0"]["bestmove"]==old and
            row["y"]==int(a["both_off0"]["bestmove"]!=old),
            "original source effect y no longer matches actual root")
    require(t==a["sham0"]["target_event"]["open"]==a["both_off0"]["target_event"]["open"],
            "original source OPEN event reselected")
    require(a["sham0"]["target_event"]["close"]["skip_f"]=="0"
            and a["sham0"]["target_event"]["close"]["skip_n"]=="0"
            and a["both_off0"]["target_event"]["close"]["skip_f"]=="1"
            and a["both_off0"]["target_event"]["close"]["skip_n"]=="1",
            "original physical intervention source mask changed")
    new=a["both_off0"]["bestmove"]
    return {"id":row["id"],"game":row["case_id"],"family":row["family"],
            "target_root":t["root"],"original_root":old,"new_root":new,
            "class":classify(old,t["root"],new)}


def original_x2(row,prior):
    require(row["valid"] and row["error"] is None,
            "original depth/node source cell invalid")
    require(row["original_target"]==prior["id"] and
            row["game_id"]==prior["case_id"] and
            row["family"]==prior["family"],
            "original exposed game/family joined incorrectly")
    arms=row["arms"]
    require(set(arms)=={"sham0","sham1","futility_only","both_off0","both_off1"},
            "actual native arm missing")
    require(arms["sham0"]==arms["sham1"] and
            arms["both_off0"]==arms["both_off1"],
            "depth horizon cold process replay differed")
    for name,arm in arms.items():
        ev=arm["genuine_source_event"]
        require(ev["open"]==prior["original_target"] and
                ev["close"]["stopped"]=="0",
                "horizon source event identity not physically contacted")
        expect_f=int(name not in ("sham0","sham1"))
        expect_n=int(name.startswith("both_off"))
        require(ev["close"]["skip_f"]==str(expect_f) and
                ev["close"]["skip_n"]==str(expect_n),
                "source gate arm not physically registered")
        require(arm["native_root_best"]["move"]==arm["native_uci"][-1].split()[1],
                "source root UCI mismatched output producer")
        require(arm["last_reported_uci_depth"]<=row["horizon_depth_cap"],
                "physical search exceeded requested depth cap")
    base=arms["sham0"];treated=arms["both_off0"]
    old=base["native_root_best"]["move"]
    new=treated["native_root_best"]["move"]
    require(row["same_depthcap_root_flip"]==int(old!=new),
            "original root switch verdict disagrees with UCI")
    target=prior["original_target"]["root"]
    return {"source_event":prior["id"],"game":prior["case_id"],
            "family":prior["family"],
            "target_root":target,"original_root":old,"new_root":new,
            "depth_cap":row["horizon_depth_cap"],
            "node_cap":row["horizon_node_cap"],
            "actual_original_depth":base["last_reported_uci_depth"],
            "actual_treated_depth":treated["last_reported_uci_depth"],
            "actual_original_nodes":base["last_reported_uci_nodes"],
            "actual_treated_nodes":treated["last_reported_uci_nodes"],
            "class":classify(old,target,new)}


def audit(p2,x2):
    old=p2["source_event_results"]
    require(p2["actual_native_intervention_processes"]==640 and len(old)==128
            and len({x["id"] for x in old})==128
            and len({x["case_id"] for x in old})==64
            and len({x["family"] for x in old})==25,
            "historical P2 physical 128 event/64 game/25 series denominator changed")
    prior={x["id"]:x for x in old}
    p2rows=[original_p2(x) for x in old]
    p2count=Counter(x["class"] for x in p2rows)
    require(p2count=={"NO_FINAL_CHANGE":114,"TARGET_DISPLACED":8,
                      "TARGET_PROMOTED":6},
            "P2 14 source-root flips and target alignment not reproduced")
    cells=x2["horizon_cells"]
    require(len(cells)==12 and x2["actual_new_native_searches"]==60
            and x2["physically_contacted_valid_cells"]==12,
            "original 12 depth horizon cells not complete")
    horizons=[original_x2(x,prior[x["original_target"]]) for x in cells]
    counts=Counter(x["class"] for x in horizons)
    require(counts=={"NO_FINAL_CHANGE":1,"TARGET_DISPLACED":7,
                     "TARGET_PROMOTED":2,"OFF_TARGET_SWITCH":2},
            "physical third-root spillover not reconstructed")
    off=[x for x in horizons if x["class"]=="OFF_TARGET_SWITCH"]
    require(len(off)==2 and {x["source_event"] for x in off}=={"P2-056-1"}
            and {x["node_cap"] for x in off}=={32000,64000}
            and {x["depth_cap"] for x in off}=={13}
            and {(x["target_root"],x["original_root"],x["new_root"])
                 for x in off}=={("h5e2","b8d8","f5h3")}
            and all(x["actual_original_depth"]==
                    x["actual_treated_depth"]==13 for x in off),
            "same-original-event third-root falsification not source-validated")
    return {
        "schema":"C3X_031_P3_X4_SOURCE_CROSS_ROOT_COUNTEREXAMPLE_COURT_V1",
        "scientific_status":"SOURCE_REANALYSIS_ONLY_NO_NEW_NATIVE_SEARCH",
        "original_P2_SHA256":P2_SHA,"original_X2_SHA256":X2_SHA,
        "original_P2_events":128,"original_P2_games":64,
        "original_P2_canonical_families":25,
        "original_X2_horizon_cells":12,
        "original_P2_root_classification":dict(sorted(p2count.items())),
        "original_X2_root_classification":dict(sorted(counts.items())),
        "off_target_source_unique_games":len({x["game"] for x in off}),
        "off_target_real_two_node_cap_reproductions":off,
        "new_stockfish_searches":0,
        "single_target_score_only_model_violated_in_observed_horizon":True,
        "TT_history_budget_mediator_identified":False,
        "chess_plan_value_established":False,
        "raw_P2_source_128_cases":p2rows,
        "raw_P3_depth_node_12_cells":horizons,
        "limitations":[
            "P3-X2 game selected after P2 outcome; this is not blind confirmation.",
            "Both off-target horizon cells originate from one game and one source event.",
            "Equal completed depth does not equal actual nodes or internal TT/history.",
            "A single isolated candidate score changing cannot swap two other winners under a fixed tie-break.",
            "The actual mediator may involve TT, history, root re-search, ordering or budget; unknown.",
            "No independent legal opponent replies or human learning evaluation has been performed."
        ],
    }


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("p2_original_zip",type=Path)
    ap.add_argument("x2_original_zip",type=Path)
    ap.add_argument("out",type=Path)
    args=ap.parse_args()
    result=audit(source_zip(args.p2_original_zip,P2_MEMBER,P2_SHA),
                 source_zip(args.x2_original_zip,X2_MEMBER,X2_SHA))
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print("P3_X4_SOURCE_LOCALITY_COURT",result["original_P2_root_classification"],
          result["original_X2_root_classification"],
          "single_source_unit",result["off_target_source_unique_games"],
          "out_sha",hashlib.sha256(args.out.read_bytes()).hexdigest())


if __name__=="__main__":
    main()

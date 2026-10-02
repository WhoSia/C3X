#!/usr/bin/env python3
from __future__ import annotations
import argparse,json
from collections import Counter,defaultdict
from pathlib import Path

def load(p): return json.loads(Path(p).read_text())

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--worlds",required=True)
    ap.add_argument("--p9-result",required=True)
    ap.add_argument("--p9-census",required=True)
    ap.add_argument("--out",required=True)
    a=ap.parse_args()

    worlds=[]
    for p in Path(a.worlds).rglob("*.json"):
        try:x=load(p)
        except Exception:continue
        if x.get("schema")=="c3x-g10-p10-opportunity-world-v1":worlds.append(x)

    p9=load(a.p9_result); census=load(a.p9_census)
    firewall=all(
      w.get("remove_set_runs")==0 and
      w.get("event_ablation_runs")==0 and
      w.get("edited_native_choice_recorded") is False and
      w.get("certificate_outcomes_consulted") is False
      for w in worlds
    )

    pos_positions=set()
    for z in p9["matched_pairs"]:
        if z["target_positive"]:pos_positions.add(z["target_position_id"])
        if z["control_positive"]:pos_positions.add(z["control_position_id"])
    pos_engines=[]
    for e,v in p9["engine_certificate_counts"].items():
        if v["TARGET"]+v["CONTROL"]>0:pos_engines.append(e)
    positive_cases=set()
    if p9["complete_local_certificate_count"]==1 and len(pos_positions)==1 and len(pos_engines)==1:
        positive_cases={(next(iter(pos_positions)),pos_engines[0])}

    active=[w for w in worlds if w.get("active")]
    classes=Counter(w.get("case_opportunity_class","NO_COMMON_BOUND") for w in active)
    positive_rows=[]
    joined=[]
    support=defaultdict(set)
    for w in active:
        ps=census["position_scores"].get(w["position_id"])
        if not ps:continue
        row={
          "source_id":w["source_id"],"engine":w["engine"],"position_id":w["position_id"],
          "opportunity_class":w["case_opportunity_class"],
          "max_common_target_bound_count":w["max_common_target_bound_count"],
          "max_target_specific_common_bound_delta":w["max_target_specific_common_bound_delta"],
          "family_distance":ps["family_distance"],
          "family_margin":ps["family_margin"],
          "family_specificity":ps["family_specificity"],
          "polarity_profile":ps["polarity_profile"],
          "development_certificate_positive":(w["position_id"],w["engine"]) in positive_cases,
        }
        joined.append(row)
        if row["development_certificate_positive"]:positive_rows.append(row)
        key=(row["source_id"],row["engine"],row["opportunity_class"],tuple(row["polarity_profile"]))
        support[key].add(row["family_distance"])

    contrast_cells=sum(len(ds)>=2 for ds in support.values())
    distinct_classes=len(classes)
    if not firewall: verdict="FAIL_OUTCOME_BLIND_FIREWALL"
    elif distinct_classes<2: verdict="DEVELOPMENT_OPPORTUNITY_SURFACE_DEGENERATE"
    else: verdict="DEVELOPMENT_OPPORTUNITY_SURFACE_NONTRIVIAL"

    out={
      "schema":"c3x-g10-p10-development-readout-v1",
      "status":"DEVELOPMENT_ONLY_NO_CONFIRMATORY_AUTHORITY",
      "verdict":verdict,
      "world_count":len(worlds),
      "active_world_count":len(active),
      "opportunity_class_counts":dict(sorted(classes.items())),
      "positive_case_count":len(positive_cases),
      "positive_case_rows":positive_rows,
      "opportunity_matched_cells_with_family_distance_variation":contrast_cells,
      "joined_rows":joined,
      "firewall_pass":firewall,
      "p9_outcomes_used_only_after_opportunity_definition_freeze":True,
      "confirmatory_authority":False,
    }
    Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("G10_P10_DEVELOPMENT",verdict)
    print("G10_P10_OPPORTUNITY_CLASSES",dict(sorted(classes.items())))
    print("G10_P10_POSITIVE_CASE",positive_rows)
    print("G10_P10_FAMILY_DISTANCE_CONTRAST_CELLS",contrast_cells)

if __name__=="__main__":main()

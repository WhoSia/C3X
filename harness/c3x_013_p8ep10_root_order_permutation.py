#!/usr/bin/env python3
"""P8 EP10: falsify ordinal-locator transport under UCI legal root list permutation.

This same CECLUB game was used for the original discovery; NOT new-source validation.
"""
import argparse, json
from pathlib import Path
import c3x_013_p8ep10_single_event_fixed_grid as ep10

ORDERS=(("f3f4","g3g4"),("g3g4","f3f4"))
TARGETS=(("MAIN",31),("MAIN",32),("MAIN",33),("QSEARCH",32))
DEPTHS=(8,12)

def analyze_in_order(binary,depth,order,site="NONE",ordinal=0,require_ep10=False):
    previous=ep10.PAIR
    try:
        ep10.PAIR=tuple(order)
        result=ep10.analyze(binary,depth,site,ordinal,require_ep10=require_ep10)
    finally:
        ep10.PAIR=previous
    gap=result["gap_white_cp"]
    result["f3f4_minus_g3g4_white_cp"]=gap if tuple(order)==ORDERS[0] else -gap if gap is not None else None
    return result

def semantic(x):
    return {k:x[k] for k in ("bestmove","f3f4_minus_g3g4_white_cp","ranks")}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--ep9",required=True);p.add_argument("--ep10",required=True);p.add_argument("--out",required=True)
    a=p.parse_args()
    rows=[]
    for order in ORDERS:
        for depth in DEPTHS:
            for repeat in (1,2):
                base=analyze_in_order(a.ep9,depth,order)
                sham=analyze_in_order(a.ep10,depth,order,require_ep10=True)
                sham_pass=semantic(base)==semantic(sham)
                sentinel=analyze_in_order(a.ep10,depth,order,"MAIN",1000000000,True)
                negative=semantic(sham)==semantic(sentinel) and sentinel["target"]["blocked"]==0
                actions={}
                if sham_pass and negative:
                    for site,ordinal in TARGETS:
                        actions[f"{site}:{ordinal}"]=analyze_in_order(a.ep10,depth,order,site,ordinal,True)
                rows.append({"order":list(order),"depth":depth,"cold_repeat":repeat,
                    "ep9_off":base,"ep10_none":sham,"sham_exact":sham_pass,
                    "negative_control":sentinel,"negative_exact":negative,"actions":actions})
                print("EP10_ORDER_FALSIFIER",order,depth,repeat,"sham",sham_pass,"negative",negative,
                      "main32",actions.get("MAIN:32",{}).get("bestmove"),flush=True)
    pass_all=all(x["sham_exact"] and x["negative_exact"] for x in rows)
    outcomes={}
    for depth in DEPTHS:
        for order in ORDERS:
            items=[r for r in rows if r["depth"]==depth and tuple(r["order"])==order]
            outcomes[f"{depth}:{order[0]}-first"]={
                "baseline":items[0]["ep10_none"]["bestmove"],
                "MAIN32":items[0]["actions"].get("MAIN:32",{}).get("bestmove"),
                "MAIN32_flip_repetitions":sum(
                    r["actions"].get("MAIN:32",{}).get("bestmove")!=r["ep10_none"]["bestmove"]
                    for r in items if "MAIN:32" in r["actions"]),
                "MAIN32_native_witness_tuples":[[
                    r["actions"]["MAIN:32"]["target"].get(k) for k in
                    ("actual_site","actual_ordinal","actual_ply","actual_depth",
                     "actual_alpha","actual_beta","actual_value")]
                    for r in items if "MAIN:32" in r["actions"]]}
    output={"schema":"c3x-013-p8ep10-root-order-permutation-falsifier-v1",
        "scientific_status":"POST_DISCOVERY_SAME_POSITION_TRANSPORT_STRESS_ONLY",
        "source_fresh":False,"independent_engine":False,
        "correct_CECLUB_FEN":ep10.FEN,"pair":list(ORDERS[0]),
        "orders":[list(x) for x in ORDERS],"depths":list(DEPTHS),"cold_repeats":2,
        "fixed_targets":[f"{s}:{n}" for s,n in TARGETS],
        "all_shams_and_sentinels_exact":pass_all,
        "outcomes":outcomes,"cells":rows,
        "event_ordinal_identity_not_proven_even_if_tuple_matches":True,
        "causal_chess_concept_certificate":False,"C3X_014":"UNOPENED_UNNAMED"}
    path=Path(a.out);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(output,indent=2)+"\n")
    print("EP10_ORDER_FALSIFIER_VERDICT",json.dumps({"gates_pass":pass_all,"outcomes":outcomes}),flush=True)
    if not pass_all:raise SystemExit("EP10_PERMUTATION_SHAM_OR_SENTINEL_HOLD")

if __name__=="__main__":main()

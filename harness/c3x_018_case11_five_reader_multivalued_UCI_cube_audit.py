#!/usr/bin/env python3
"""Full-source C3X018 case11 32-mask Boolean + five-valued UCI core certificate.

Exhaustive finite-cube analysis; no extrapolation to independent chess games.
"""
import argparse,hashlib,itertools,json,math
from collections import defaultdict
from pathlib import Path

RAW_SHA="1d2a66fd9d0cefe5ab5320b67caf98edce15f62bb394b50682c0bb5f2c485eed"
CALLS=(9,10,11,12,13)
def check(t,why):
    if not t:raise RuntimeError("C3X018_CUBE_"+why)
def subset(a,b):return (a&b)==a
def score(y,i):
    total=0
    for mask in range(32):
        if mask&(1<<i):continue
        if y[mask]!=y[mask|(1<<i)]:
            total+=1
    return total
def shapley(y,i):
    acc=0
    for mask in range(32):
        if mask&(1<<i):continue
        k=mask.bit_count()
        weight=math.factorial(k)*math.factorial(5-k-1)/math.factorial(5)
        acc+=weight*(int(y[mask|(1<<i)])-int(y[mask]))
    return round(acc,12)
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--native",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    raw=Path(a.native).read_bytes()
    check(hashlib.sha256(raw).hexdigest()==RAW_SHA,"PHYSICAL_RAW_SOURCE_SHA")
    j=json.loads(raw)
    q=j["masks"]
    check([r["mask"] for r in q]==list(range(32)),"POWERSET")
    y={r["mask"]:r["bestmove_changed"] for r in q}
    check(sum(y.values())==12,"TWELVE_FLIPS")
    minimal=[m for m in range(32) if y[m] and not any(
        subset(k,m) and k!=m and y[k] for k in range(32))]
    check(minimal==[20,24],"MINIMAL_PAIR_SOURCE_DRIFT")
    check(all(y[m]==bool((m&16) and (m&4 or m&8)) for m in range(32)),
          "EXACT_BOOLEAN_FORMULA_DRIFT")
    groups=defaultdict(list)
    for r in q:
        u=r["UCI"]
        key=json.dumps(u,sort_keys=True,separators=(",",":"))
        groups[key].append(r["mask"])
    check(len(groups)==5,"FIVE_SEARCH_CORE_EQUIVALENCE_CLASSES")
    classes=[{"masks":v,"exemplar_UCI":json.loads(k),
              "bestmove_changed":bool(y[v[0]])}
              for k,v in groups.items()]
    classes.sort(key=lambda x:x["masks"][0])
    check([x["masks"] for x in classes]==[
         list(range(0,16)),list(range(16,20)),list(range(20,24)),
         [24,25],[26,27,28,29,30,31]],"FULL_CORE_CLASSES_CHANGED")
    pivot={str(CALLS[i]):score(y,i) for i in range(5)}
    phi={str(CALLS[i]):shapley(y,i) for i in range(5)}
    check(pivot=={"9":0,"10":0,"11":4,"12":4,"13":12},"PIVOT_RECONSTRUCTION")
    report={"schema":"c3x018-case11-32-cold-intervention-five-UCI-equivalence-classes-and-Boolean-influence-v1",
      "native_source_sha256":RAW_SHA,
      "study_status":"ADAPTIVE_FINITE_SOURCE_NOT_CROSS_GAME_GENERALIZATION",
      "full_masks_verified":32,"minimal_root_flipping_calls":[[11,13],[12,13]],
      "exact_finite_Y":"Y=x13*(x11 OR x12)",
      "binary_mobius":"Y=x11*x13+x12*x13-x11*x12*x13",
      "core_equivalence_classes":classes,
      "pivotal_subsets_per_rootcall":pivot,
      "shapley_source_finite_cube":phi,
      "first_modulation_call13_only":{"mask":16,"bestmove_changed":False,
        "score_cp_before":classes[0]["exemplar_UCI"]["score_value"],
        "score_cp_after":classes[1]["exemplar_UCI"]["score_value"],
        "nodes_before":classes[0]["exemplar_UCI"]["nodes"],
        "nodes_after":classes[1]["exemplar_UCI"]["nodes"]},
      "UCI_core_class_sensitive_call10":True,
      "UCI_core_class_sensitive_call9":False,
      "limits":[
        "Shapley numbers refer to uniform distribution over these five synthetic intervention bits, not natural gameplay attribution",
        "The categorical root choice and full score/node/PV have DIFFERENT response partitions",
        "A source call can have no categorical effect but a computational effect in combination with other gate calls",
        "All source root-call identities are conditional and may shift after search trajectory changes",
        "No unique TT causal mediation or transferable chess concept proven"]}
    Path(a.out).parent.mkdir(parents=True,exist_ok=True)
    Path(a.out).write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print("C3X018_SOURCE_32_FINITE_CUBE_MATHEMATICAL_CERTIFICATE_PASS",
          json.dumps({"root_flips":12,"core_classes":5,"minimal":minimal,
                      "pivot":pivot,"shapley":phi},sort_keys=True))
if __name__=="__main__":main()

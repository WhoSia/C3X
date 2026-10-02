#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,math
from collections import Counter,defaultdict
from pathlib import Path

BOARDS=("B0","TARGET","SUBSET","SHAM")
BOUNDS=("UPPER","LOWER")
CLASS_ORD={"NO_COMMON_BOUND":0,"ONE_COMMON_BOUND":1,"TWO_COMMON_BOUNDS":2}

def load(p): return json.loads(Path(p).read_text())

def bit_signature(chain):
    bits=[]
    for b in BOARDS:
        avail=set(chain["board_topology"][b]["available_bounds"])
        for q in BOUNDS:
            bits.append(1 if q in avail else 0)
    return "".join(str(x) for x in bits)

def entropy(counts):
    n=sum(counts.values())
    if n==0:return 0.0
    return -sum((v/n)*math.log2(v/n) for v in counts.values() if v)

def mutual_info(rows):
    # descriptive MI between coarse opportunity class and integer family distance.
    joint=Counter((r["opportunity_class"],int(r["family_distance"])) for r in rows)
    a=Counter(r["opportunity_class"] for r in rows)
    b=Counter(int(r["family_distance"]) for r in rows)
    n=len(rows)
    if not n:return 0.0
    mi=0.0
    for (x,y),v in joint.items():
        p=v/n; px=a[x]/n; py=b[y]/n
        mi += p*math.log2(p/(px*py))
    return mi

def corr(xs,ys):
    n=len(xs)
    if n<2:return None
    mx=sum(xs)/n; my=sum(ys)/n
    vx=sum((x-mx)**2 for x in xs); vy=sum((y-my)**2 for y in ys)
    if vx==0 or vy==0:return None
    return sum((x-mx)*(y-my) for x,y in zip(xs,ys))/math.sqrt(vx*vy)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--worlds",required=True)
    ap.add_argument("--p9-census",required=True)
    ap.add_argument("--out",required=True)
    a=ap.parse_args()

    worlds=[]
    for p in Path(a.worlds).rglob("*.json"):
        try:x=load(p)
        except Exception:continue
        if x.get("schema")=="c3x-g10-p10-opportunity-world-v1":
            worlds.append(x)
    census=load(a.p9_census)

    active=[w for w in worlds if w.get("active")]
    case_rows=[]
    chain_sig_counts=Counter()
    case_sig_counts=Counter()
    by_engine_sig=defaultdict(Counter)
    by_source_sig=defaultdict(Counter)
    by_engine_class=defaultdict(Counter)
    by_source_class=defaultdict(Counter)

    for w in active:
        ps=census["position_scores"].get(w["position_id"])
        if not ps:continue
        chains=w.get("chains",[])
        sigs=[bit_signature(ch) for ch in chains]
        for sig in sigs:
            chain_sig_counts[sig]+=1
        canonical_sig=sigs[0] if sigs else "00000000"
        case_sig_counts[canonical_sig]+=1
        by_engine_sig[w["engine"]][canonical_sig]+=1
        by_source_sig[w["source_id"]][canonical_sig]+=1
        by_engine_class[w["engine"]][w["case_opportunity_class"]]+=1
        by_source_class[w["source_id"]][w["case_opportunity_class"]]+=1
        case_rows.append({
          "source_id":w["source_id"],"engine":w["engine"],"position_id":w["position_id"],
          "opportunity_class":w["case_opportunity_class"],
          "opportunity_ordinal":CLASS_ORD[w["case_opportunity_class"]],
          "canonical_signature":canonical_sig,
          "family_distance":int(ps["family_distance"]),
          "family_margin":int(ps["family_margin"]),
          "family_specificity":int(ps["family_specificity"]),
          "polarity_profile":ps["polarity_profile"],
        })

    # Cross-engine transport at the same position.
    bypos=defaultdict(list)
    for r in case_rows:bypos[r["position_id"]].append(r)
    multi={k:v for k,v in bypos.items() if len(v)>=2}
    class_unanimous=0; sig_unanimous=0; pair_agree=0; pair_total=0
    engine_pair=defaultdict(lambda:[0,0])
    for pid,rows in multi.items():
        if len({r["opportunity_class"] for r in rows})==1:class_unanimous+=1
        if len({r["canonical_signature"] for r in rows})==1:sig_unanimous+=1
        for i in range(len(rows)):
            for j in range(i+1,len(rows)):
                a0,b0=rows[i],rows[j]
                pair_total+=1
                same=a0["opportunity_class"]==b0["opportunity_class"]
                pair_agree+=int(same)
                key="|".join(sorted((a0["engine"],b0["engine"])))
                engine_pair[key][1]+=1;engine_pair[key][0]+=int(same)

    # Opportunity-matched geometry variation.
    cells=defaultdict(list)
    for r in case_rows:
        key=(r["source_id"],r["engine"],r["opportunity_class"],tuple(r["polarity_profile"]))
        cells[key].append(r)
    varying_cells=[]
    for key,rows in cells.items():
        ds=sorted({r["family_distance"] for r in rows})
        if len(ds)>=2:
            varying_cells.append({
              "source_id":key[0],"engine":key[1],"opportunity_class":key[2],
              "polarity_profile":list(key[3]),"n":len(rows),"family_distances":ds
            })

    fd=[r["family_distance"] for r in case_rows]
    oo=[r["opportunity_ordinal"] for r in case_rows]
    mi=mutual_info(case_rows)
    pear=corr(fd,oo)

    out={
      "schema":"c3x-g10-p10-opportunity-cartography-v1",
      "status":"DEVELOPMENT_ONLY_NO_CONFIRMATORY_AUTHORITY",
      "world_count":len(worlds),
      "active_world_count":len(active),
      "case_row_count":len(case_rows),
      "chain_signature_count":sum(chain_sig_counts.values()),
      "distinct_chain_signatures":len(chain_sig_counts),
      "distinct_case_signatures":len(case_sig_counts),
      "chain_signature_entropy_bits":entropy(chain_sig_counts),
      "case_signature_entropy_bits":entropy(case_sig_counts),
      "top_case_signatures":case_sig_counts.most_common(20),
      "top_chain_signatures":chain_sig_counts.most_common(20),
      "engine_class_counts":{k:dict(v) for k,v in sorted(by_engine_class.items())},
      "source_class_counts":{k:dict(v) for k,v in sorted(by_source_class.items())},
      "engine_signature_entropy_bits":{k:entropy(v) for k,v in sorted(by_engine_sig.items())},
      "source_signature_entropy_bits":{k:entropy(v) for k,v in sorted(by_source_sig.items())},
      "cross_engine_transport":{
        "positions_with_multiple_active_engines":len(multi),
        "class_unanimous_positions":class_unanimous,
        "class_unanimous_fraction":class_unanimous/len(multi) if multi else None,
        "signature_unanimous_positions":sig_unanimous,
        "signature_unanimous_fraction":sig_unanimous/len(multi) if multi else None,
        "pairwise_class_agreement":pair_agree/pair_total if pair_total else None,
        "engine_pair_class_agreement":{k:(v[0]/v[1] if v[1] else None) for k,v in sorted(engine_pair.items())}
      },
      "geometry_opportunity_factorization":{
        "mutual_information_bits_coarse_class_vs_family_distance":mi,
        "pearson_family_distance_vs_opportunity_ordinal":pear,
        "opportunity_matched_cells_with_family_distance_variation":len(varying_cells),
        "varying_cells":varying_cells,
        "deterministic_recoding_rejected":len(varying_cells)>0
      },
      "firewall":{
        "certificate_labels_used":False,
        "event_ablation_used":False,
        "remove_set_used":False,
        "post_outcome_threshold_tuning":False
      },
      "confirmatory_authority":False
    }
    Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("G10_P10_CARTOGRAPHY_PASS")
    print("SIGNATURES",out["distinct_case_signatures"],out["case_signature_entropy_bits"])
    print("TRANSPORT",out["cross_engine_transport"])
    print("FACTOR",out["geometry_opportunity_factorization"]["mutual_information_bits_coarse_class_vs_family_distance"],
          out["geometry_opportunity_factorization"]["pearson_family_distance_vs_opportunity_ordinal"],
          out["geometry_opportunity_factorization"]["opportunity_matched_cells_with_family_distance_variation"])

if __name__=="__main__":main()

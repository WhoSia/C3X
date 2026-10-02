#!/usr/bin/env python3
from __future__ import annotations
import argparse,itertools,json
from collections import Counter,defaultdict
from pathlib import Path

STATES=("00","01","10","11")
EDITS=("TARGET","SUBSET","SHAM")
PAIRS=(("berserk","ethereal"),("berserk","stockfish_19"),("ethereal","stockfish_19"))
MAPS={
 ("berserk","ethereal"):{s:s for s in STATES},
 ("berserk","stockfish_19"):{"00":"00","01":"10","10":"01","11":"11"},
 ("ethereal","stockfish_19"):{"00":"00","01":"10","10":"01","11":"11"},
}

def load(p): return json.loads(Path(p).read_text())

def collect(root):
    out=[]
    for p in Path(root).rglob("*.json"):
        try:x=load(p)
        except Exception:continue
        if x.get("schema")=="c3x-g10-p10-opportunity-world-v1" and x.get("active"):
            out.append(x)
    return out

def vec(ch,b):
    a=set(ch["board_topology"][b]["available_bounds"])
    return "".join("1" if q in a else "0" for q in ("UPPER","LOWER"))

def support_counts(worlds,source=None):
    out=defaultdict(lambda:defaultdict(Counter))
    for w in worlds:
        if source is not None and w["source_id"]!=source:continue
        for ch in w.get("chains",[]):
            x=vec(ch,"B0")
            for d in EDITS:
                out[w["engine"]][d][(x,vec(ch,d))]+=1
    return out

def transform_support(c,m):
    return {(m[x],m[y]) for (x,y),n in c.items() if n>0}

def support(c):
    return {e for e,n in c.items() if n>0}

def residual_atoms(c,e1,e2,m):
    atoms={"LEFT_ONLY_AFTER_ALIGNMENT":set(),"RIGHT_ONLY":set()}
    cores={}
    for d in EDITS:
        a=transform_support(c[e1][d],m); b=support(c[e2][d])
        cores[d]=sorted(a&b)
        for edge in a-b:atoms["LEFT_ONLY_AFTER_ALIGNMENT"].add((d,edge))
        for edge in b-a:atoms["RIGHT_ONLY"].add((d,edge))
    return atoms,cores

def edge_name(e): return f"{e[0]}>{e[1]}"

def maximal_rectangles(atomset):
    # Rows are edits; columns are directed edges. For each nonempty row subset,
    # take every edge whose cells are all 1. This maximal rectangle dominates
    # all smaller rectangles with the same row set.
    cand={}
    for r in range(1,1<<len(EDITS)):
        rows=tuple(EDITS[i] for i in range(len(EDITS)) if (r>>i)&1)
        edges=[]
        for x in STATES:
            for y in STATES:
                e=(x,y)
                if all((d,e) in atomset for d in rows):
                    edges.append(e)
        if not edges:continue
        covered=frozenset((d,e) for d in rows for e in edges)
        key=covered
        # keep the largest row signature metadata if duplicate covered set occurs
        if key not in cand:
            cand[key]={
              "edits":rows,
              "edges":tuple(edges),
              "covered":covered
            }
    return list(cand.values())

def minimum_rectangle_covers(atomset):
    if not atomset:
        return {"atomic_count":0,"candidate_rectangles":[],"minimum_basis_size":0,"minimum_covers":[[]],"essential_generators":[]}
    rects=maximal_rectangles(atomset)
    target=frozenset(atomset)
    sols=[]
    for k in range(1,len(rects)+1):
        for idxs in itertools.combinations(range(len(rects)),k):
            cov=frozenset().union(*(rects[i]["covered"] for i in idxs))
            if cov==target:
                sols.append(idxs)
        if sols:break
    if not sols:
        raise SystemExit("P12_NO_RECTANGLE_COVER")
    def sig(r):
        return {
          "edit_subset":list(r["edits"]),
          "edge_set":[edge_name(e) for e in r["edges"]],
          "covered_atom_count":len(r["covered"])
        }
    covers=[[sig(rects[i]) for i in s] for s in sols]
    sets=[{json.dumps(sig(rects[i]),sort_keys=True) for i in s} for s in sols]
    essential=set.intersection(*sets) if sets else set()
    return {
      "atomic_count":len(atomset),
      "candidate_rectangles":[sig(r) for r in rects],
      "minimum_basis_size":len(sols[0]),
      "minimum_cover_count":len(sols),
      "minimum_covers":covers,
      "essential_generators":[json.loads(x) for x in sorted(essential)],
      "compression_ratio":len(atomset)/len(sols[0]) if sols[0] else None
    }

def generator_atoms(g):
    edges=[]
    for s in g["edge_set"]:
        a,b=s.split(">")
        edges.append((a,b))
    return {(d,e) for d in g["edit_subset"] for e in edges}

def gen_signature(sign,g):
    return json.dumps({"sign":sign,"edits":g["edit_subset"],"edges":g["edge_set"]},sort_keys=True)

def analyze_scope(c,e1,e2,m):
    atoms,cores=residual_atoms(c,e1,e2,m)
    bysign={s:minimum_rectangle_covers(a) for s,a in atoms.items()}
    total_atoms=sum(len(v) for v in atoms.values())
    total_basis=sum(v["minimum_basis_size"] for v in bysign.values())
    return atoms,cores,{
      "shared_core_edge_count":sum(len(v) for v in cores.values()),
      "shared_core_by_edit":{d:[edge_name(e) for e in cores[d]] for d in EDITS},
      "residual_atom_count":total_atoms,
      "minimum_basis_size":total_basis,
      "overall_compression_ratio":total_atoms/total_basis if total_basis else None,
      "by_sign":bysign
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--worlds",required=True)
    ap.add_argument("--out",required=True)
    a=ap.parse_args()
    worlds=collect(a.worlds)
    sources=sorted({w["source_id"] for w in worlds})
    pooled=support_counts(worlds)

    result={}
    cross_pair=defaultdict(list)
    for e1,e2 in PAIRS:
        key=f"{e1}|{e2}";m=MAPS[(e1,e2)]
        patoms,cores,pana=analyze_scope(pooled,e1,e2,m)
        srcdata={}
        srcatoms={}
        for src in sources:
            c=support_counts(worlds,src)
            sa,sc,sana=analyze_scope(c,e1,e2,m)
            srcatoms[src]=sa
            srcdata[src]=sana

        stable_atoms={}
        for sign in ("LEFT_ONLY_AFTER_ALIGNMENT","RIGHT_ONLY"):
            stable=set.intersection(*(srcatoms[src][sign] for src in sources))
            stable_atoms[sign]=stable

        # generator stability across ALL minimum pooled covers:
        stable_generators=[]
        essential_stable=[]
        leave_one_out=[]
        all_min_gen_sigs=set()
        essential_sigs=set()
        for sign,ana in pana["by_sign"].items():
            for cover in ana["minimum_covers"]:
                for g in cover:
                    all_min_gen_sigs.add(gen_signature(sign,g))
            for g in ana["essential_generators"]:
                essential_sigs.add(gen_signature(sign,g))
                atoms_g=generator_atoms(g)
                isstable=atoms_g.issubset(stable_atoms[sign])
                if isstable:essential_stable.append({"sign":sign,**g})
                # omit essential generator from an arbitrary minimum cover containing it:
                # residual mass = atoms not covered by all remaining generators.
                cov_others=set()
                chosen=None
                for cover in ana["minimum_covers"]:
                    if any(gen_signature(sign,x)==gen_signature(sign,g) for x in cover):
                        chosen=cover;break
                if chosen is not None:
                    for x in chosen:
                        if gen_signature(sign,x)!=gen_signature(sign,g):
                            cov_others |= generator_atoms(x)
                    remaining=len(patoms[sign]-cov_others)
                    leave_one_out.append({"sign":sign,"generator":g,"remaining_residual_atoms":remaining})
            for cover in ana["minimum_covers"]:
                for g in cover:
                    if generator_atoms(g).issubset(stable_atoms[sign]):
                        stable_generators.append({"sign":sign,**g})

        # stable-only removal on each source using every pooled minimum-cover generator
        # that is source-stable.
        stable_unique={}
        for g in stable_generators:stable_unique[gen_signature(g["sign"],g)]=g
        stable_removal={}
        for src in sources:
            before=sum(len(srcatoms[src][s]) for s in srcatoms[src])
            covered=0;remaining=0
            for sign in srcatoms[src]:
                cov=set()
                for g in stable_unique.values():
                    if g["sign"]==sign:cov |= generator_atoms(g)
                covered += len(srcatoms[src][sign]&cov)
                remaining += len(srcatoms[src][sign]-cov)
            stable_removal[src]={
              "before":before,"covered_by_source_stable_pooled_generators":covered,
              "remaining":remaining,
              "fraction_removed":covered/before if before else None
            }

        recurrence={
          sign:{
            "pooled_atoms":len(patoms[sign]),
            "stable_atoms":len(stable_atoms[sign]),
            "stable_fraction":len(stable_atoms[sign])/len(patoms[sign]) if patoms[sign] else None,
            "stable_atom_list":[{"edit":d,"edge":edge_name(e)} for d,e in sorted(stable_atoms[sign])]
          } for sign in patoms
        }

        # cross-pair signatures only from essential pooled generators
        for sig in essential_sigs:cross_pair[sig].append(key)

        result[key]={
          "alignment_map":m,
          "pooled":pana,
          "source_specific":srcdata,
          "source_recurrence":recurrence,
          "source_stable_essential_generators":essential_stable,
          "stable_only_counterfactual_removal":stable_removal,
          "leave_one_essential_generator_out":leave_one_out
        }

    shared=[{"generator":json.loads(sig),"pairs":pairs} for sig,pairs in cross_pair.items() if len(pairs)>=2]

    # presealed verdict rule: strong only if every pair has >=2x compression and >=25% stable atoms overall.
    strong=True;pooled_sparse=True
    for k,v in result.items():
        cr=v["pooled"]["overall_compression_ratio"]
        if cr is None or cr<1.5:pooled_sparse=False
        pa=sum(x["pooled_atoms"] for x in v["source_recurrence"].values())
        sa=sum(x["stable_atoms"] for x in v["source_recurrence"].values())
        if cr is None or cr<2.0 or pa==0 or sa/pa<0.25:strong=False
    if strong:verdict="DEVELOPMENT_SOURCE_STABLE_SPARSE_DEFECT_BASIS"
    elif pooled_sparse:verdict="DEVELOPMENT_POOLED_SPARSE_SOURCE_FRAGILE_DEFECT_BASIS"
    else:verdict="DEVELOPMENT_PAIR_SPECIFIC_LOW_COMPRESSION_DEFECT_ECOLOGY"

    out={
      "schema":"c3x-g10-p12-obstruction-basis-v1",
      "status":"DEVELOPMENT_ONLY_NO_CONFIRMATORY_AUTHORITY",
      "verdict":verdict,
      "sources":sources,
      "engine_pairs":result,
      "cross_pair_essential_generator_recurrence":shared,
      "validity":{
        "p11_alignment_reselected":False,
        "rectangle_cover_exhaustive":True,
        "counterfactual_full_basis_exact_by_construction":True
      },
      "claim_ceiling":"DEVELOPMENT_DEFECT_FACTORIZATION_ONLY"
    }
    Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("G10_P12_BASIS_PASS",verdict)
    for k,v in result.items():
        print("PAIR",k,
              "ATOMS",v["pooled"]["residual_atom_count"],
              "BASIS",v["pooled"]["minimum_basis_size"],
              "CR",v["pooled"]["overall_compression_ratio"],
              "STABLE", {s:(x["stable_atoms"],x["pooled_atoms"]) for s,x in v["source_recurrence"].items()},
              "SRC_BASIS",{s:x["minimum_basis_size"] for s,x in v["source_specific"].items()})
    print("CROSS_PAIR_SHARED_ESSENTIAL",json.dumps(shared,sort_keys=True))
if __name__=="__main__":main()

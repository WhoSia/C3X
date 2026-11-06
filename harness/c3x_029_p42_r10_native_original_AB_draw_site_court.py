#!/usr/bin/env python3
"""P42/R10 original Game14 A/B node-parity draw site causal isolation.

One exact original Stockfish16 source binary, four modes 0/1/2/3, two cold
repeats per A/B. Evidence: source actually reached each site, physical TT
reader and unrestricted root result. Site intervention is global across all
encounters of that source caller; still NOT natural TT->SEE->root mediation.
"""
import argparse,json,os,re
from pathlib import Path
from c3x_029_p42_r9_original_AB_neutralized_source_probe import verify_original_inputs
from c3x_023_P1_R2_T0_chronological_post_TT_common_SEE_dev import cold
from c3x_018_independent16_TT_value_transport_native import verified_reader_lineage

LINE=re.compile(r"^c3x042_r10 site=([12]) ply=(\d+) mod4=([0-3]) original=(-?\d+) selected=([01]) result=(-?\d+)$",re.M)
def observed(raw,mode):
    lines=[x for x in raw.splitlines() if x.startswith("c3x042_r10 ")]
    found=LINE.findall(raw)
    if len(found)!=len(lines):
        raise ValueError("R10_HOLD_MALFORMED_NATIVE_CALLSITE_EVENT")
    sites={"1":{"calls":0,"selected":0},"2":{"calls":0,"selected":0}}
    for site,ply,mod4,original,selected,value in found:
        k,n,s,r=int(site),int(mod4),int(selected),int(value)
        native=int(original)
        expected = mode==3 or mode==k
        if s!=int(expected) or native!=-1+(n&2) or r!=(0 if expected else native):
            raise ValueError("R10_HOLD_NATIVE_SITE_VALUE_OR_SCOPE_MISMATCH")
        if int(ply)<0:
            raise ValueError("R10_HOLD_SOURCE_PLY_NEGATIVE")
        sites[site]["calls"]+=1
        sites[site]["selected"]+=s
    return sites

def verdict(root,sites,reader_valid):
    out={"status":"HOLD", "original_A":"b3a4","original_B":"f3f4",
         "root_moves":root,"source_site_counts":sites,
         "root_causation_proven":False,"specific_node_to_root_lineage_proven":False,
         "natural_guard_mediation_proven":False,
         "independent_chess_meaning_proven":False,"prospective_transport_proven":False}
    if not all(reader_valid):
        out["status"]="HOLD_PHYSICAL_TT_READER_PROOF"
        return out
    for mode in ("0","1","2","3"):
        if any(len(root[mode][x])!=2 for x in ("A","B")):
            out["status"]="HOLD_COLD_MISSING"
            return out
        if any(root[mode][x][0]!=root[mode][x][1] for x in ("A","B")):
            out["status"]="HOLD_SOURCE_ROOT_COLD_INSTABILITY"
            return out
    if root["0"]["A"]!=["b3a4"]*2 or root["0"]["B"]!=["f3f4"]*2:
        out["status"]="HOLD_ORIGINAL_GAME14_BASELINE_DRIFT"
        return out
    if root["3"]["A"]!=["b3a4"]*2 or root["3"]["B"]!=["b3a4"]*2:
        out["status"]="HOLD_R9_BROAD_INTERVENTION_NOT_REPRODUCED"
        return out
    # If the intervention changes root under mode 1 or 2, require physical
    # source contact at that selected site in both cold runs.
    causal={}
    for m in ("1","2"):
        moved=root[m]["B"][0]
        changed=moved!=root["0"]["B"][0]
        counts=sites[m]["B"]
        if changed and (len(counts)!=2 or any(x[m]["selected"]<=0 for x in counts)):
            out["status"]="HOLD_CHANGED_ROOT_WITHOUT_MATCHED_SOURCE_CONTACT"
            return out
        causal[m]={"B_root_changes":changed,"B_native_choice":moved,
                   "A_native_choice":root[m]["A"][0]}
    out["status"]="PASS_SOURCE_SITE_INTERVENTIONS_WITH_STABLE_HISTORICAL_CONTROLS"
    out["source_site_effects"]=causal
    out["claim"]="A causal effect of globally modifying calls at a known source site, if changed; not a proof of the unique ancestor path or of chess-semantic value."
    return out

def main():
    p=argparse.ArgumentParser()
    for key in ("source","stagea","forecast","engine","private","public-out"):
        p.add_argument("--"+key,required=True)
    a=p.parse_args()
    world,clock,physical,watch,filters=verify_original_inputs(a.source,a.stagea,a.forecast)
    private=Path(a.private);private.mkdir(parents=True,exist_ok=True)
    roots={m:{"A":[],"B":[]} for m in ("0","1","2","3")}
    sites={m:{"A":[],"B":[]} for m in ("0","1","2","3")}
    readers=[]
    for mode in ("0","1","2","3"):
        for rep in range(2):
            for arm in ("A","B"):
                path=private/(f"m{mode}_{arm}_cold{rep}_draw_sites.txt")
                path.write_text("")
                before=os.environ.copy()
                os.environ["C3X042_R10_DRAW_SITE_TRACE"]=str(path.resolve())
                os.environ["C3X042_R10_NEUTRAL_DRAW_SITE"]=mode
                os.environ.pop("C3X042_R9_DRAW_PARITY_NEUTRAL",None)
                os.environ.pop("C3X042_R8_DROP_DESCENDANT_TT_SAVE",None)
                try:
                    result=(cold(a.engine,world,clock,"O","OBS",watch=watch)
                            if arm=="A" else
                            cold(a.engine,world,clock,"O","V",physical,filter=filters,watch=watch))
                finally:
                    os.environ.clear();os.environ.update(before)
                roots[mode][arm].append(result["UCI"]["bestmove"])
                sites[mode][arm].append(observed(path.read_text(),int(mode)))
                if arm=="B":
                    readers.append(bool(verified_reader_lineage(result)["all_valid"])
                                   and any(x.get("kind")=="reader_block" for x in result["blocks"]))
    result=verdict(roots,sites,readers)
    output=Path(a.public_out)
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("C3X042_R10_SITE_SOURCE_ROOT_COURT",result["status"],
          {m:{a:root[0] for a,root in arms.items()} for m,arms in roots.items()},
          {m:{a:[v[m]["selected"] for v in seq] for a,seq in arms.items()}
           for m,arms in sites.items() if m in ("1","2")})
    if not result["status"].startswith("PASS_"):raise SystemExit(2)

if __name__=="__main__":
    main()
